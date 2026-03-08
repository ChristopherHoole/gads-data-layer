# CHAT 73 HANDOFF

**Date:** 2026-03-08
**Status:** Complete — ready for manual testing

## What To Test

### 1. Reseed and verify DB

```bash
python tools/reseed_queue.py
python tools/reseed_tracking.py
```

Expected output:
```
Done. Test email reseeded to chrishoole101@gmail.com. Total queued: X
Done. Tracking data seeded for test lead.
  open_count=3, click_count=1, cv_open_count=1
```

### 2. Flask startup

```bash
python -m act_dashboard.app
```

Check for:
- `✅ [Chat 73] CSRF exempted: outreach.track_open`
- `✅ [Chat 73] CSRF exempted: outreach.track_click`
- `✅ [Chat 73] CSRF exempted: outreach.track_cv`
- No startup errors

### 3. Test open endpoint (browser)

```
http://localhost:5000/outreach/track/open/00000000-0000-0000-0000-000000000002
```

- Browser should return a blank/transparent image (1×1 GIF)
- Flask log should show: `[TRACKING] open: email_id=00000000-0000-0000-0000-000000000002`

### 4. Test click endpoint (browser)

```
http://localhost:5000/outreach/track/click/00000000-0000-0000-0000-000000000002?url=https://christopherhoole.com
```

- Browser should redirect to `https://christopherhoole.com`
- Flask log should show: `[TRACKING] click: email_id=00000000-0000-0000-0000-000000000002 → https://christopherhoole.com`

### 5. Send email from Queue page, check Gmail source

After sending, in Gmail "Show original":
- Should see `<img src="http://localhost:5000/outreach/track/open/..." ...>`
- All links should be wrapped: `href="http://localhost:5000/outreach/track/click/...?url=..."`

### 6. Analytics page

Open Analytics page in Opera — should show non-zero open/click counts for the test lead.

## Notes

- `base_url` in `email_config.yaml` controls the tracking domain. Change to the live server URL when ACT is hosted publicly.
- The test email_id `00000000-0000-0000-0000-000000000002` is created by `reseed_queue.py`.
- All 3 tracking endpoints work without authentication (by design — email clients have no session).

## Next Chat

Analytics page display of tracking data is already in the DB. Chat 74 may focus on:
- Live server deployment (changing `base_url` to public URL)
- Reply tracking or other pipeline steps
