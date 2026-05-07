# DBD Daily Morning Routine

## Step 1 — Snapshot catch-up (only if scheduler missed)
- Check ACT Morning Review for "ACT last ran"
- If yesterday's snapshot missing: `python -m act_dashboard.scheduler.overnight_run`

## Step 2 — PMax CSV ingest
- Open the GAds scheduled report email
- Click the link, CSV downloads to `C:\Users\User\Downloads\`
- Drag-drop into `client_csvs/dbd001/incoming/` — auto-watcher ingests + archives
- Confirm in ACT Search Terms that PMax row count looks right
- Click **Reclassify today's terms** in ACT to bucket the new PMax data

## Step 3 — Search Term triage (Pass 1/2)
- Work through the 4 main flows in ACT Search Terms tab
- Block / Don't Block each
- Push to GAds Neg Lists at the end

## Step 4 — Pass 3 AI
- Click **Run Pass 3** (live counter shows progress, takes 30s-2min)
- Review the 5-15 fragments + theme summary
- Block the safe ones (locations, competitors first; off-not-adv if confident)
- Push to GAds Neg Lists

## Step 5 — PMax → DII redirect (NEW)
**Goal:** slowly starve PMax of search terms now covered by new DII ad groups.

1. Open GAds → Dental Implants - Pmax campaign → **Search terms** tab → last 14 days
2. Sort by **Cost** descending
3. For each high-cost term, ask:
   - Is there a matching `[ex]` ad group in DII that covers this exact intent?
   - If YES → add term to **PMax Exact Negs** list as exact match
   - If NO → leave it (PMax's job to cover the gaps until DII has coverage)
4. Track total cost of negs added today
5. **Drop PMax daily budget by the same amount** — e.g. £140/day of terms negged → cut PMax budget by £140/day
6. Log what was redirected in a quick note (term + cost + DII ad group it now serves)

**Rules:**
- ONLY neg a PMax term if the matching `[ex]` keyword is already live + approved in DII
- Watch DII impressions / conversions next day — confirm it actually picked up the redirected traffic
- Don't cut PMax budget faster than terms negged — leaves PMax serving worse terms with the freed budget
- Cap: ~50 terms/day to avoid shocking the campaign

## Step 6 — Continue GAds rebuild
- Pick next parent from `Campaigns/_LP_URLS.md` build sequence
- Build LPs → ngrok review → push live → generate Ads Editor CSVs → upload
- Aim 4-7 parents per day

## Step 7 — Daily log
- Update memory + handoff if anything material happened
- Note any pending Tommaso/Giulio decisions

---
**Updated:** 2026-05-05 (added Step 5 PMax→DII redirect)
