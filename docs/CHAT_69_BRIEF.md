# CHAT 69: EMAIL SIGNATURE

**Date:** 2026-03-07
**Estimated Time:** 1–2 hours
**Priority:** HIGH
**Dependencies:** Chat 68 complete

---

## CONTEXT

Chat 68 built live email sending via Gmail SMTP (`chris@christopherhoole.com`). Emails currently send without any signature block. Every outgoing email needs a consistent HTML signature appended below the body.

## OBJECTIVE

Append a formatted HTML signature to every email sent from `queue_send()`.

---

## DELIVERABLES

1. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\email_sender.py` — MODIFY
   - Add `get_signature_html()` function returning formatted HTML signature block

2. `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\outreach.py` — MODIFY
   - In `queue_send()`, append signature to `body_html` before calling `send_email()`

3. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_69_HANDOFF.md` — CREATE
4. `C:\Users\User\Desktop\gads-data-layer\docs\CHAT_69_SUMMARY.md` — CREATE

---

## REQUIREMENTS

### Signature Content
- Name: Christopher Hoole
- Title: Google Ads Specialist | 16 Years Experience
- Email: chris@christopherhoole.com
- Website: https://christopherhoole.com
- Top border separator, grey text, Arial font, 12px

### Technical
- Signature appended after body content, separated by `<br><br><hr style='border:none;border-top:1px solid #ddd;margin:20px 0;'>`
- Must not break existing `body_html` wrapping div
- UTF-8 safe — no special characters in signature

---

## SUCCESS CRITERIA

- [ ] Email arrives at chrishoole101@gmail.com with visible signature below body
- [ ] Signature shows name, title, email, website
- [ ] Separator line between body and signature
- [ ] Special characters render correctly
- [ ] Flask log shows `[EMAIL] OK Sent`
- [ ] No console errors, Flask starts cleanly

---

## REFERENCE FILES

- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\email_sender.py` — current `send_email()` implementation
- `C:\Users\User\Desktop\gads-data-layer\act_dashboard\routes\outreach.py` — current `queue_send()` (~line 671)

---

## TESTING

1. Run `python tools/reseed_queue.py`
2. Start Flask
3. Send one email from Queue page
4. Check chrishoole101@gmail.com — confirm signature present and correctly formatted
5. Report exact Flask `[EMAIL] OK Sent` log line
