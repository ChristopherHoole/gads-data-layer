"""
act_dashboard/routes/outreach.py

Outreach system blueprint — Chat 59.
Routes:
  GET  /outreach/leads                   — Leads page
  PATCH /outreach/leads/<lead_id>/notes  — Save notes (AJAX)
  POST  /outreach/leads/add              — Add new lead (AJAX)
  POST  /outreach/sync-from-sheets       — Sync new leads from Google Sheets (Chat 65)
"""

import imaplib
import json
import os
import uuid
from datetime import datetime, date, timedelta
from pathlib import Path

import duckdb
from flask import Blueprint, jsonify, render_template, request, session

from act_dashboard.auth import login_required
from act_dashboard.routes.shared import get_available_clients, get_current_config

bp = Blueprint("outreach", __name__, url_prefix="/outreach")

# ── path to warehouse.duckdb (writable) ──────────────────────────────────────
_WAREHOUSE_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "warehouse.duckdb")
)


def get_outreach_db():
    """Return a read-write connection to warehouse.duckdb for outreach tables."""
    return duckdb.connect(_WAREHOUSE_PATH)


# ── CV upload directory ───────────────────────────────────────────────────────
_CV_DIR = Path(__file__).parent.parent / "static" / "uploads" / "cv"


def _ensure_schema():
    """Create system_config table and add missing columns to outreach_emails if missing."""
    try:
        conn = get_outreach_db()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS system_config (
                key   VARCHAR PRIMARY KEY,
                value VARCHAR
            )
        """)
        try:
            conn.execute(
                "ALTER TABLE outreach_emails ADD COLUMN cv_attached BOOLEAN DEFAULT FALSE"
            )
        except Exception:
            pass  # Column already exists
        # Chat 72: add direction column for outbound vs outbound_reply tracking
        conn.execute(
            "ALTER TABLE outreach_emails ADD COLUMN IF NOT EXISTS direction VARCHAR DEFAULT 'outbound'"
        )
        conn.close()
    except Exception as e:
        print(f"[OUTREACH] Schema setup warning: {e}")


_ensure_schema()


# ── Context processor: nav badge counts for all templates ────────────────────
@bp.app_context_processor
def inject_outreach_badge_counts():
    """Provide queue + unread-reply counts to every template (for nav badges)."""
    try:
        conn = get_outreach_db()
        queue_count = conn.execute(
            "SELECT COUNT(*) FROM outreach_emails WHERE status = 'queued'"
        ).fetchone()[0]
        replies_count = conn.execute(
            "SELECT COUNT(*) FROM outreach_emails "
            "WHERE reply_received = true AND reply_read = false"
        ).fetchone()[0]
        conn.close()
        return {
            "outreach_queue_count":   queue_count,
            "outreach_replies_count": replies_count,
        }
    except Exception:
        return {"outreach_queue_count": 0, "outreach_replies_count": 0}


# ── Helpers ───────────────────────────────────────────────────────────────────
STATUS_DISPLAY = {
    "cold":            "Cold",
    "queued":          "Queued",
    "contacted":       "Contacted",
    "followed_up":     "Followed Up",
    "replied":         "Replied",
    "in_conversation": "In Conversation",
    "meeting":         "Meeting",
    "won":             "Won",
    "lost":            "Lost",
    "no_reply":        "No Reply",
}

STATUS_CSS = {
    "cold":        "cold",
    "queued":      "queued",
    "contacted":   "contacted",
    "followed_up": "followedup",
    "replied":     "replied",
    "meeting":     "meeting",
    "won":         "won",
    "lost":        "lost",
    "no_reply":    "noreply",
}

STATUS_PROG_CSS = {
    "cold":        "cold",
    "queued":      "queued",
    "contacted":   "contacted",
    "followed_up": "followedup",
    "replied":     "replied",
    "meeting":     "meeting",
    "won":         "won",
    "lost":        "lost",
    "no_reply":    "noreply",
}

COUNTRY_FLAG = {
    "UK":        "🇬🇧",
    "USA":       "🇺🇸",
    "UAE":       "🇦🇪",
    "Canada":    "🇨🇦",
    "Australia": "🇦🇺",
}

TZ_DISPLAY = {
    "GMT":  "🕐 GMT (UTC+0)",
    "EST":  "🕐 EST (UTC-5)",
    "PST":  "🕐 PST (UTC-8)",
    "CST":  "🕐 CST (UTC-6)",
    "MST":  "🕐 MST (UTC-7)",
    "GST":  "🕐 GST (UTC+4)",
    "AEST": "🕐 AEST (UTC+10)",
}


def score_info(score):
    """Return (css_class, label_text) for a lead type score."""
    if score >= 4:
        return ("type-high", "🔥 High")
    elif score >= 2:
        return ("type-medium", "🟡 Medium")
    else:
        return ("type-low", "Low")


def track_css(track):
    """Return CSS class for a track badge."""
    return {
        "Agency":    "track-agency",
        "Recruiter": "track-recruiter",
        "Direct":    "track-direct",
        "Job":       "track-job",
    }.get(track, "track-job")


def format_added_date(added_date):
    """Return 'D Mon YYYY' formatted date string."""
    if not added_date:
        return ""
    if isinstance(added_date, str):
        try:
            added_date = datetime.strptime(added_date, "%Y-%m-%d").date()
        except ValueError:
            return str(added_date)
    if hasattr(added_date, "strftime"):
        # %-d is Linux-only; lstrip removes leading zero cross-platform
        return added_date.strftime("%d %b %Y").lstrip("0")
    return str(added_date)


def _safe_str(val):
    """Convert value to JSON-serialisable type."""
    if isinstance(val, (datetime, date)):
        return val.isoformat()
    return val


def enrich_lead(row, cols):
    """Convert a DuckDB row to an enriched dict for template rendering."""
    lead = dict(zip(cols, row))
    status = lead.get("status", "cold")
    score  = lead.get("lead_type_score", 1) or 1
    track  = lead.get("track", "Job")
    country = lead.get("country", "")

    lead["status_display"]  = STATUS_DISPLAY.get(status, status.title())
    lead["status_css"]      = STATUS_CSS.get(status, "cold")
    lead["prog_css"]        = STATUS_PROG_CSS.get(status, "cold")
    lead["score_css"], lead["score_label"] = score_info(score)
    lead["track_css"]       = track_css(track)
    lead["flag"]            = COUNTRY_FLAG.get(country, "")
    lead["tz_display"]      = TZ_DISPLAY.get(lead.get("timezone", "GMT"), "")
    lead["added_date_fmt"]  = format_added_date(lead.get("added_date"))

    # Determine contact display name
    full = lead.get("full_name", "").strip()
    role = lead.get("role", "")
    lead["contact_display"] = f"{full} · {role}" if (full and role) else (full or role or "—")

    return lead


def enrich_email(row, cols):
    """Convert a DuckDB email row to a dict for JSON serialisation."""
    e = {cols[i]: _safe_str(row[i]) for i in range(len(cols))}
    return e


def compute_email_type_pill(email_type, sequence_step):
    """Return (label, css_class) for the email type pill.

    Primary dispatch is on email_type (follow_up_1 / follow_up_2 / follow_up_3).
    Falls back to sequence_step for any legacy 'follow_up' rows.
    """
    if email_type == "initial":
        return ("Initial email", "pill-initial")
    if email_type == "follow_up_1":
        return ("Follow-up 1", "pill-followup")
    if email_type == "follow_up_2":
        return ("Follow-up 2", "pill-followup")
    if email_type == "follow_up_3":
        return ("Follow-up 3", "pill-followup")
    # Legacy fallback: old 'follow_up' generic value — use sequence_step
    step = int(sequence_step or 1)
    if step <= 2:
        return ("Follow-up 1", "pill-followup")
    elif step == 3:
        return ("Follow-up 2", "pill-followup")
    else:
        return ("Follow-up 3", "pill-followup")


def format_send_time(scheduled_at, timezone):
    """Format datetime as 'Mon 6 Mar · 8:30am EST'."""
    if not scheduled_at:
        return ""
    if isinstance(scheduled_at, str):
        try:
            scheduled_at = datetime.fromisoformat(scheduled_at)
        except ValueError:
            return ""
    hour_24 = scheduled_at.hour
    hour_12 = hour_24 % 12 or 12
    ampm = "am" if hour_24 < 12 else "pm"
    minute = scheduled_at.strftime("%M")
    time_str = f"{hour_12}:{minute}{ampm}" if minute != "00" else f"{hour_12}{ampm}"
    return (
        f"{scheduled_at.strftime('%a')} {scheduled_at.day} "
        f"{scheduled_at.strftime('%b')} · {time_str} {timezone or 'GMT'}"
    )


def format_schedule_note(scheduled_at, timezone):
    """Format 'Will send Mon 6 Mar at 8:30am EST (recipient local time)'."""
    if not scheduled_at:
        return ""
    if isinstance(scheduled_at, str):
        try:
            scheduled_at = datetime.fromisoformat(scheduled_at)
        except ValueError:
            return ""
    hour_24 = scheduled_at.hour
    hour_12 = hour_24 % 12 or 12
    ampm = "am" if hour_24 < 12 else "pm"
    minute = scheduled_at.strftime("%M")
    time_str = f"{hour_12}:{minute}{ampm}" if minute != "00" else f"{hour_12}{ampm}"
    return (
        f"Will send {scheduled_at.strftime('%a')} {scheduled_at.day} "
        f"{scheduled_at.strftime('%b')} at {time_str} {timezone or 'GMT'} "
        f"(recipient local time)"
    )


def _get_lead_columns(conn):
    """Return column names for outreach_leads."""
    info = conn.execute("PRAGMA table_info(outreach_leads)").fetchall()
    return [r[1] for r in info]


def _get_email_columns(conn):
    """Return column names for outreach_emails."""
    info = conn.execute("PRAGMA table_info(outreach_emails)").fetchall()
    return [r[1] for r in info]


# ── Main Leads page ───────────────────────────────────────────────────────────
@bp.route("/leads")
@login_required
def leads():
    config  = get_current_config()
    clients = get_available_clients()
    current_client_path = session.get("current_client_config")

    conn = get_outreach_db()
    try:
        lead_cols  = _get_lead_columns(conn)
        email_cols = _get_email_columns(conn)

        # ── Stats ────────────────────────────────────────────────────────────
        total = conn.execute(
            "SELECT COUNT(*) FROM outreach_leads"
        ).fetchone()[0]

        contacted = conn.execute(
            "SELECT COUNT(*) FROM outreach_leads WHERE status IN "
            "('contacted','followed_up','replied','meeting','won','no_reply')"
        ).fetchone()[0]

        replies = conn.execute(
            "SELECT COUNT(DISTINCT lead_id) FROM outreach_emails WHERE reply_received = true"
        ).fetchone()[0]

        hot_leads = conn.execute(
            "SELECT COUNT(*) FROM outreach_leads WHERE lead_type_score >= 4"
        ).fetchone()[0]

        won = conn.execute(
            "SELECT COUNT(*) FROM outreach_leads WHERE status = 'won'"
        ).fetchone()[0]

        stats = {
            "total":     total,
            "contacted": contacted,
            "replies":   replies,
            "hot_leads": hot_leads,
            "won":       won,
        }

        # ── Leads ────────────────────────────────────────────────────────────
        lead_rows = conn.execute(
            "SELECT * FROM outreach_leads ORDER BY added_date DESC, last_activity DESC"
        ).fetchall()
        leads_list = [enrich_lead(r, lead_cols) for r in lead_rows]

        # ── Emails (for slide panel) ─────────────────────────────────────────
        email_rows = conn.execute(
            "SELECT * FROM outreach_emails ORDER BY sent_at DESC, scheduled_at DESC"
        ).fetchall()
        emails_by_lead = {}
        for row in email_rows:
            e = enrich_email(row, email_cols)
            lid = e.get("lead_id")
            if lid not in emails_by_lead:
                emails_by_lead[lid] = []
            emails_by_lead[lid].append(e)

        # ── Serialise to JSON for JS ─────────────────────────────────────────
        def lead_to_js(lead):
            return {k: _safe_str(v) for k, v in lead.items()}

        leads_json = json.dumps([lead_to_js(l) for l in leads_list])
        emails_json = json.dumps(emails_by_lead)

    except Exception as e:
        print(f"[OUTREACH] Error loading leads: {e}")
        stats = {"total": 0, "contacted": 0, "replies": 0, "hot_leads": 0, "won": 0}
        leads_list = []
        leads_json = "[]"
        emails_json = "{}"
    finally:
        conn.close()

    return render_template(
        "outreach/leads.html",
        client_name=config.client_name,
        available_clients=clients,
        current_client_config=current_client_path,
        stats=stats,
        leads=leads_list,
        leads_json=leads_json,
        emails_json=emails_json,
    )


# ── PATCH /outreach/leads/<lead_id>/notes ────────────────────────────────────
@bp.route("/leads/<lead_id>/notes", methods=["PATCH"])
@login_required
def patch_lead_notes(lead_id):
    """Save notes text for a lead. AJAX endpoint — CSRF exempt."""
    data = request.get_json(silent=True)
    if not data or "notes" not in data:
        return jsonify({"success": False, "message": "Missing notes field"}), 400

    notes = str(data["notes"]).strip()
    conn = get_outreach_db()
    try:
        conn.execute(
            "UPDATE outreach_leads SET notes = ?, last_activity = ? WHERE lead_id = ?",
            [notes, datetime.now(), lead_id]
        )
        return jsonify({"success": True, "notes": notes})
    except Exception as e:
        print(f"[OUTREACH] Notes update error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()


# ── POST /outreach/leads/<lead_id>/mark-won ──────────────────────────────────
@bp.route("/leads/<lead_id>/mark-won", methods=["POST"])
@login_required
def mark_won(lead_id):
    """Mark a lead as won (stage 8). AJAX endpoint — CSRF exempt."""
    conn = get_outreach_db()
    try:
        conn.execute(
            "UPDATE outreach_leads SET status = 'won', progress_stage = 8, "
            "last_activity = ? WHERE lead_id = ?",
            [datetime.now(), lead_id]
        )
        return jsonify({"success": True})
    except Exception as e:
        print(f"[OUTREACH] mark-won error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()


# ── POST /outreach/leads/<lead_id>/mark-lost ─────────────────────────────────
@bp.route("/leads/<lead_id>/mark-lost", methods=["POST"])
@login_required
def mark_lost(lead_id):
    """Mark a lead as lost (stage 8). AJAX endpoint — CSRF exempt."""
    conn = get_outreach_db()
    try:
        conn.execute(
            "UPDATE outreach_leads SET status = 'lost', progress_stage = 8, "
            "last_activity = ? WHERE lead_id = ?",
            [datetime.now(), lead_id]
        )
        return jsonify({"success": True})
    except Exception as e:
        print(f"[OUTREACH] mark-lost error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()


# ── Status → pipeline stage mapping ──────────────────────────────────────────
_STATUS_STAGE = {
    "cold": 1, "queued": 2, "contacted": 3, "followed_up": 4,
    "no_reply": 5, "replied": 6, "meeting": 7, "won": 8, "lost": 8,
}


# ── POST /outreach/leads/<lead_id>/update-status ──────────────────────────────
@bp.route("/leads/<lead_id>/update-status", methods=["POST"])
@login_required
def update_status(lead_id):
    """Update a lead's status and progress_stage. AJAX endpoint — CSRF exempt."""
    data = request.get_json(silent=True)
    if not data or "status" not in data:
        return jsonify({"success": False, "message": "Missing status field"}), 400

    new_status = str(data["status"]).strip().lower()
    if new_status not in _STATUS_STAGE:
        return jsonify({"success": False, "message": f"Invalid status: {new_status}"}), 400

    stage = _STATUS_STAGE[new_status]
    conn = get_outreach_db()
    try:
        conn.execute(
            "UPDATE outreach_leads SET status = ?, progress_stage = ?, "
            "last_activity = ? WHERE lead_id = ?",
            [new_status, stage, datetime.now(), lead_id]
        )
        return jsonify({"success": True})
    except Exception as e:
        print(f"[OUTREACH] update-status error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()


# ── POST /outreach/leads/<lead_id>/delete ─────────────────────────────────────
@bp.route("/leads/<lead_id>/delete", methods=["POST"])
@login_required
def delete_lead(lead_id):
    """Delete a lead and cascade to emails + tracking events. AJAX — CSRF exempt."""
    conn = get_outreach_db()
    try:
        conn.execute(
            "DELETE FROM outreach_tracking_events WHERE tracking_id IN "
            "(SELECT tracking_id FROM outreach_emails WHERE lead_id = ?)",
            [lead_id]
        )
        conn.execute("DELETE FROM outreach_emails WHERE lead_id = ?", [lead_id])
        conn.execute("DELETE FROM outreach_leads WHERE lead_id = ?", [lead_id])
        return jsonify({"success": True})
    except Exception as e:
        print(f"[OUTREACH] delete-lead error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()


# ── POST /outreach/leads/add ─────────────────────────────────────────────────
@bp.route("/leads/add", methods=["POST"])
@login_required
def add_lead():
    """Insert a new lead. AJAX endpoint — CSRF exempt."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "message": "No JSON body"}), 400

    company = (data.get("company") or "").strip()
    email   = (data.get("email") or "").strip()
    track   = (data.get("track") or "").strip()
    country = (data.get("country") or "").strip()
    source  = (data.get("source") or "").strip()

    if not company or not email or not track or not country or not source:
        return jsonify({"success": False, "message": "Missing required fields"}), 400

    contact_name = (data.get("contact_name") or "").strip()
    city_state   = (data.get("city_state") or "").strip()
    notes        = (data.get("notes") or "").strip()

    first_name = ""
    last_name  = ""
    full_name  = contact_name

    # Simple name split
    parts = contact_name.split(" ", 1)
    if len(parts) == 2:
        first_name, last_name = parts[0], parts[1]
    elif parts:
        first_name = parts[0]

    # Default score by track
    score_map = {"Agency": 3, "Recruiter": 2, "Direct": 3, "Job": 1}
    score = score_map.get(track, 1)

    # Default timezone by country
    tz_map = {"UK": "GMT", "USA": "EST", "UAE": "GST", "Canada": "EST", "Australia": "AEST"}
    timezone = tz_map.get(country, "GMT")

    lead_id    = str(uuid.uuid4())
    added_date = date.today()
    now        = datetime.now()

    conn = get_outreach_db()
    try:
        conn.execute(
            """INSERT INTO outreach_leads
               (lead_id, first_name, last_name, full_name, company, role, email,
                linkedin_url, website, city_state, country, timezone,
                track, source, lead_type_score, status, progress_stage,
                notes, added_date, last_activity, sequence_step, do_not_contact)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            [lead_id, first_name, last_name, full_name, company,
             data.get("role", ""), email, "", "", city_state,
             country, timezone, track, source, score,
             "cold", 1, notes, added_date, now, 0, False]
        )
        return jsonify({"success": True, "lead_id": lead_id})
    except Exception as e:
        print(f"[OUTREACH] Add lead error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()


# ── GET /outreach/queue ───────────────────────────────────────────────────────
@bp.route("/queue")
@login_required
def queue():
    """Queue page — emails awaiting approval before sending."""
    config  = get_current_config()
    clients = get_available_clients()
    current_client_path = session.get("current_client_config")

    conn = get_outreach_db()
    try:
        awaiting = conn.execute(
            "SELECT COUNT(*) FROM outreach_emails WHERE status = 'queued'"
        ).fetchone()[0]

        scheduled_this_week = conn.execute(
            "SELECT COUNT(*) FROM outreach_emails WHERE status = 'queued' "
            "AND scheduled_at <= CURRENT_TIMESTAMP + INTERVAL '7 days'"
        ).fetchone()[0]

        sent_today = conn.execute(
            "SELECT COUNT(*) FROM outreach_emails WHERE status = 'sent' "
            "AND sent_at >= CURRENT_DATE"
        ).fetchone()[0]

        daily_limit_remaining = max(0, 50 - sent_today)

        stats = {
            "awaiting":              awaiting,
            "scheduled_this_week":   scheduled_this_week,
            "sent_today":            sent_today,
            "daily_limit_remaining": daily_limit_remaining,
        }

        rows = conn.execute("""
            SELECT e.email_id, e.lead_id, e.email_type, e.subject, e.body,
                   e.cv_attached, e.scheduled_at,
                   l.company, l.full_name, l.role, l.email, l.city_state,
                   l.country, l.track, l.timezone, l.sequence_step
            FROM outreach_emails e
            JOIN outreach_leads l ON e.lead_id = l.lead_id
            WHERE e.status = 'queued'
            ORDER BY e.scheduled_at ASC
        """).fetchall()

        queued_emails = []
        for row in rows:
            (email_id, lead_id, email_type, subject, body, cv_attached,
             scheduled_at, company, full_name, role, email_addr, city_state,
             country, track, timezone, sequence_step) = row

            pill_label, pill_css = compute_email_type_pill(email_type, sequence_step)
            send_time     = format_send_time(scheduled_at, timezone)
            schedule_note = format_schedule_note(scheduled_at, timezone)

            queued_emails.append({
                "email_id":      email_id,
                "lead_id":       lead_id,
                "email_type":    email_type or "",
                "subject":       subject or "",
                "body":          body or "",
                "cv_attached":   bool(cv_attached),
                "company":       company or "",
                "full_name":     full_name or "",
                "role":          role or "",
                "email":         email_addr or "",
                "city_state":    city_state or "",
                "country":       country or "",
                "flag":          COUNTRY_FLAG.get(country or "", ""),
                "track":         track or "",
                "track_css":     track_css(track or ""),
                "timezone":      timezone or "GMT",
                "sequence_step": int(sequence_step or 0),
                "pill_label":    pill_label,
                "pill_css":      pill_css,
                "send_time":     send_time,
                "schedule_note": schedule_note,
            })

    except Exception as e:
        print(f"[OUTREACH] Error loading queue: {e}")
        stats = {
            "awaiting": 0, "scheduled_this_week": 0,
            "sent_today": 0, "daily_limit_remaining": 50,
        }
        queued_emails = []
    finally:
        conn.close()

    return render_template(
        "outreach/queue.html",
        client_name=config.client_name,
        available_clients=clients,
        current_client_config=current_client_path,
        stats=stats,
        queued_emails=queued_emails,
    )


# ── Chat 73: Tracking helper ──────────────────────────────────────────────────
def inject_tracking(body_html, email_id, base_url, has_cv=False):
    """Wrap href links with click-tracking redirect and append open-pixel."""
    import re
    import urllib.parse

    # Wrap all http/https links with click-tracking redirect
    def replace_href(m):
        original_url = m.group(1)
        encoded = urllib.parse.quote(original_url, safe='')
        return f'href="{base_url}/outreach/track/click/{email_id}?url={encoded}"'

    body_html = re.sub(r'href="(https?://[^"]+)"', replace_href, body_html)

    # Inject CV link just before signature separator <br><br><hr
    if has_cv:
        cv_link = f'<a href="{base_url}/outreach/track/cv/{email_id}">View my CV</a>'
        body_html = body_html.replace('<br><br><hr', f'{cv_link}<br><br><hr', 1)

    # Append open-pixel just before closing </div>
    pixel = (
        f'<img src="{base_url}/outreach/track/open/{email_id}" '
        f'width="1" height="1" style="display:none;" />'
    )
    body_html = body_html.replace('</div>', f'{pixel}</div>', 1)

    return body_html


# ── POST /outreach/queue/<email_id>/send ─────────────────────────────────────
@bp.route("/queue/<email_id>/send", methods=["POST"])
@login_required
def queue_send(email_id):
    """Send real email via Gmail SMTP then mark as sent. AJAX — CSRF exempt."""
    from act_dashboard.email_sender import send_email, check_daily_limit, get_signature_html, load_email_config

    conn = get_outreach_db()
    try:
        # Fetch email content + recipient from DB
        row = conn.execute("""
            SELECT e.lead_id, e.subject, e.body, e.cv_attached,
                   l.email, l.first_name, l.full_name, l.company
            FROM outreach_emails e
            JOIN outreach_leads l ON e.lead_id = l.lead_id
            WHERE e.email_id = ?
        """, [email_id]).fetchone()
        if not row:
            return jsonify({"success": False, "message": "Email not found"}), 404

        lead_id, subject, body, cv_attached, to_email, first_name, full_name, company = row

        # Substitute placeholders with lead data before sending
        # Templates use single-brace format: {first_name}
        _vars = {
            "first_name": first_name or (full_name.split()[0] if full_name else ""),
            "full_name":  full_name or "",
            "company":    company or "",
        }
        for key, val in _vars.items():
            subject = subject.replace("{" + key + "}", val)
            body    = body.replace("{" + key + "}", val)
        print(f"[OUTREACH] send: email_id={email_id} to={to_email} subject='{subject[:60]}'")

        # Check daily sending limit
        limit_info = check_daily_limit(conn)
        if limit_info["remaining"] <= 0:
            return jsonify({
                "success": False,
                "message": f"Daily limit reached ({limit_info['limit']} emails/day). Try again tomorrow.",
            }), 429

        # Convert plain-text body to HTML and append signature
        body_html = (
            "<div style='font-family:Arial,sans-serif;font-size:14px;"
            "line-height:1.6;color:#333;'>"
            + (body or "").replace("\n", "<br>")
            + "</div>"
            + get_signature_html()
        )
        # Resolve CV attachment path if toggle is on
        attachment_path = None
        if cv_attached:
            cv_files = [f for f in _CV_DIR.iterdir() if f.is_file()] if _CV_DIR.exists() else []
            if cv_files:
                attachment_path = str(cv_files[0])
            else:
                print(f"[OUTREACH] WARNING: cv_attached=True for {email_id} but no CV file found on disk")

        # Chat 73: inject open/click/CV tracking into email body
        email_config = load_email_config()
        base_url = email_config.get('base_url', 'http://localhost:5000')
        has_cv = bool(cv_attached and attachment_path)
        body_html = inject_tracking(body_html, email_id, base_url, has_cv=has_cv)

        # Send the actual email via Gmail SMTP
        result = send_email(
            to_email=to_email,
            subject=subject,
            body_html=body_html,
            attachment_path=attachment_path,
        )
        if not result["success"]:
            return jsonify({"success": False, "message": result.get("error", "Send failed")}), 500

        # Update DB on success
        now = datetime.now()
        conn.execute(
            "UPDATE outreach_emails SET status = 'sent', sent_at = ? WHERE email_id = ?",
            [now, email_id],
        )
        conn.execute(
            "UPDATE outreach_leads SET status = 'contacted', progress_stage = 3, "
            "last_activity = ? WHERE lead_id = ? AND status IN ('cold', 'queued')",
            [now, lead_id],
        )
        return jsonify({"success": True, "message": "Email sent"})
    except Exception as e:
        print(f"[OUTREACH] queue send error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()


# ── Chat 73: Tracking endpoints (CSRF exempt — no session in email client) ────

# ── GET /outreach/track/open/<email_id> ──────────────────────────────────────
@bp.route("/track/open/<email_id>", methods=["GET"])
def track_open(email_id):
    """Return 1×1 GIF and increment open_count. No auth — loads in email client."""
    from flask import Response
    GIF_1X1 = (
        b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff'
        b'\x00\x00\x00\x21\xf9\x04\x00\x00\x00\x00\x00\x2c\x00\x00\x00\x00'
        b'\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
    )
    conn = get_outreach_db()
    try:
        row = conn.execute(
            "SELECT email_id FROM outreach_emails WHERE email_id = ?", [email_id]
        ).fetchone()
        if row:
            conn.execute(
                "UPDATE outreach_emails SET open_count = open_count + 1, "
                "opened_at = COALESCE(opened_at, now()) WHERE email_id = ?",
                [email_id],
            )
            print(f"[TRACKING] open: email_id={email_id}")
    except Exception as e:
        print(f"[TRACKING] open error: {e}")
    finally:
        conn.close()
    return Response(GIF_1X1, mimetype='image/gif',
                    headers={'Cache-Control': 'no-cache, no-store'})


# ── GET /outreach/track/click/<email_id>?url=<target_url> ────────────────────
@bp.route("/track/click/<email_id>", methods=["GET"])
def track_click(email_id):
    """Increment click_count and redirect to target URL. No auth — opens in email client."""
    from flask import redirect
    target_url = request.args.get('url', '/')
    conn = get_outreach_db()
    try:
        row = conn.execute(
            "SELECT email_id FROM outreach_emails WHERE email_id = ?", [email_id]
        ).fetchone()
        if row:
            conn.execute(
                "UPDATE outreach_emails SET click_count = click_count + 1, "
                "clicked_at = COALESCE(clicked_at, now()) WHERE email_id = ?",
                [email_id],
            )
            print(f"[TRACKING] click: email_id={email_id} → {target_url}")
    except Exception as e:
        print(f"[TRACKING] click error: {e}")
    finally:
        conn.close()
    return redirect(target_url)


# ── GET /outreach/track/cv/<email_id> ────────────────────────────────────────
@bp.route("/track/cv/<email_id>", methods=["GET"])
def track_cv(email_id):
    """Increment cv_open_count and redirect to CV file. No auth — opens in email client."""
    from flask import redirect, url_for
    conn = get_outreach_db()
    try:
        row = conn.execute(
            "SELECT email_id FROM outreach_emails WHERE email_id = ?", [email_id]
        ).fetchone()
        if row:
            conn.execute(
                "UPDATE outreach_emails SET cv_open_count = cv_open_count + 1, "
                "cv_opened_at = COALESCE(cv_opened_at, now()) WHERE email_id = ?",
                [email_id],
            )
            print(f"[TRACKING] cv_open: email_id={email_id}")
        cv_row = conn.execute(
            "SELECT value FROM system_config WHERE key = 'cv_path'"
        ).fetchone()
    except Exception as e:
        print(f"[TRACKING] cv error: {e}")
        return "Not found", 404
    finally:
        conn.close()
    if not cv_row or not cv_row[0]:
        return "No CV on file", 404
    cv_filename = Path(cv_row[0]).name
    return redirect(url_for('static', filename='uploads/cv/' + cv_filename))


# ── POST /outreach/queue/<email_id>/skip ─────────────────────────────────────
@bp.route("/queue/<email_id>/skip", methods=["POST"])
@login_required
def queue_skip(email_id):
    """Delay email by 2 days (move to back of queue). AJAX — CSRF exempt."""
    conn = get_outreach_db()
    try:
        conn.execute(
            "UPDATE outreach_emails SET scheduled_at = scheduled_at + INTERVAL '2 days' "
            "WHERE email_id = ?",
            [email_id],
        )
        return jsonify({"success": True})
    except Exception as e:
        print(f"[OUTREACH] queue skip error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()


# ── POST /outreach/queue/<email_id>/discard ───────────────────────────────────
@bp.route("/queue/<email_id>/discard", methods=["POST"])
@login_required
def queue_discard(email_id):
    """Mark email as discarded. AJAX — CSRF exempt."""
    conn = get_outreach_db()
    try:
        conn.execute(
            "UPDATE outreach_emails SET status = 'discarded' WHERE email_id = ?",
            [email_id],
        )
        return jsonify({"success": True})
    except Exception as e:
        print(f"[OUTREACH] queue discard error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()


# ── GET /outreach/queue/<email_id>/get ────────────────────────────────────────
@bp.route("/queue/<email_id>/get", methods=["GET"])
@login_required
def queue_get(email_id):
    """Return subject + body for the edit modal. AJAX — CSRF exempt."""
    conn = get_outreach_db()
    try:
        row = conn.execute(
            "SELECT email_id, subject, body FROM outreach_emails "
            "WHERE email_id = ? AND status = 'queued'",
            [email_id],
        ).fetchone()
        if not row:
            return jsonify({"success": False, "message": "Email not found or not queued"}), 404
        return jsonify({"success": True, "email_id": row[0], "subject": row[1] or "", "body": row[2] or ""})
    except Exception as e:
        print(f"[OUTREACH] queue get error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()


# ── POST /outreach/queue/<email_id>/edit ──────────────────────────────────────
@bp.route("/queue/<email_id>/edit", methods=["POST"])
@login_required
def queue_edit(email_id):
    """Save updated subject + body to outreach_emails (queued only). AJAX — CSRF exempt."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "message": "No JSON body"}), 400

    subject = str(data.get("subject", "")).strip()
    body    = str(data.get("body", "")).strip()

    if not subject:
        return jsonify({"success": False, "message": "Subject is required"}), 400

    conn = get_outreach_db()
    try:
        result = conn.execute(
            "UPDATE outreach_emails SET subject = ?, body = ? "
            "WHERE email_id = ? AND status = 'queued'",
            [subject, body, email_id],
        )
        print(f"[OUTREACH] queue edit: {email_id} subject='{subject[:60]}'")
        return jsonify({"success": True, "subject": subject})
    except Exception as e:
        print(f"[OUTREACH] queue edit error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()


# ── GET /outreach/queue/<email_id>/templates ──────────────────────────────────
@bp.route("/queue/<email_id>/templates", methods=["GET"])
@login_required
def queue_get_templates(email_id):
    """Return templates filtered by the lead's track type. AJAX — CSRF exempt."""
    conn = get_outreach_db()
    try:
        # Fetch lead's track via the email record
        track_row = conn.execute(
            "SELECT l.track FROM outreach_emails e "
            "JOIN outreach_leads l ON e.lead_id = l.lead_id "
            "WHERE e.email_id = ? AND e.status = 'queued'",
            [email_id],
        ).fetchone()
        if not track_row:
            return jsonify({"success": False, "message": "Email not found or not queued"}), 404

        track = track_row[0] or "Job"

        rows = conn.execute(
            "SELECT template_id, name, sequence_step, subject, body "
            "FROM outreach_templates WHERE active = true ORDER BY sequence_step ASC",
        ).fetchall()

        templates = [
            {
                "template_id": str(r[0]),
                "name":        r[1] or "",
                "step":        int(r[2] or 1),
                "subject":     r[3] or "",
                "body":        r[4] or "",
            }
            for r in rows
        ]
        return jsonify({"success": True, "track": track, "templates": templates})
    except Exception as e:
        print(f"[OUTREACH] queue get-templates error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()


# ── POST /outreach/queue/<email_id>/switch-template ───────────────────────────
@bp.route("/queue/<email_id>/switch-template", methods=["POST"])
@login_required
def queue_switch_template(email_id):
    """Apply a template's subject + body to the queued email. AJAX — CSRF exempt."""
    data = request.get_json(silent=True)
    if not data or "template_id" not in data:
        return jsonify({"success": False, "message": "Missing template_id"}), 400

    template_id = str(data["template_id"]).strip()

    conn = get_outreach_db()
    try:
        tmpl = conn.execute(
            "SELECT subject, body FROM outreach_templates WHERE template_id = ?",
            [template_id],
        ).fetchone()
        if not tmpl:
            return jsonify({"success": False, "message": "Template not found"}), 404

        subject, body = tmpl[0] or "", tmpl[1] or ""

        conn.execute(
            "UPDATE outreach_emails SET subject = ?, body = ? "
            "WHERE email_id = ? AND status = 'queued'",
            [subject, body, email_id],
        )
        print(f"[OUTREACH] switch-template: email={email_id} template={template_id} subject='{subject[:60]}'")
        return jsonify({"success": True, "subject": subject})
    except Exception as e:
        print(f"[OUTREACH] queue switch-template error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()


# ── GET /outreach/cv/status ───────────────────────────────────────────────────
@bp.route("/cv/status", methods=["GET"])
@login_required
def cv_status():
    """Return CV upload status. AJAX — CSRF exempt."""
    _CV_DIR.mkdir(parents=True, exist_ok=True)
    files = [f for f in _CV_DIR.iterdir() if f.is_file()]
    if files:
        f = files[0]
        return jsonify({
            "uploaded":  True,
            "filename":  f.name,
            "filesize":  f.stat().st_size,
        })
    return jsonify({"uploaded": False, "filename": "", "filesize": 0})


# ── POST /outreach/cv/upload ──────────────────────────────────────────────────
@bp.route("/cv/upload", methods=["POST"])
@login_required
def cv_upload():
    """Upload a PDF as the active CV. AJAX — CSRF exempt."""
    if "cv_file" not in request.files:
        return jsonify({"success": False, "message": "No file provided"}), 400
    f = request.files["cv_file"]
    if not f.filename:
        return jsonify({"success": False, "message": "No file selected"}), 400
    if not f.filename.lower().endswith(".pdf"):
        return jsonify({"success": False, "message": "Only PDF files are allowed"}), 400

    data = f.read()
    if len(data) > 5 * 1024 * 1024:
        return jsonify({"success": False, "message": "File exceeds 5MB limit"}), 400

    _CV_DIR.mkdir(parents=True, exist_ok=True)
    for old in _CV_DIR.iterdir():
        if old.is_file():
            old.unlink()

    filename = f.filename
    dest = _CV_DIR / filename
    dest.write_bytes(data)

    conn = get_outreach_db()
    try:
        conn.execute(
            "INSERT INTO system_config (key, value) VALUES ('cv_path', ?) "
            "ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value",
            [str(dest)],
        )
    except Exception as e:
        print(f"[OUTREACH] cv_upload db error: {e}")
    finally:
        conn.close()

    print(f"[OUTREACH] CV uploaded: {filename} ({len(data)} bytes)")
    return jsonify({"success": True, "filename": filename, "filesize": len(data)})


# ── POST /outreach/cv/remove ──────────────────────────────────────────────────
@bp.route("/cv/remove", methods=["POST"])
@login_required
def cv_remove():
    """Remove the active CV. AJAX — CSRF exempt."""
    _CV_DIR.mkdir(parents=True, exist_ok=True)
    for old in _CV_DIR.iterdir():
        if old.is_file():
            old.unlink()
    conn = get_outreach_db()
    try:
        conn.execute("DELETE FROM system_config WHERE key = 'cv_path'")
    except Exception as e:
        print(f"[OUTREACH] cv_remove db error: {e}")
    finally:
        conn.close()
    print("[OUTREACH] CV removed")
    return jsonify({"success": True})


# ── POST /outreach/queue/<email_id>/toggle-cv ─────────────────────────────────
@bp.route("/queue/<email_id>/toggle-cv", methods=["POST"])
@login_required
def queue_toggle_cv(email_id):
    """Toggle cv_attached boolean on outreach_emails row. AJAX — CSRF exempt."""
    conn = get_outreach_db()
    try:
        row = conn.execute(
            "SELECT cv_attached FROM outreach_emails WHERE email_id = ?",
            [email_id],
        ).fetchone()
        if not row:
            return jsonify({"success": False, "message": "Email not found"}), 404
        new_val = not bool(row[0])
        conn.execute(
            "UPDATE outreach_emails SET cv_attached = ? WHERE email_id = ?",
            [new_val, email_id],
        )
        return jsonify({"success": True, "cv_attached": new_val})
    except Exception as e:
        print(f"[OUTREACH] toggle_cv error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()


# ── Sent page helpers ─────────────────────────────────────────────────────────

def format_sent_at(sent_at, timezone):
    """Return ('5 Mar 2026', '8:30am EST') from sent_at datetime."""
    if not sent_at:
        return ("—", "")
    if isinstance(sent_at, str):
        try:
            sent_at = datetime.fromisoformat(sent_at)
        except ValueError:
            return (str(sent_at), "")
    date_str = sent_at.strftime("%d %b %Y").lstrip("0")
    hour_24 = sent_at.hour
    hour_12 = hour_24 % 12 or 12
    ampm = "am" if hour_24 < 12 else "pm"
    minute = sent_at.strftime("%M")
    time_str = f"{hour_12}:{minute}{ampm}" if minute != "00" else f"{hour_12}{ampm}"
    tz = timezone or "GMT"
    return (date_str, f"{time_str} {tz}")


def compute_followup_status(followup_due, today):
    """Return (status_key, display_label) for a followup_due date."""
    if followup_due is None:
        return ("none", "—")
    if isinstance(followup_due, str):
        try:
            followup_due = datetime.strptime(followup_due, "%Y-%m-%d").date()
        except ValueError:
            return ("none", "—")
    # DuckDB may return datetime; get date portion
    if hasattr(followup_due, "date") and callable(followup_due.date):
        followup_due = followup_due.date()
    if followup_due < today:
        delta = (today - followup_due).days
        return ("overdue", f"Overdue · {delta} day{'s' if delta != 1 else ''}")
    if followup_due == today:
        return ("today", "Today")
    label = followup_due.strftime("%d %b %Y").lstrip("0")
    return ("soon", label)


# ── GET /outreach/sent ────────────────────────────────────────────────────────
@bp.route("/sent")
@login_required
def sent():
    """Sent page — all sent emails with follow-up tracking."""
    config  = get_current_config()
    clients = get_available_clients()
    current_client_path = session.get("current_client_config")

    today = date.today()
    conn = get_outreach_db()
    try:
        total_sent = conn.execute(
            "SELECT COUNT(*) FROM outreach_emails WHERE status = 'sent'"
        ).fetchone()[0]

        overdue_count = conn.execute(
            "SELECT COUNT(*) FROM outreach_emails WHERE status = 'sent' AND followup_due < ?",
            [today]
        ).fetchone()[0]

        due_today_count = conn.execute(
            "SELECT COUNT(*) FROM outreach_emails WHERE status = 'sent' AND followup_due = ?",
            [today]
        ).fetchone()[0]

        replied_count = conn.execute(
            "SELECT COUNT(*) FROM outreach_leads WHERE status IN ('replied', 'meeting', 'won')"
        ).fetchone()[0]

        closed_count = conn.execute(
            "SELECT COUNT(*) FROM outreach_leads WHERE status IN ('no_reply', 'lost')"
        ).fetchone()[0]

        stats = {
            "total_sent":   total_sent,
            "overdue":      overdue_count,
            "due_today":    due_today_count,
            "replied":      replied_count,
            "closed":       closed_count,
        }

        rows = conn.execute("""
            SELECT e.email_id, e.lead_id, e.email_type, e.subject,
                   e.sent_at, e.followup_due,
                   e.cv_attached, e.reply_received, e.reply_text,
                   l.company, l.full_name, l.email, l.track,
                   l.status, l.timezone, l.sequence_step
            FROM outreach_emails e
            JOIN outreach_leads l ON e.lead_id = l.lead_id
            WHERE e.status = 'sent'
            ORDER BY e.sent_at DESC
        """).fetchall()

        sent_emails = []
        for row in rows:
            (email_id, lead_id, email_type, subject,
             sent_at, followup_due,
             cv_attached, reply_received, reply_text,
             company, full_name, email_addr, track,
             lead_status, timezone, sequence_step) = row

            date_str, time_str = format_sent_at(sent_at, timezone)
            due_status, due_label = compute_followup_status(followup_due, today)
            pill_label, pill_css = compute_email_type_pill(email_type, sequence_step)
            status_css = STATUS_CSS.get(lead_status or "", "cold")
            status_display = STATUS_DISPLAY.get(lead_status or "", "—")

            sent_emails.append({
                "email_id":       str(email_id),
                "lead_id":        str(lead_id),
                "email_type":     email_type or "",
                "subject":        subject or "",
                "sent_date":      date_str,
                "sent_time":      time_str,
                "due_status":     due_status,
                "due_label":      due_label,
                "company":        company or "",
                "full_name":      full_name or "",
                "email":          email_addr or "",
                "track":          track or "",
                "track_css":      track_css(track or ""),
                "status":         lead_status or "",
                "status_css":     status_css,
                "status_display": status_display,
                "pill_label":     pill_label,
                "pill_css":       pill_css,
                "reply_received": bool(reply_received),
                "reply_text":     reply_text or "",
            })

        # Fetch full email threads for leads visible on this page (for slide panel)
        lead_ids = list({e["lead_id"] for e in sent_emails})
        emails_by_lead = {}
        if lead_ids:
            placeholders = ",".join("?" * len(lead_ids))
            email_cols = _get_email_columns(conn)
            thread_rows = conn.execute(
                f"SELECT * FROM outreach_emails WHERE lead_id IN ({placeholders}) "
                f"ORDER BY sent_at ASC",
                lead_ids,
            ).fetchall()
            for trow in thread_rows:
                e = enrich_email(trow, email_cols)
                lid = str(e.get("lead_id", ""))
                if lid not in emails_by_lead:
                    emails_by_lead[lid] = []
                emails_by_lead[lid].append(e)

        sent_emails_json = json.dumps(sent_emails)
        emails_json      = json.dumps(emails_by_lead)

    except Exception as ex:
        print(f"[OUTREACH] Error loading sent: {ex}")
        stats = {"total_sent": 0, "overdue": 0, "due_today": 0, "replied": 0, "closed": 0}
        sent_emails = []
        sent_emails_json = "[]"
        emails_json = "{}"
    finally:
        conn.close()

    return render_template(
        "outreach/sent.html",
        client_name=config.client_name,
        available_clients=clients,
        current_client_config=current_client_path,
        stats=stats,
        sent_emails=sent_emails,
        sent_emails_json=sent_emails_json,
        emails_json=emails_json,
    )


# ── POST /outreach/sent/<email_id>/queue-followup ─────────────────────────────
@bp.route("/sent/<email_id>/queue-followup", methods=["POST"])
@login_required
def sent_queue_followup(email_id):
    """Set followup_due to tomorrow; mark lead as followed_up. AJAX — CSRF exempt."""
    conn = get_outreach_db()
    try:
        row = conn.execute(
            "SELECT lead_id FROM outreach_emails WHERE email_id = ?", [email_id]
        ).fetchone()
        if not row:
            return jsonify({"success": False, "message": "Email not found"}), 404
        lead_id  = row[0]
        tomorrow = date.today() + timedelta(days=1)
        now      = datetime.now()
        conn.execute(
            "UPDATE outreach_emails SET followup_due = ? WHERE email_id = ?",
            [tomorrow, email_id],
        )
        conn.execute(
            "UPDATE outreach_leads SET status = 'followed_up', progress_stage = 4, "
            "last_activity = ? WHERE lead_id = ?",
            [now, lead_id],
        )
        return jsonify({"success": True})
    except Exception as e:
        print(f"[OUTREACH] sent queue-followup error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()


# ── POST /outreach/sent/<lead_id>/update-status ───────────────────────────────
@bp.route("/sent/<lead_id>/update-status", methods=["POST"])
@login_required
def sent_update_status(lead_id):
    """Update lead status from sent page. AJAX — CSRF exempt."""
    data = request.get_json(silent=True)
    if not data or "status" not in data:
        return jsonify({"success": False, "message": "Missing status field"}), 400
    new_status = str(data["status"]).strip().lower()
    if new_status not in _STATUS_STAGE:
        return jsonify({"success": False, "message": f"Invalid status: {new_status}"}), 400
    stage = _STATUS_STAGE[new_status]
    conn = get_outreach_db()
    try:
        conn.execute(
            "UPDATE outreach_leads SET status = ?, progress_stage = ?, "
            "last_activity = ? WHERE lead_id = ?",
            [new_status, stage, datetime.now(), lead_id],
        )
        return jsonify({"success": True})
    except Exception as e:
        print(f"[OUTREACH] sent update-status error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()


# ── POST /outreach/sent/<lead_id>/mark-won ────────────────────────────────────
@bp.route("/sent/<lead_id>/mark-won", methods=["POST"])
@login_required
def sent_mark_won(lead_id):
    """Mark lead as won from sent page. AJAX — CSRF exempt."""
    conn = get_outreach_db()
    try:
        conn.execute(
            "UPDATE outreach_leads SET status = 'won', progress_stage = 8, "
            "last_activity = ? WHERE lead_id = ?",
            [datetime.now(), lead_id],
        )
        return jsonify({"success": True})
    except Exception as e:
        print(f"[OUTREACH] sent mark-won error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()


# ── POST /outreach/sent/<lead_id>/mark-lost ───────────────────────────────────
@bp.route("/sent/<lead_id>/mark-lost", methods=["POST"])
@login_required
def sent_mark_lost(lead_id):
    """Mark lead as lost from sent page. AJAX — CSRF exempt."""
    conn = get_outreach_db()
    try:
        conn.execute(
            "UPDATE outreach_leads SET status = 'lost', progress_stage = 8, "
            "last_activity = ? WHERE lead_id = ?",
            [datetime.now(), lead_id],
        )
        return jsonify({"success": True})
    except Exception as e:
        print(f"[OUTREACH] sent mark-lost error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()


# ══════════════════════════════════════════════════════════════════════════════
# REPLIES PAGE — Chat 62
# ══════════════════════════════════════════════════════════════════════════════

def format_replied_at(replied_at):
    """Return ('5 Mar 2026', '8:30am') from a replied_at datetime."""
    if not replied_at:
        return ("—", "")
    if isinstance(replied_at, str):
        try:
            replied_at = datetime.fromisoformat(replied_at)
        except ValueError:
            return (str(replied_at), "")
    date_str = replied_at.strftime("%d %b %Y").lstrip("0")
    hour_24 = replied_at.hour
    hour_12 = hour_24 % 12 or 12
    ampm = "am" if hour_24 < 12 else "pm"
    minute = replied_at.strftime("%M")
    time_str = f"{hour_12}:{minute}{ampm}" if minute != "00" else f"{hour_12}{ampm}"
    return (date_str, time_str)


# ── GET /outreach/replies ─────────────────────────────────────────────────────
@bp.route("/replies")
@login_required
def replies():
    """Replies page — leads who have replied, with compose and status actions."""
    config  = get_current_config()
    clients = get_available_clients()
    current_client_path = session.get("current_client_config")

    conn = get_outreach_db()
    try:
        # Ensure reply_read column exists on outreach_emails
        conn.execute(
            "ALTER TABLE outreach_emails ADD COLUMN IF NOT EXISTS "
            "reply_read BOOLEAN DEFAULT false"
        )

        # ── Stats ────────────────────────────────────────────────────────────
        total_replies = conn.execute(
            "SELECT COUNT(*) FROM outreach_leads "
            "WHERE status IN ('replied', 'meeting', 'won')"
        ).fetchone()[0]

        unread_count = conn.execute(
            "SELECT COUNT(DISTINCT lead_id) FROM outreach_emails "
            "WHERE reply_received = true AND reply_read = false"
        ).fetchone()[0]

        meetings_count = conn.execute(
            "SELECT COUNT(*) FROM outreach_leads WHERE status = 'meeting'"
        ).fetchone()[0]

        awaiting_count = conn.execute(
            "SELECT COUNT(*) FROM outreach_leads WHERE status = 'replied'"
        ).fetchone()[0]

        won_count = conn.execute(
            "SELECT COUNT(*) FROM outreach_leads WHERE status = 'won'"
        ).fetchone()[0]

        stats = {
            "total_replies": total_replies,
            "unread":        unread_count,
            "meetings":      meetings_count,
            "awaiting":      awaiting_count,
            "won":           won_count,
        }

        # ── Replies list ─────────────────────────────────────────────────────
        rows = conn.execute("""
            WITH reply_email AS (
                SELECT lead_id, reply_text, reply_read
                FROM outreach_emails
                WHERE reply_received = true
            ),
            latest_sent AS (
                SELECT lead_id, email_type, sequence_step,
                       ROW_NUMBER() OVER (
                           PARTITION BY lead_id ORDER BY sent_at DESC
                       ) AS rn
                FROM outreach_emails
                WHERE status = 'sent'
            )
            SELECT
                l.lead_id, l.full_name, l.company, l.email,
                l.track, l.status,
                l.last_activity  AS replied_at,
                re.reply_text,
                re.reply_read,
                ls.email_type,
                ls.sequence_step
            FROM outreach_leads l
            LEFT JOIN reply_email re ON l.lead_id = re.lead_id
            LEFT JOIN latest_sent  ls ON l.lead_id = ls.lead_id AND ls.rn = 1
            WHERE l.status IN ('replied', 'meeting', 'won')
            ORDER BY l.last_activity DESC
        """).fetchall()

        cols = [
            "lead_id", "full_name", "company", "email",
            "track", "status",
            "replied_at",
            "reply_text", "reply_read",
            "email_type", "sequence_step",
        ]

        replies_list = []
        for row in rows:
            r = dict(zip(cols, row))
            r["track_css"]       = track_css(r.get("track") or "")
            r["status_display"]  = STATUS_DISPLAY.get(r.get("status", ""), "—")
            date_str, time_str   = format_replied_at(r.get("replied_at"))
            r["replied_date"]    = date_str
            r["replied_time"]    = time_str
            r["reply_read"]      = bool(r.get("reply_read"))
            r["unread"]          = not r["reply_read"]
            r["reply_text"]      = r.get("reply_text") or ""
            r["lead_id"]         = str(r["lead_id"])
            pill_label, pill_css = compute_email_type_pill(
                r.get("email_type"), r.get("sequence_step")
            )
            r["pill_label"] = pill_label
            r["pill_css"]   = pill_css
            replies_list.append(r)

        # ── Email threads per lead (for slide panel) ──────────────────────────
        lead_ids = list({r["lead_id"] for r in replies_list})
        emails_by_lead = {}
        if lead_ids:
            placeholders = ",".join("?" * len(lead_ids))
            email_cols   = _get_email_columns(conn)
            thread_rows  = conn.execute(
                f"SELECT * FROM outreach_emails WHERE lead_id IN ({placeholders}) "
                f"ORDER BY sent_at ASC",
                lead_ids,
            ).fetchall()
            for trow in thread_rows:
                e   = enrich_email(trow, email_cols)
                lid = str(e.get("lead_id", ""))
                if lid not in emails_by_lead:
                    emails_by_lead[lid] = []
                emails_by_lead[lid].append(e)

        # ── Chat 74: reply_id from email_replies (for Mark as Unread) ─────────
        reply_id_map = {}
        try:
            if lead_ids:
                placeholders2 = ",".join("?" * len(lead_ids))
                rr = conn.execute(
                    f"SELECT lead_id, id FROM email_replies "
                    f"WHERE lead_id IN ({placeholders2}) "
                    f"QUALIFY ROW_NUMBER() OVER "
                    f"(PARTITION BY lead_id ORDER BY received_at DESC NULLS LAST) = 1",
                    lead_ids,
                ).fetchall()
                reply_id_map = {str(row[0]): str(row[1]) for row in rr}
        except Exception:
            pass
        for r in replies_list:
            r["reply_id"] = reply_id_map.get(r["lead_id"], "")

        def reply_to_js(r):
            return {k: _safe_str(v) for k, v in r.items()}

        replies_json = json.dumps([reply_to_js(r) for r in replies_list])
        emails_json  = json.dumps(emails_by_lead)

    except Exception as ex:
        print(f"[OUTREACH] Error loading replies: {ex}")
        stats        = {"total_replies": 0, "unread": 0, "meetings": 0, "awaiting": 0, "won": 0}
        replies_list = []
        replies_json = "[]"
        emails_json  = "{}"
    finally:
        conn.close()

    return render_template(
        "outreach/replies.html",
        client_name=config.client_name,
        available_clients=clients,
        current_client_config=current_client_path,
        stats=stats,
        replies=replies_list,
        replies_json=replies_json,
        emails_json=emails_json,
    )


# ── IMAP helper (Chat 74) ─────────────────────────────────────────────────────
def get_imap_connection():
    """Open an authenticated IMAP connection to Gmail INBOX."""
    from act_dashboard.email_sender import load_email_config
    config = load_email_config()
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(config["smtp_username"], config["smtp_password"])
    mail.select("INBOX")
    return mail


# ── POST /outreach/replies/<lead_id>/mark-read ────────────────────────────────
@bp.route("/replies/<lead_id>/mark-read", methods=["POST"])
@login_required
def replies_mark_read(lead_id):
    """Mark all reply emails for a lead as read. AJAX — CSRF exempt."""
    conn = get_outreach_db()
    try:
        conn.execute(
            "UPDATE outreach_emails SET reply_read = true "
            "WHERE lead_id = ? AND reply_received = true",
            [lead_id],
        )
        # Chat 74: also mark as read in email_replies and sync to Gmail
        try:
            conn.execute(
                "UPDATE email_replies SET read = true WHERE lead_id = ?",
                [lead_id],
            )
            row = conn.execute(
                "SELECT gmail_message_uid FROM email_replies "
                "WHERE lead_id = ? AND gmail_message_uid IS NOT NULL LIMIT 1",
                [lead_id],
            ).fetchone()
            if row and row[0]:
                uid = row[0]
                try:
                    mail = get_imap_connection()
                    mail.uid("STORE", uid.encode(), "+FLAGS", "\\Seen")
                    mail.logout()
                    print(f"[POLLER] Marked as read in Gmail: uid={uid}")
                except Exception as imap_err:
                    print(f"[POLLER] WARNING: IMAP mark-read failed: {imap_err}")
        except Exception as e2:
            print(f"[OUTREACH] WARNING: email_replies mark-read sync error: {e2}")
        return jsonify({"success": True})
    except Exception as e:
        print(f"[OUTREACH] replies mark-read error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()


# ── POST /outreach/replies/<reply_id>/mark-unread ─────────────────────────────
@bp.route("/replies/<reply_id>/mark-unread", methods=["POST"])
@login_required
def replies_mark_unread(reply_id):
    """Mark an individual reply as unread in DB and Gmail. AJAX — CSRF exempt."""
    conn = get_outreach_db()
    try:
        row = conn.execute(
            "SELECT gmail_message_uid FROM email_replies WHERE id = ?",
            [reply_id],
        ).fetchone()
        conn.execute(
            "UPDATE email_replies SET read = false WHERE id = ?",
            [reply_id],
        )
        if row and row[0]:
            uid = row[0]
            try:
                mail = get_imap_connection()
                mail.uid("STORE", uid.encode(), "-FLAGS", "\\Seen")
                mail.logout()
                print(f"[POLLER] Marked as unread in Gmail: uid={uid}")
            except Exception as imap_err:
                print(f"[POLLER] WARNING: IMAP mark-unread failed: {imap_err}")
        return jsonify({"success": True})
    except Exception as e:
        print(f"[OUTREACH] replies mark-unread error: {e}")
        return jsonify({"success": True})  # DB update may have succeeded
    finally:
        conn.close()


# ── POST /outreach/replies/<lead_id>/mark-won ─────────────────────────────────
@bp.route("/replies/<lead_id>/mark-won", methods=["POST"])
@login_required
def replies_mark_won(lead_id):
    """Mark lead as won from replies page. AJAX — CSRF exempt."""
    conn = get_outreach_db()
    try:
        conn.execute(
            "UPDATE outreach_leads SET status = 'won', progress_stage = 8, "
            "last_activity = ? WHERE lead_id = ?",
            [datetime.now(), lead_id],
        )
        return jsonify({"success": True})
    except Exception as e:
        print(f"[OUTREACH] replies mark-won error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()


# ── POST /outreach/replies/<lead_id>/mark-lost ────────────────────────────────
@bp.route("/replies/<lead_id>/mark-lost", methods=["POST"])
@login_required
def replies_mark_lost(lead_id):
    """Mark lead as lost from replies page. AJAX — CSRF exempt."""
    conn = get_outreach_db()
    try:
        conn.execute(
            "UPDATE outreach_leads SET status = 'lost', progress_stage = 8, "
            "last_activity = ? WHERE lead_id = ?",
            [datetime.now(), lead_id],
        )
        return jsonify({"success": True})
    except Exception as e:
        print(f"[OUTREACH] replies mark-lost error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()


# ── POST /outreach/replies/<lead_id>/book-meeting ─────────────────────────────
@bp.route("/replies/<lead_id>/book-meeting", methods=["POST"])
@login_required
def replies_book_meeting(lead_id):
    """Mark lead as meeting from replies page. AJAX — CSRF exempt."""
    conn = get_outreach_db()
    try:
        conn.execute(
            "UPDATE outreach_leads SET status = 'meeting', progress_stage = 7, "
            "last_activity = ? WHERE lead_id = ?",
            [datetime.now(), lead_id],
        )
        return jsonify({"success": True})
    except Exception as e:
        print(f"[OUTREACH] replies book-meeting error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()


# ── POST /outreach/replies/<lead_id>/send-reply ───────────────────────────────
@bp.route("/replies/<lead_id>/send-reply", methods=["POST"])
@login_required
def replies_send_reply(lead_id):
    """Send a reply email to a lead and record it. AJAX — CSRF exempt. Chat 72."""
    import re as _re
    from act_dashboard.email_sender import send_email, get_signature_html, substitute_variables

    data = request.get_json(silent=True) or {}
    body_text = (data.get("body") or "").strip()
    if not body_text:
        return jsonify({"success": False, "error": "Reply body is required"}), 400

    conn = get_outreach_db()
    try:
        # Fetch lead info
        lead_row = conn.execute(
            "SELECT lead_id, email, full_name, first_name, company "
            "FROM outreach_leads WHERE lead_id = ?",
            [lead_id],
        ).fetchone()
        if not lead_row:
            return jsonify({"success": False, "error": "Lead not found"}), 404

        _, to_email, full_name, first_name, company = lead_row

        # Get subject from latest sent email for this lead
        subj_row = conn.execute(
            "SELECT subject FROM outreach_emails "
            "WHERE lead_id = ? AND status = 'sent' "
            "ORDER BY sent_at DESC LIMIT 1",
            [lead_id],
        ).fetchone()
        orig_subject = subj_row[0] if subj_row else ""

        # Build subject: strip any Re:/RE:/re: prefix, prepend single Re:
        clean_subject = _re.sub(r"^(re:\s*)+", "", orig_subject, flags=_re.IGNORECASE).strip()
        subject = f"Re: {clean_subject}"

        # Substitute template variables in body
        lead_data = {
            "full_name":  full_name or "",
            "first_name": first_name or (full_name.split()[0] if full_name else ""),
            "company":    company or "",
        }
        body_text = substitute_variables(body_text, lead_data)

        # Convert plain-text body to HTML and append signature
        body_html = (
            "<div style='font-family:Arial,sans-serif;font-size:14px;"
            "line-height:1.6;color:#333;'>"
            + body_text.replace("\n", "<br>")
            + "</div>"
            + get_signature_html()
        )

        print(f"[OUTREACH] send-reply: lead_id={lead_id} to={to_email} subject='{subject[:60]}'")

        # Send via Gmail SMTP — no CV attachment on replies
        result = send_email(to_email=to_email, subject=subject, body_html=body_html)
        if not result["success"]:
            return jsonify({"success": False, "error": result.get("error", "Send failed")}), 500

        # Record outbound reply in outreach_emails
        new_email_id = str(uuid.uuid4())
        conn.execute(
            """INSERT INTO outreach_emails
               (email_id, lead_id, email_type, subject, body, status, direction, sent_at, created_at)
               VALUES (?, ?, 'outbound_reply', ?, ?, 'sent', 'outbound_reply', now(), now())""",
            [new_email_id, lead_id, subject, body_text],
        )

        # Update lead status to in_conversation
        conn.execute(
            "UPDATE outreach_leads SET status = 'in_conversation', last_activity = now() "
            "WHERE lead_id = ?",
            [lead_id],
        )

        return jsonify({"success": True})

    except Exception as e:
        print(f"[OUTREACH] replies send-reply error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        conn.close()


# ══════════════════════════════════════════════════════════════════════════════
# TEMPLATES PAGE — Chat 63
# ══════════════════════════════════════════════════════════════════════════════

# ── GET /outreach/templates ───────────────────────────────────────────────────
@bp.route("/templates", methods=["GET"])
@login_required
def templates():
    """Outreach Templates page — view and edit email templates."""
    import re as _re

    config              = get_current_config()
    clients             = get_available_clients()
    current_client_path = session.get("current_client_config")

    conn = get_outreach_db()
    try:
        tmpl_rows = conn.execute(
            """SELECT template_id, name, email_type, sequence_step, subject, body,
                      send_delay_days, cv_attached_default
               FROM outreach_templates
               ORDER BY sequence_step ASC"""
        ).fetchall()

        tmpl_cols = [
            "template_id", "name", "email_type", "sequence_step",
            "subject", "body", "send_delay_days", "cv_attached_default",
        ]

        # Per-email-type stats from outreach_emails
        stats_rows = conn.execute(
            """SELECT email_type,
                      COUNT(*) FILTER (WHERE status = 'sent')          AS times_sent,
                      COUNT(*) FILTER (WHERE reply_received = true)    AS replies
               FROM outreach_emails
               GROUP BY email_type"""
        ).fetchall()
        stats = {r[0]: {"times_sent": r[1], "replies": r[2]} for r in stats_rows}

        templates_list = []
        cumulative_day = 1
        for row in tmpl_rows:
            t     = dict(zip(tmpl_cols, row))
            et    = t["email_type"]
            s     = stats.get(et, {"times_sent": 0, "replies": 0})
            sent  = s["times_sent"]
            reps  = s["replies"]

            t["times_sent"] = sent
            t["replies"]    = reps
            t["reply_rate"] = round(reps / sent * 100) if sent > 0 else 0

            # Cumulative day label for sequence flow
            delay = t["send_delay_days"] or 0
            if t["sequence_step"] == 1:
                cumulative_day = 1
            else:
                cumulative_day += delay
            t["day_label"] = f"Day {cumulative_day}"

            # Pill label and class
            step = t["sequence_step"]
            if step == 1:
                t["pill_label"] = "Step 1"
                t["pill_class"] = "pill-initial"
            else:
                t["pill_label"] = f"Step {step} · +{delay} days"
                t["pill_class"] = "pill-followup"

            # CV toggle display
            t["cv_label"] = (
                "CV attached by default" if t["cv_attached_default"]
                else "No CV by default"
            )
            t["cv_class"] = "attach-on" if t["cv_attached_default"] else "attach-off"

            # Detect template variables (preserve insertion order, deduplicate)
            t["variables"] = list(
                dict.fromkeys(_re.findall(r"\{\{(\w+)\}\}", t["body"] or ""))
            )

            templates_list.append(t)

        return render_template(
            "outreach/templates.html",
            templates=templates_list,
            page_title="Outreach — Templates",
            available_clients=clients,
            current_client_config=current_client_path,
        )
    except Exception as e:
        print(f"[OUTREACH TEMPLATES] Error loading templates: {e}")
        return render_template(
            "outreach/templates.html",
            templates=[],
            page_title="Outreach — Templates",
            available_clients=clients if "clients" in dir() else [],
            current_client_config=current_client_path if "current_client_path" in dir() else None,
        )
    finally:
        conn.close()


# ── POST /outreach/templates/<template_id>/update ─────────────────────────────
@bp.route("/templates/<template_id>/update", methods=["POST"])
@login_required
def templates_update(template_id):
    """Update template fields. AJAX JSON — CSRF exempt."""
    data = request.get_json() or {}
    conn = get_outreach_db()
    try:
        cv_attached = str(data.get("cv_attached", "no")).lower() == "yes"
        delay_days  = int(data.get("send_delay_days", 0) or 0)
        conn.execute(
            """UPDATE outreach_templates
               SET name                = ?,
                   subject             = ?,
                   body                = ?,
                   cv_attached_default = ?,
                   send_delay_days     = ?,
                   updated_at          = ?
               WHERE template_id = ?""",
            [
                data.get("name"), data.get("subject"), data.get("body"),
                cv_attached, delay_days, datetime.now(), template_id,
            ],
        )
        return jsonify({"success": True})
    except Exception as e:
        print(f"[OUTREACH TEMPLATES] Update error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()


# ── POST /outreach/templates/<template_id>/duplicate ──────────────────────────
@bp.route("/templates/<template_id>/duplicate", methods=["POST"])
@login_required
def templates_duplicate(template_id):
    """Placeholder: duplicate template. AJAX — CSRF exempt."""
    return jsonify({"success": True, "message": "Duplicate coming soon"})


# ── GET /outreach/analytics ────────────────────────────────────────────────────
@bp.route("/analytics")
@login_required
def analytics():
    """Analytics dashboard for the outreach system — Chat 64."""
    days = request.args.get("days", 30, type=int)
    if days not in (7, 14, 30, 90):
        days = 30

    conn = get_outreach_db()
    try:
        clients = get_available_clients()
        current_client_path = session.get("current_client_config")

        cutoff = datetime.now() - timedelta(days=days)
        prev_cutoff = datetime.now() - timedelta(days=days * 2)

        # ── KPI: core counts (current period) ─────────────────────────────────
        # opened_at/clicked_at/cv_opened_at are never populated; use *_count columns
        row = conn.execute("""
            SELECT
                COUNT(*) FILTER (WHERE status = 'sent')                            AS total_sent,
                COUNT(*) FILTER (WHERE status = 'sent' AND open_count > 0)         AS total_opened,
                COUNT(*) FILTER (WHERE status = 'sent' AND click_count > 0)        AS links_clicked,
                COUNT(*) FILTER (WHERE status = 'sent' AND cv_open_count > 0)      AS cv_opens
            FROM outreach_emails
            WHERE sent_at >= ?
        """, [cutoff]).fetchone()

        total_sent    = row[0] or 0
        total_opened  = row[1] or 0
        links_clicked = row[2] or 0
        cv_opens      = row[3] or 0

        open_rate     = round(total_opened  / total_sent * 100, 1) if total_sent else 0
        click_rate    = round(links_clicked / total_sent * 100, 1) if total_sent else 0
        cv_open_rate  = round(cv_opens      / total_sent * 100, 1) if total_sent else 0

        # ── KPI: replies & meetings (leads who had emails sent in period) ──────
        total_replies = conn.execute("""
            SELECT COUNT(DISTINCT l.lead_id)
            FROM outreach_leads l
            JOIN outreach_emails e ON l.lead_id = e.lead_id
            WHERE e.status = 'sent' AND e.sent_at >= ?
              AND l.status IN ('replied', 'meeting', 'won')
        """, [cutoff]).fetchone()[0] or 0

        meetings_booked = conn.execute("""
            SELECT COUNT(DISTINCT l.lead_id)
            FROM outreach_leads l
            JOIN outreach_emails e ON l.lead_id = e.lead_id
            WHERE e.status = 'sent' AND e.sent_at >= ?
              AND l.status = 'meeting'
        """, [cutoff]).fetchone()[0] or 0

        reply_rate = round(total_replies / total_sent * 100, 1) if total_sent else 0

        # ── KPI: warm leads (opened but no reply) ─────────────────────────────
        opened_no_reply = conn.execute("""
            SELECT COUNT(DISTINCT l.lead_id)
            FROM outreach_leads l
            JOIN outreach_emails e ON l.lead_id = e.lead_id
            WHERE e.sent_at >= ?
              AND e.open_count > 0
              AND l.status NOT IN ('replied', 'meeting', 'won', 'lost')
        """, [cutoff]).fetchone()[0] or 0

        # ── KPI: avg days to reply ─────────────────────────────────────────────
        avg_row = conn.execute("""
            SELECT ROUND(AVG(DATEDIFF('day', e.min_sent, l.last_activity)), 1)
            FROM outreach_leads l
            JOIN (
                SELECT lead_id, MIN(sent_at) AS min_sent
                FROM outreach_emails
                WHERE status = 'sent' AND sent_at >= ?
                GROUP BY lead_id
            ) e ON l.lead_id = e.lead_id
            WHERE l.status IN ('replied', 'meeting', 'won')
              AND l.last_activity IS NOT NULL
        """, [cutoff]).fetchone()
        avg_days_to_reply = float(avg_row[0]) if avg_row and avg_row[0] is not None else 0.0

        # ── KPI: prev period (for delta) ───────────────────────────────────────
        prev_row = conn.execute("""
            SELECT COUNT(*) FILTER (WHERE status = 'sent') AS prev_sent
            FROM outreach_emails
            WHERE sent_at >= ? AND sent_at < ?
        """, [prev_cutoff, cutoff]).fetchone()
        prev_sent = prev_row[0] or 0

        prev_meetings = conn.execute("""
            SELECT COUNT(DISTINCT l.lead_id)
            FROM outreach_leads l
            JOIN outreach_emails e ON l.lead_id = e.lead_id
            WHERE e.status = 'sent' AND e.sent_at >= ? AND e.sent_at < ?
              AND l.status = 'meeting'
        """, [prev_cutoff, cutoff]).fetchone()[0] or 0

        prev_days_row = conn.execute("""
            SELECT ROUND(AVG(DATEDIFF('day', e.min_sent, l.last_activity)), 1)
            FROM outreach_leads l
            JOIN (
                SELECT lead_id, MIN(sent_at) AS min_sent
                FROM outreach_emails
                WHERE status = 'sent' AND sent_at >= ? AND sent_at < ?
                GROUP BY lead_id
            ) e ON l.lead_id = e.lead_id
            WHERE l.status IN ('replied', 'meeting', 'won')
              AND l.last_activity IS NOT NULL
        """, [prev_cutoff, cutoff]).fetchone()
        prev_avg_days = float(prev_days_row[0]) if prev_days_row and prev_days_row[0] is not None else 0.0

        # ── Engagement funnel ──────────────────────────────────────────────────
        leads_total = conn.execute("SELECT COUNT(*) FROM outreach_leads").fetchone()[0] or 0

        # ── Daily activity chart ───────────────────────────────────────────────
        daily_rows = conn.execute("""
            SELECT
                CAST(sent_at AS DATE) AS day,
                COUNT(*) FILTER (WHERE status = 'sent')                        AS sent,
                COUNT(*) FILTER (WHERE status = 'sent' AND open_count > 0)     AS opened,
                COUNT(*) FILTER (WHERE status = 'sent' AND click_count > 0)    AS clicked,
                COUNT(*) FILTER (WHERE reply_received = true)                  AS replied
            FROM outreach_emails
            WHERE sent_at >= ?
            GROUP BY CAST(sent_at AS DATE)
            ORDER BY day
        """, [cutoff]).fetchall()

        from datetime import date as date_cls
        date_range = [cutoff.date() + timedelta(days=i) for i in range(days + 1)
                      if cutoff.date() + timedelta(days=i) <= date_cls.today()]
        daily_dict = {row[0]: row for row in daily_rows}
        daily_labels  = [f"{d.day} {d.strftime('%b')}" for d in date_range]
        daily_sent_arr    = [daily_dict.get(d, (None, 0, 0, 0, 0))[1] for d in date_range]
        daily_opened_arr  = [daily_dict.get(d, (None, 0, 0, 0, 0))[2] for d in date_range]
        daily_clicked_arr = [daily_dict.get(d, (None, 0, 0, 0, 0))[3] for d in date_range]
        daily_replied_arr = [daily_dict.get(d, (None, 0, 0, 0, 0))[4] for d in date_range]

        # ── Reply/open/click rate by day of week ───────────────────────────────
        # isodow: 1=Mon, 2=Tue, ..., 7=Sun
        dow_rows = conn.execute("""
            SELECT
                date_part('isodow', sent_at) AS dow,
                COUNT(*) AS total,
                COUNT(*) FILTER (WHERE open_count > 0)      AS opened,
                COUNT(*) FILTER (WHERE click_count > 0)     AS clicked,
                COUNT(*) FILTER (WHERE reply_received = true) AS replied
            FROM outreach_emails
            WHERE status = 'sent' AND sent_at >= ?
            GROUP BY dow
            ORDER BY dow
        """, [cutoff]).fetchall()

        dow_map = {int(r[0]): r for r in dow_rows}
        dow_open_pct  = []
        dow_click_pct = []
        dow_reply_pct = []
        for d in range(1, 8):
            r = dow_map.get(d)
            if r and r[1] > 0:
                dow_open_pct.append(round(r[2] / r[1] * 100))
                dow_click_pct.append(round(r[3] / r[1] * 100))
                dow_reply_pct.append(round(r[4] / r[1] * 100))
            else:
                dow_open_pct.append(0)
                dow_click_pct.append(0)
                dow_reply_pct.append(0)

        # ── Emails sent by DOW ─────────────────────────────────────────────────
        dow_sent_rows = conn.execute("""
            SELECT date_part('isodow', sent_at) AS dow, COUNT(*) AS cnt
            FROM outreach_emails
            WHERE status = 'sent' AND sent_at >= ?
            GROUP BY dow
            ORDER BY dow
        """, [cutoff]).fetchall()
        dow_sent_map = {int(r[0]): r[1] for r in dow_sent_rows}
        dow_sent_arr = [dow_sent_map.get(d, 0) for d in range(1, 8)]

        # ── Performance by track ───────────────────────────────────────────────
        track_rows_raw = conn.execute("""
            SELECT
                l.track,
                COUNT(e.email_id)                                                 AS sent,
                COUNT(*) FILTER (WHERE e.open_count > 0)                          AS opened,
                COUNT(*) FILTER (WHERE e.click_count > 0)                         AS clicked,
                COUNT(*) FILTER (WHERE e.cv_open_count > 0)                       AS cv_opens,
                COUNT(*) FILTER (WHERE e.reply_received = true)                   AS replied,
                COUNT(DISTINCT CASE WHEN l.status = 'meeting' THEN l.lead_id END) AS meetings
            FROM outreach_emails e
            JOIN outreach_leads l ON e.lead_id = l.lead_id
            WHERE e.status = 'sent' AND e.sent_at >= ?
            GROUP BY l.track
            ORDER BY sent DESC
        """, [cutoff]).fetchall()

        def pct(n, d):
            return round(n / d * 100) if d else 0

        track_rows = []
        for r in track_rows_raw:
            s = r[1] or 0
            track_rows.append({
                "name":        r[0] or "Unknown",
                "sent":        s,
                "opened":      r[2] or 0, "open_pct":    pct(r[2], s),
                "clicked":     r[3] or 0, "click_pct":   pct(r[3], s),
                "cv_opens":    r[4] or 0, "cv_pct":      pct(r[4], s),
                "replied":     r[5] or 0, "reply_pct":   pct(r[5], s),
                "meetings":    r[6] or 0, "meeting_pct": pct(r[6], s),
            })

        # ── Performance by template step ───────────────────────────────────────
        STEP_META = {
            "initial":     ("Step 1", "Initial"),
            "follow_up_1": ("Step 2", "Follow-up 1"),
            "follow_up_2": ("Step 3", "Follow-up 2"),
            "follow_up_3": ("Step 4", "Follow-up 3"),
        }
        STEP_ORDER = ["initial", "follow_up_1", "follow_up_2", "follow_up_3"]

        step_rows_raw = conn.execute("""
            SELECT
                e.email_type,
                COUNT(*)                                            AS sent,
                COUNT(*) FILTER (WHERE e.open_count > 0)           AS opened,
                COUNT(*) FILTER (WHERE e.click_count > 0)          AS clicked,
                COUNT(*) FILTER (WHERE e.cv_open_count > 0)        AS cv_opens,
                COUNT(*) FILTER (WHERE e.reply_received = true)    AS replied
            FROM outreach_emails e
            WHERE e.status = 'sent' AND e.sent_at >= ?
            GROUP BY e.email_type
        """, [cutoff]).fetchall()

        step_dict = {r[0]: r for r in step_rows_raw}
        step_rows = []
        for etype in STEP_ORDER:
            r = step_dict.get(etype)
            if r is None:
                continue
            s = r[1] or 0
            label, name = STEP_META.get(etype, ("?", etype))
            step_rows.append({
                "label":    label,
                "name":     name,
                "sent":     s,
                "opened":   r[2] or 0, "open_pct":  pct(r[2], s),
                "clicked":  r[3] or 0, "click_pct": pct(r[3], s),
                "cv_opens": r[4] or 0, "cv_pct":    pct(r[4], s),
                "replied":  r[5] or 0, "reply_pct": pct(r[5], s),
            })

        # ── Status distribution donut ──────────────────────────────────────────
        STATUS_ORDER = ["cold", "queued", "contacted", "followed_up",
                        "replied", "meeting", "won", "lost", "no_reply"]
        STATUS_LABEL = {
            "cold": "Not contacted", "queued": "Queued",
            "contacted": "Contacted", "followed_up": "Followed up",
            "replied": "Replied", "meeting": "Meeting booked",
            "won": "Won", "lost": "Lost", "no_reply": "No reply",
        }
        status_raw = conn.execute("""
            SELECT status, COUNT(*) AS cnt FROM outreach_leads
            GROUP BY status ORDER BY cnt DESC
        """).fetchall()
        status_map = {r[0]: r[1] for r in status_raw}
        status_labels = [STATUS_LABEL.get(s, s) for s in STATUS_ORDER if s in status_map]
        status_values = [status_map[s] for s in STATUS_ORDER if s in status_map]

        # ── Link clicks breakdown donut ────────────────────────────────────────
        cv_click_count  = cv_opens  # emails where cv_open_count > 0
        web_click_count = conn.execute("""
            SELECT COUNT(*) FROM outreach_emails
            WHERE status = 'sent' AND sent_at >= ?
              AND click_count > 0 AND cv_open_count = 0
        """, [cutoff]).fetchone()[0] or 0
        click_labels = ["CV opened", "Website / other link"]
        click_values = [cv_click_count, web_click_count]

        # ── Pack data dict ─────────────────────────────────────────────────────
        data = {
            # KPI
            "total_sent":       total_sent,
            "total_opened":     total_opened,
            "open_rate":        open_rate,
            "links_clicked":    links_clicked,
            "click_rate":       click_rate,
            "cv_opens":         cv_opens,
            "cv_open_rate":     cv_open_rate,
            "total_replies":    total_replies,
            "reply_rate":       reply_rate,
            "meetings_booked":  meetings_booked,
            "opened_no_reply":  opened_no_reply,
            "avg_days_to_reply": avg_days_to_reply,
            # prev period
            "prev_sent":     prev_sent,
            "prev_meetings": prev_meetings,
            "prev_avg_days": prev_avg_days,
            # funnel
            "leads_total": leads_total,
            # daily activity chart
            "daily_labels":  daily_labels,
            "daily_sent":    daily_sent_arr,
            "daily_opened":  daily_opened_arr,
            "daily_clicked": daily_clicked_arr,
            "daily_replied": daily_replied_arr,
            # DOW reply/open/click rate
            "dow_open_pct":  dow_open_pct,
            "dow_click_pct": dow_click_pct,
            "dow_reply_pct": dow_reply_pct,
            # DOW sent
            "dow_sent": dow_sent_arr,
            # track table
            "tracks": track_rows,
            # step table
            "steps": step_rows,
            # status donut
            "status_labels": status_labels,
            "status_values": status_values,
            # click breakdown
            "click_labels": click_labels,
            "click_values": click_values,
        }

        return render_template(
            "outreach/analytics.html",
            data=data,
            days=days,
            page_title="Outreach — Analytics",
            available_clients=clients,
            current_client_config=current_client_path,
        )

    except Exception as exc:
        import traceback
        print(f"[OUTREACH ANALYTICS] Error: {exc}")
        traceback.print_exc()
        return render_template(
            "outreach/analytics.html",
            data={},
            days=days,
            page_title="Outreach — Analytics",
            available_clients=[],
            current_client_config=None,
        )
    finally:
        conn.close()


# ── Sync leads from Google Sheets ────────────────────────────────────────────
_SHEET_ID   = "1zRTPuzwvHDSq23RqJ9iiRaNZ8bSOMmndUzxiP_DW38I"
_CREDS_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "secrets", "google-credentials.json")
)


@bp.route("/sync-from-sheets", methods=["POST"])
@login_required
def sync_from_sheets():
    """Pull rows with Status='new' from Google Sheet and insert into outreach_leads."""
    try:
        import gspread
        from google.oauth2.service_account import Credentials as GCredentials

        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds  = GCredentials.from_service_account_file(_CREDS_PATH, scopes=scopes)
        gc     = gspread.authorize(creds)
        sheet  = gc.open_by_key(_SHEET_ID).sheet1

        rows = sheet.get_all_values()  # includes header row
    except FileNotFoundError:
        return jsonify({"success": False, "message": "google-credentials.json not found"}), 500
    except Exception as exc:
        return jsonify({"success": False, "message": f"Sheets error: {exc}"}), 500

    if len(rows) < 2:
        return jsonify({"success": True, "imported": 0, "skipped": 0})

    # Sheet columns: Timestamp(0) Name(1) Email(2) Company(3) Role(4)
    #                LookingFor(5) Phone(6) IPAddress(7) UserAgent(8) Status(9)
    imported = 0
    skipped  = 0

    conn = get_outreach_db()
    try:
        for row_num, row in enumerate(rows[1:], start=2):  # skip header; row_num is 1-indexed sheet row
            # Pad short rows
            while len(row) < 10:
                row.append("")

            status = row[9].strip().lower()
            if status != "new":
                continue

            email   = row[2].strip()
            name    = row[1].strip()
            company = row[3].strip()
            phone   = row[6].strip()

            if not email:
                skipped += 1
                continue

            # Deduplication check against outreach_leads
            exists = conn.execute(
                "SELECT 1 FROM outreach_leads WHERE email = ?", [email]
            ).fetchone()

            if exists:
                skipped += 1
                # Mark as imported in sheet so we don't check it again
                sheet.update_cell(row_num, 10, "imported")
                continue

            # Parse name into parts
            parts      = name.split(" ", 1)
            first_name = parts[0] if parts else ""
            last_name  = parts[1] if len(parts) > 1 else ""
            notes      = f"Phone: {phone}" if phone else ""

            conn.execute(
                """
                INSERT INTO outreach_leads
                    (lead_id, first_name, last_name, full_name, company, role, email,
                     linkedin_url, website, city_state, country, timezone,
                     track, source, lead_type_score, status, progress_stage,
                     notes, added_date, last_activity, sequence_step, do_not_contact)
                VALUES (?, ?, ?, ?, ?, '', ?, '', '', '', '', 'GMT',
                        'Direct', 'website', 3, 'cold', 1,
                        ?, ?, ?, 0, false)
                """,
                [str(uuid.uuid4()), first_name, last_name, name, company or "", email,
                 notes, date.today(), datetime.now()],
            )
            imported += 1

            # Mark row as imported in sheet
            sheet.update_cell(row_num, 10, "imported")

    finally:
        conn.close()

    return jsonify({"success": True, "imported": imported, "skipped": skipped})
