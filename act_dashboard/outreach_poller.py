"""
act_dashboard/outreach_poller.py

IMAP polling daemon — Chat 74.
Polls chris@christopherhoole.com inbox every 120 seconds, imports
unmatched inbound replies into email_replies, and syncs lead status.
"""

import email
import imaplib
import re
import threading
import uuid
from datetime import datetime
from email.header import decode_header
from pathlib import Path

import duckdb
import yaml


# ── DB path ───────────────────────────────────────────────────────────────────
_WAREHOUSE_PATH = str(
    (Path(__file__).parent.parent / "warehouse.duckdb").resolve()
)


def _load_email_config():
    config_path = Path(__file__).parent / "secrets" / "email_config.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def _get_db():
    return duckdb.connect(_WAREHOUSE_PATH)


# ── Schema migration ──────────────────────────────────────────────────────────

def _ensure_schema():
    """Add required columns if missing."""
    conn = _get_db()
    try:
        conn.execute(
            "ALTER TABLE email_replies ADD COLUMN IF NOT EXISTS message_id VARCHAR"
        )
        conn.execute(
            "ALTER TABLE email_replies ADD COLUMN IF NOT EXISTS gmail_message_uid VARCHAR"
        )
        conn.execute(
            "ALTER TABLE outreach_emails ADD COLUMN IF NOT EXISTS replied_at TIMESTAMP"
        )
        print("[POLLER] Schema migration complete (message_id, gmail_message_uid, replied_at)")
    except Exception as e:
        print(f"[POLLER] WARNING: Schema migration failed: {e}")
    finally:
        conn.close()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _decode_str(raw):
    """Decode an encoded email header value to a plain string."""
    if raw is None:
        return ""
    parts = decode_header(raw)
    result = []
    for part, charset in parts:
        if isinstance(part, bytes):
            try:
                result.append(part.decode(charset or "utf-8", errors="replace"))
            except LookupError:
                result.append(part.decode("utf-8", errors="replace"))
        else:
            result.append(part)
    return "".join(result)


def _strip_re_prefixes(subject):
    """Recursively strip Re:, Fwd:, Re: Re: etc. from the start of a subject."""
    pattern = re.compile(r"^\s*(re|fwd|fw)\s*:\s*", re.IGNORECASE)
    while True:
        stripped = pattern.sub("", subject).strip()
        if stripped == subject.strip():
            break
        subject = stripped
    return stripped


def _get_plain_body(msg):
    """Extract plain-text body from an email.message.Message, HTML fallback."""
    plain = None
    html = None
    if msg.is_multipart():
        for part in msg.walk():
            ct = part.get_content_type()
            disp = str(part.get("Content-Disposition") or "")
            if "attachment" in disp:
                continue
            if ct == "text/plain" and plain is None:
                try:
                    plain = part.get_payload(decode=True).decode(
                        part.get_content_charset() or "utf-8", errors="replace"
                    )
                except Exception:
                    pass
            elif ct == "text/html" and html is None:
                try:
                    html = part.get_payload(decode=True).decode(
                        part.get_content_charset() or "utf-8", errors="replace"
                    )
                except Exception:
                    pass
    else:
        try:
            payload = msg.get_payload(decode=True)
            if payload:
                charset = msg.get_content_charset() or "utf-8"
                plain = payload.decode(charset, errors="replace")
        except Exception:
            pass
    return plain or html or ""


# ── Poll cycle ────────────────────────────────────────────────────────────────

def _run_poll_cycle():
    config = _load_email_config()
    username = config["smtp_username"]
    password = config["smtp_password"]

    mail = None
    conn = None
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(username, password)
        mail.select("INBOX")

        # Search for all unseen messages
        status, data = mail.uid("SEARCH", None, "UNSEEN")
        if status != "OK":
            return 0

        uid_list = data[0].split() if data[0] else []
        imported = 0

        conn = _get_db()
        for uid_bytes in uid_list:
            uid_str = uid_bytes.decode("utf-8")

            try:
                # Fetch full message
                status, msg_data = mail.uid("FETCH", uid_bytes, "(RFC822)")
                if status != "OK" or not msg_data or not msg_data[0]:
                    continue

                raw = msg_data[0][1]
                msg = email.message_from_bytes(raw)

                message_id = _decode_str(msg.get("Message-ID", "")).strip()
                subject_raw = _decode_str(msg.get("Subject", "")).strip()
                from_raw = _decode_str(msg.get("From", "")).strip()
                date_raw = msg.get("Date", "")

                # Parse from_email and from_name
                match = re.match(r"^(.*?)\s*<(.+?)>\s*$", from_raw)
                if match:
                    from_name  = match.group(1).strip().strip('"')
                    from_email = match.group(2).strip()
                else:
                    from_name  = ""
                    from_email = from_raw

                # Parse received_at
                try:
                    received_at = email.utils.parsedate_to_datetime(date_raw)
                except Exception:
                    received_at = datetime.now()

                # Skip emails with no Message-ID — can't deduplicate safely
                if not message_id:
                    print(f"[POLLER] Skipping email with no Message-ID (uid={uid_str})")
                    continue

                # Deduplication: skip if message_id already imported
                existing = conn.execute(
                    "SELECT id FROM email_replies WHERE message_id = ?",
                    [message_id],
                ).fetchone()
                if existing:
                    continue

                # Strip Re:/Fwd: prefixes and match against outreach_emails
                clean_subject = _strip_re_prefixes(subject_raw)

                matched = conn.execute(
                    "SELECT email_id, lead_id FROM outreach_emails "
                    "WHERE LOWER(subject) = LOWER(?) AND status = 'sent' "
                    "LIMIT 1",
                    [clean_subject],
                ).fetchone()

                if not matched:
                    print(f'[POLLER] Unmatched reply subject: "{clean_subject}" — skipped')
                    continue

                email_id, lead_id = matched
                body = _get_plain_body(msg)

                # Insert into email_replies
                reply_id = str(uuid.uuid4())
                conn.execute(
                    """
                    INSERT INTO email_replies
                        (id, lead_id, from_email, from_name, subject, body,
                         received_at, read, message_id, gmail_message_uid)
                    VALUES (?, ?, ?, ?, ?, ?, ?, false, ?, ?)
                    """,
                    [reply_id, str(lead_id), from_email, from_name,
                     subject_raw, body, received_at,
                     message_id or None, uid_str],
                )

                # Update outreach_emails: mark reply_received
                conn.execute(
                    "UPDATE outreach_emails SET reply_received = true, replied_at = ? "
                    "WHERE email_id = ?",
                    [datetime.now(), email_id],
                )

                # Update lead status to replied
                conn.execute(
                    "UPDATE outreach_leads SET status = 'replied' WHERE lead_id = ?",
                    [str(lead_id)],
                )

                imported += 1
                print(f"[POLLER] New reply from {from_email} — imported (lead_id={lead_id})")

            except Exception as e:
                print(f"[POLLER] WARNING: Error processing uid={uid_str}: {e}")
                continue

        return imported

    finally:
        if conn:
            conn.close()
        if mail:
            try:
                mail.logout()
            except Exception:
                pass


# ── Poll loop ─────────────────────────────────────────────────────────────────

def _poll_loop():
    _ensure_schema()
    while True:
        print("[POLLER] Cycle start")
        try:
            n = _run_poll_cycle()
            print(f"[POLLER] Cycle complete — {n} new replies imported")
        except Exception as e:
            print(f"[POLLER] WARNING: Cycle error: {e}")
        import time
        time.sleep(120)


def start_poller():
    thread = threading.Thread(target=_poll_loop, daemon=True, name="OutreachPoller")
    thread.start()
