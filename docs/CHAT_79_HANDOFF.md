# CHAT 79 Handoff

## Testing checklist

Run through these steps in Opera after starting Flask fresh:

1. **Trigger renders** — Calendar icon + date label + chevron visible in navbar
2. **Quick buttons** — 7d / 30d / 90d sit below trigger, correct one shows active (blue)
3. **Open panel** — Click trigger → panel appears, calendar shows correct month, preset highlighted
4. **Preset click** — Click "Last 30 days" → panel closes, page reloads with 30-day data
5. **Custom range** — Click trigger → click "Custom range" → panel stays open → click start date → click end date → click Apply → page reloads with correct range
6. **Cancel** — Open panel, change something, click Cancel → panel closes, no change
7. **Quick button** — Click 7d → page reloads immediately (no panel needed)
8. **Date inputs** — Type `09/03/2026` in start field → calendar highlights update
9. **Month nav** — Click ‹/› arrows → calendar navigates to prev/next month
10. **Other pages** — Campaigns, Keywords, Ad Groups, Ads, Shopping all show working date picker
11. **Console** — No JS errors in DevTools console
12. **Flask log** — No Python errors on startup or date change

## Known limitation

Presets other than 7d/30d/90d (Today, Yesterday, 14 days, This month, Last month, All time) get stored in the session as custom date ranges. After a page reload, the trigger label shows the formatted date range rather than the preset name (e.g. "Mar 9 – Mar 9, 2026" instead of "Today"). This is a backend limitation — the session schema only stores days or dates, not named presets. Fixing this would require a backend change, which was out of scope for Chat 79.

## Files to know

| File | Role |
|------|------|
| `act_dashboard/templates/components/date_filter.html` | The component (replaced in Chat 79) |
| `act_dashboard/static/css/custom.css` | CSS (appended in Chat 79, see `/* ── Date Picker (Chat 79) ── */`) |
| `act_dashboard/routes/shared.py` | `/set-date-range` endpoint + `get_date_range_from_session()` |

## If something breaks

- **Panel not showing**: check `dp-wrapper` has `position: relative` and `dp-panel` has `z-index: 1050`; make sure no parent has `overflow: hidden`
- **Dates wrong**: the `calcPreset()` function in date_filter.html calculates all dates relative to `today` (browser clock); check the system clock
- **Submit fails**: check browser DevTools Network tab for the POST to `/set-date-range`; expected payload: `{"range_type":"custom","date_from":"YYYY-MM-DD","date_to":"YYYY-MM-DD"}`
- **Active preset not highlighted**: `ACTIVE_DAYS` is injected from Jinja2; check that the including template passes `active_days`
