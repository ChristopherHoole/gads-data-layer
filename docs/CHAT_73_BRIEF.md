# CHAT 73: OPEN/CLICK TRACKING

**Date:** 2026-03-08
**Estimated Time:** 3–4 hours
**Priority:** HIGH
**Dependencies:** Chat 72 complete (send reply live)

---

## CONTEXT & APPROACH

Chat 72 completed live email sending from both Queue and Replies pages. All 6 tracking columns already exist in `outreach_emails` (`opened_at`, `clicked_at`, `cv_opened_at`, `open_count`, `click_count`, `cv_open_count`) but nothing writes to them. This chat builds the full tracking infrastructure — 3 endpoints + injection on send. Tracking only fires when ACT is publicly accessible; for now it works on localhost for testing with a reseed tool.

Build order:
1. Add `base_url` to `email_config.yaml`
2. Add 3 tracking endpoints to `outreach.py`
3. Add `inject_tracking()` helper that wraps links + appends pixel
4. Call `inject_tracking()` in `queue_send()` before `send_email()`
5. Create `tools/reseed_tracking.py` to seed fake tracking data for Analytics page testing

---

## OBJECTIVE

Build open/click/CV tracking endpoints and auto-inject tracking into all outgoing emails.

---

## DELIVERABLES

1. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\secrets\email_config.yaml` — MODIFY
   - Add `base_url: http://localhost:5000`

2. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\outreach.py` — MODIFY
   - Add 3 tracking endpoints (see Requirements)
   - Add `inject_tracking()` helper function
   - Call `inject_tracking()` in `queue_send()` before `send_email()`
   - Add CSRF exemptions comment for the 3 new routes

3. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\app.py` — MODIFY
   - Add CSRF exemptions for 3 new tracking routes:
     - `outreach.track_open`
     - `outreach.track_click`
     - `outreach.track_cv`
   - Label each: `✅ [Chat 73] CSRF exempted: outreach.track_*`

4. `C:\Users\User\Desktop\gads-data-layer\tools\reseed_tracking.py` — CREATE
   - Seeds fake open/click data into `outreach_emails` for the test lead
   - Sets `open_count=3`, `click_count=1`, `cv_open_count=1`
   - Sets `opened_at`, `clicked_at`, `cv_opened_at` to realistic recent timestamps
   - Idempotent — safe to run multiple times
   - Prints: `Done. Tracking data seeded for test lead.`

5. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_73_HANDOFF.md` — CREATE
6. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_73_SUMMARY.md` — CREATE

---

## REQUIREMENTS

### Tracking Endpoints

**Open pixel:**
```
GET /outreach/track/open/<email_id>
```
- Look up `outreach_emails` by `email_id`
- If found: `UPDATE outreach_emails SET open_count = open_count + 1, opened_at = COALESCE(opened_at, now()) WHERE id = email_id`
- Return a 1×1 transparent GIF (inline bytes — no file needed):
```python
from flask import Response
GIF_1X1 = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00\x21\xf9\x04\x00\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b'
return Response(GIF_1X1, mimetype='image/gif', headers={'Cache-Control': 'no-cache, no-store'})
```
- Log: `[TRACKING] open: email_id={email_id}`

**Click redirect:**
```
GET /outreach/track/click/<email_id>?url=<target_url>
```
- Look up `outreach_emails` by `email_id`
- If found: `UPDATE outreach_emails SET click_count = click_count + 1, clicked_at = COALESCE(clicked_at, now()) WHERE id = email_id`
- `target_url = request.args.get('url', '/')`
- Log: `[TRACKING] click: email_id={email_id} → {target_url}`
- Return `redirect(target_url)`

**CV open redirect:**
```
GET /outreach/track/cv/<email_id>
```
- Look up `outreach_emails` by `email_id`
- If found: `UPDATE outreach_emails SET cv_open_count = cv_open_count + 1, cv_opened_at = COALESCE(cv_opened_at, now()) WHERE id = email_id`
- Get CV path from `system_config` table (key=`cv_path`)
- Log: `[TRACKING] cv_open: email_id={email_id}`
- Return `redirect(url_for('static', filename='uploads/cv/' + cv_filename))`
- If no CV found: return 404

### inject_tracking() Helper

Add this function to `outreach.py` (above `queue_send()`):

```python
def inject_tracking(body_html, email_id, base_url, has_cv=False):
```

- **Wrap all links:** Find all `href="http://..."` and `href="https://..."` in `body_html` using regex
  - Replace with `href="{base_url}/outreach/track/click/{email_id}?url={original_url}"`
  - URL-encode the original URL in the query param
- **CV link:** If `has_cv=True`, append a "View my CV" link using the CV tracking endpoint:
  - `<a href="{base_url}/outreach/track/cv/{email_id}">View my CV</a>`
  - Add this just before the signature separator `<br><br><hr`
- **Tracking pixel:** Append as the very last element inside the wrapping div, just before `</div>`:
  - `<img src="{base_url}/outreach/track/open/{email_id}" width="1" height="1" style="display:none;" />`

### queue_send() Changes

After building `body_html` and appending signature, add:
```python
base_url = email_config.get('base_url', 'http://localhost:5000')
has_cv = bool(cv_attached and cv_path)
body_html = inject_tracking(body_html, email_id, base_url, has_cv=has_cv)
```

### Constraints
- 🚨 Deselect worktree — all work on main branch
- 🚨 Do NOT send test emails — Christopher tests manually
- `opened_at` uses `COALESCE` — only sets on first open, never overwrites
- Same pattern for `clicked_at` and `cv_opened_at`
- All 3 endpoints must work without authentication (tracking pixels load in recipient's email client with no session)
- URL encoding for click redirect: use `urllib.parse.quote(target_url, safe='')`

---

## SUCCESS CRITERIA

- [ ] `email_config.yaml` has `base_url: http://localhost:5000`
- [ ] `GET /outreach/track/open/<id>` returns a 1×1 GIF and writes to DB
- [ ] `GET /outreach/track/click/<id>?url=https://example.com` redirects and writes to DB
- [ ] `GET /outreach/track/cv/<id>` redirects to CV file and writes to DB
- [ ] After `python tools/reseed_queue.py` + send from Queue page, Flask log shows `[TRACKING]` pixel URL in email source (verify via Gmail "Show original")
- [ ] `python tools/reseed_tracking.py` runs clean and seeds data
- [ ] Analytics page shows non-zero open/click counts for test lead
- [ ] Flask starts cleanly, no errors
- [ ] All 3 CSRF exemptions present in `app.py`

---

## REFERENCE FILES

- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\outreach.py` — `queue_send()` at ~line 671, existing send logic
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\email_sender.py` — `load_email_config()` pattern
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\app.py` — CSRF exemption pattern
- `C:\Users\User\Desktop\gads-data-layer\tools\reseed_replies.py` — reseed tool pattern

---

## TESTING (Claude Code — no email sends)

1. Confirm `email_config.yaml` has `base_url`
2. Confirm 3 endpoints exist in `outreach.py`
3. Confirm 3 CSRF exemptions in `app.py`
4. Run `python tools/reseed_tracking.py` — confirm clean, prints confirmation
5. DB check: `SELECT open_count, click_count, cv_open_count FROM outreach_emails WHERE id='00000000-0000-0000-0000-000000000001'` — must show 3, 1, 1
6. Start Flask — confirm clean startup
7. Test open endpoint directly: `http://localhost:5000/outreach/track/open/00000000-0000-0000-0000-000000000001` — must return GIF (check Flask log for `[TRACKING] open`)
8. Test click endpoint: `http://localhost:5000/outreach/track/click/00000000-0000-0000-0000-000000000001?url=https://christopherhoole.com` — must redirect and log
9. Report all results — Christopher verifies Analytics page in Opera
