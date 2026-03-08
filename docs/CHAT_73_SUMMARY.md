# CHAT 73 SUMMARY: Open/Click Tracking

**Date:** 2026-03-08
**Status:** Complete

## What Was Built

Full open/click/CV tracking infrastructure for outgoing emails.

### Files Modified

**`act_dashboard/secrets/email_config.yaml`**
- Added `base_url: http://localhost:5000`

**`act_dashboard/routes/outreach.py`**
- Added `inject_tracking(body_html, email_id, base_url, has_cv=False)` helper above `queue_send()`
  - Wraps all `http/https` hrefs with click-tracking redirect
  - Appends CV link before `<br><br><hr` separator when `has_cv=True`
  - Appends 1×1 transparent tracking pixel before closing `</div>`
- Added 3 tracking endpoints (all CSRF exempt, no `@login_required`):
  - `GET /outreach/track/open/<email_id>` — returns 1×1 GIF, increments `open_count`
  - `GET /outreach/track/click/<email_id>?url=<target>` — redirects, increments `click_count`
  - `GET /outreach/track/cv/<email_id>` — redirects to CV file, increments `cv_open_count`
- Updated `queue_send()` to call `inject_tracking()` before `send_email()`

**`act_dashboard/app.py`**
- Added Chat 73 CSRF exemption block for `outreach.track_open`, `outreach.track_click`, `outreach.track_cv`

### Files Created

**`tools/reseed_tracking.py`**
- Seeds `open_count=3`, `click_count=1`, `cv_open_count=1` for test email_id `00000000-0000-0000-0000-000000000002`
- Sets realistic recent timestamps for all three `*_at` columns
- Idempotent — safe to run multiple times

## DB Verification

```
open_count=3, click_count=1, cv_open_count=1 ✅
opened_at, clicked_at, cv_opened_at all set ✅
```

## Key Design Decisions

- `COALESCE(opened_at, now())` — first open only, never overwrites
- All 3 tracking endpoints require no auth (email clients have no session)
- `urllib.parse.quote(url, safe='')` for click URL encoding
- `base_url` falls back to `http://localhost:5000` if not in config
- `TEST_EMAIL_ID = "00000000-0000-0000-0000-000000000002"` matches reseed_queue.py
