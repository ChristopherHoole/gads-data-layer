"""
act_dashboard/routes/outreach.py

Outreach system blueprint — Chat 59.
Routes:
  GET  /outreach/leads                   — Leads page
  PATCH /outreach/leads/<lead_id>/notes  — Save notes (AJAX)
  POST  /outreach/leads/add              — Add new lead (AJAX)
"""

import json
import os
import uuid
from datetime import datetime, date

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
    "cold":        "Cold",
    "queued":      "Queued",
    "contacted":   "Contacted",
    "followed_up": "Followed Up",
    "replied":     "Replied",
    "meeting":     "Meeting",
    "won":         "Won",
    "lost":        "Lost",
    "no_reply":    "No Reply",
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
