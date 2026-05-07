# Morning Review — Sub-Group Plan (4 May 2026)

**TL;DR:** 26 parent ad groups → **74 total ad groups** when split by intent dimension.
**842 dental-tourism keywords** become defensive negs across all groups.
6 build days = ~12 ad groups/day. Tight but matches your last sprint pace (25 LPs in 2 days).

---

## How parents broke down

| Parent | Sub-groups | Why this number |
|---|---:|---|
| general_implants | **9** | Biggest universe — 5,000+ historical variants across every intent dimension |
| all_on_4 | 6 | Core / Cost / Cheap / Location / Comparison / Brand all justified by data |
| new_teeth | 6 | Wide intent spread |
| full_mouth_implants | 5 | Core / Cost / Cheap / Location / Finance |
| all_on_6 | 4 | Smaller but still 4 distinct intent buckets |
| implants_elderly | 4 | |
| comparison_shoppers | 4 | |
| implant_denture | 4 | (PENDING Giulio — only build if approved) |
| screwless_implants | 3 | |
| same_day_teeth | 3 | |
| smile_in_a_day | 3 | |
| implant_clinic | 3 | |
| permanent_teeth_48h | 2 | |
| full_arch | 2 | |
| upper_jaw | 2 | |
| implant_bridge | 2 | |
| bone_graft | 2 | |
| lower_jaw | 1 | (no historical split) |
| nobel_biocare | 1 | |
| fixed_teeth | 1 | |
| zygomatic_pterygoid | 1 | (PENDING Giulio) |
| straumann | 1 | (PENDING Giulio) |
| nhs_implants | 1 | (PENDING Tommaso/Giulio) |
| vivo_bridge | 1 | (no historical — build because DBD's branded product) |
| single_arch | 1 | (no historical split — kept as standalone per your call) |
| double_arch | 1 | (same as single arch) |
| implant_replacement | 1 | (no historical) |
| **Total** | **74** | |

---

## Split logic (the rules the script applied)

For every parent, every keyword got bucketed into one intent dimension by priority:
TOURISM → NHS → COMPARISON → LOCATION → FINANCE → CHEAP → COST → INFO → BRAND → CORE.

Then each (parent, dimension) was scored:
- **TOURISM** keywords → defensive negs (842 of them across all groups). Never built as ad groups.
- **< 3 keywords** in a dimension → merged back into the parent's CORE.
- **bookings > 0** in a dimension → BUILD (proven conversion = own RSA + LP messaging).
- **>= 10 keywords AND >= £50 spend** → BUILD (volume justifies).
- **else** → merged into CORE.

This is in `_PLAN_subgroups.md` line by line. Full per-row data in `_PLAN_subgroup_data.csv`.

---

## What this means for the build

**Total deliverables:**
- 74 ad groups (one keyword set per group, 10-25 keywords each)
- ~222 RSAs (3 per group, 15 headlines + 4 descriptions each)
- 74 LPs (one per ad group; some can share if intent overlaps significantly)
- 1 master defensive-negs list (842 tourism + foreign-language keywords) applied at campaign or shared list level

**Day allocation (rough):**
- Day 1: 12 ad groups (the 5 Day-1 parents → ~24 sub-groups; pick the 12 with highest historical bookings)
- Day 2: 12-13 ad groups (5 Day-2 parents)
- Day 3: 13-14 ad groups (6 Day-3 parents — single/double/full arch + upper/lower jaw + elderly)
- Day 4: 14-16 ad groups (7 Day-4 parents + comparison_shoppers)
- Day 5: 4-7 ad groups (PENDING approvals only)
- Day 6: Buffer + neg audit + ad scheduling

**Reality check:** 74 LPs in 5 build days = 15/day. You did 25 LPs in 2 days last week (= 12.5/day). So this is achievable but no slack.

---

## Three decisions I need from you in the morning

### 1. Approve 74, or trim?

Three options:
- **A — Build all 74** (best Quality Score, biggest build effort, 6 days tight)
- **B — Trim to ~50** by merging similar dimensions (e.g. CHEAP always rolls into COST; INFO rolls into CORE unless very high-volume). Easier build, slightly lower QS.
- **C — Trim to ~30** by only splitting the top 5 parents (All on 4, Full Mouth, General Implants, New Teeth, Same Day). Other 21 parents stay as single ad groups. Fastest build but most parents miss the QS benefit.

My recommendation: **A** — you said yes to extra work for best product. Quality Score saves serious money on a £45k/mo budget.

### 2. Should some split sub-groups share a single LP?

E.g. for All on 4, the 6 sub-groups could:
- **Option X — 6 separate LPs**: All-On-4 / All-On-4 Cost / All-On-4 Cheap / All-On-4 London / All-On-4 vs All-On-6 / All-On-4 Brand. Best Quality Score per group.
- **Option Y — 1 LP with anchor sections**: One `all-on-4` page with `#cost`, `#location`, `#vs-all-on-6` anchors. Each ad group's Final URL points to its own anchor. Easier build (1 LP per parent = 27 total LPs instead of 74).

Option Y cuts LP build effort from 74 to ~27. Quality Score impact is real but smaller than ad group split impact (Google scores the page, but the anchor + page content is what matters).

My recommendation: **Y** — 1 LP per parent with anchor sections. Saves 50%+ of LP build effort. Quality Score still good because the LP content covers the parent topic comprehensively.

### 3. Tourism negs — campaign level, or shared list?

842 keywords (hungary, poland, czech, thailand, "cheapest country", Polish "cena/cennik" etc.) need to be excluded across every ad group. Two ways:
- **Campaign-level negs**: applied once at the new campaign level, blocks all ad groups inside
- **Shared neg list**: new "DII Tourism Block" list applied to the new campaign

Both work. Shared list is reusable on future campaigns. Recommendation: **shared list**.

---

## Files in this folder

- `_PLAN_subgroups.md` — full per-parent breakdown, every sub-group with data + recommendation
- `_PLAN_subgroup_data.csv` — same data as table (sortable in Excel/Sheets)
- `_LP_URLS.md` — earlier 26-LP URL list (will need updating once you decide LP strategy)
- `Day_1/` — folder with the 5 Day-1 ad-group draft files. Day 1's All-On-4 file is in the OLD format (single ad group, 109 keywords) — will need rewriting once you approve the split. The other 4 Day-1 files are even older format.

I'm not drafting more keywords/RSAs until you confirm the split direction in the morning. Otherwise we'd waste effort if you trim.
