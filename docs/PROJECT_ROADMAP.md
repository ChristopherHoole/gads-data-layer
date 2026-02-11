# Ads Control Tower (A.C.T) - Project Roadmap

**Last Updated:** 2026-02-11  
**Project Location:** `C:\Users\User\Desktop\gads-data-layer`  
**GitHub:** https://github.com/ChristopherHoole/gads-data-layer

---

## 🎯 PROJECT VISION

Build an AI-powered Google Ads optimization platform that:
- Reads Google Ads data daily
- Analyzes performance using feature engineering
- Generates actionable optimization recommendations
- Executes safe, explainable changes (budgets, bids, keywords, ads)
- Monitors results and auto-rolls back bad changes
- Provides full explainability for client trust

**Target Timeline:** Working prototype in 3-4 weeks

---

## 🏗️ SYSTEM ARCHITECTURE

```
Google Ads Account
        ↓
📥 Data Collector (Chunk 1)
        ↓
📊 Lighthouse (Chunks 2-3) - Insights & Diagnostics
        ↓
🧠 Autopilot (Chunks 4-5-6) - Decision & Execution Engine
        ↓
📡 Radar (Chunk 7) - Monitoring & Rollback
        ↓
📈 Reporting & Scaling (Chunks 8-11)
```

---

## 📋 CHUNK STATUS

### ✅ CHUNK 0: Project Constitution (COMPLETE)
**Status:** 100% Complete  
**Files:**
- `docs/GAds_Project_Constitution_v0.2.md`
- Defines: Guardrails, risk tiers, change limits, rollback policies
- Establishes: Client config requirements, approval workflows

**Key Outputs:**
- ✅ Safety-first philosophy
- ✅ Risk model (Low/Medium/High)
- ✅ Change limits (±10% default)
- ✅ Cooldown rules (7 days)
- ✅ Protected entities (brand campaigns)
- ✅ Client config template

---

### ✅ CHUNK 1: Read-Only Data Layer (COMPLETE)
**Status:** 100% Complete  
**Files:**
- `src/gads_pipeline/` - Main Python package
- `configs/client_001.yaml` - Test client config
- `docker-compose.yml` - PostgreSQL setup
- `tools/check_health.ps1` - Health checks
- `tools/refresh_readonly.ps1` - DB refresh

**Key Outputs:**
- ✅ Google Ads API integration
- ✅ DuckDB warehouse (warehouse.duckdb + warehouse_readonly.duckdb)
- ✅ Analytics view: `analytics.campaign_daily`
- ✅ Daily data ingestion pipeline
- ✅ Idempotent loading (no duplicates)

**Test Account Details:**
- MCC ID: 207-792-3976 (Test Account Access)
- Customer ID: 737-284-4356

**Working Commands:**
```powershell
# Mock mode (fake data, no credentials)
python -m gads_pipeline.cli run-v1 mock .\configs\client_001.yaml --lookback-days 7

# Test mode (real Google Ads API)
python -m gads_pipeline.cli run-v1 test .\configs\client_001.yaml --lookback-days 7

# Refresh readonly DB
.\tools\refresh_readonly.ps1

# Health check
.\tools\check_health.ps1
```

---

### 🔄 CHUNK 2-3: Lighthouse Module (IN PROGRESS)
**Status:** ~70% Complete - Needs Testing & Bug Fixes  
**Files:**
- `act_lighthouse/cli.py` - Command interface
- `act_lighthouse/features.py` - Feature engineering (636 lines)
- `act_lighthouse/diagnostics.py` - Insight generation
- `act_lighthouse/report.py` - JSON report output
- `act_lighthouse/config.py` - Config loading
- `act_lighthouse/db.py` - Database connections

**What Works:**
- ✅ Rolling window calculations (1/3/7/14/30 days)
- ✅ Trend analysis (period-over-period changes)
- ✅ Feature engineering (CTR, CPC, CVR, CPA, ROAS)
- ✅ Insight generation with diagnosis codes
- ✅ JSON report output

**What Needs Work:**
- ⚠️ Not fully tested end-to-end
- ⚠️ May have bugs (ChatGPT coding issues)
- ⚠️ Needs validation on real data
- ⚠️ Missing Constitution compliance (Rule ID references)

**Command:**
```powershell
python -m act_lighthouse.cli run-v0 configs/client_001.yaml --snapshot-date 2026-02-09
```

**Next Steps (Chat 2):**
1. Test thoroughly with mock data
2. Fix any bugs/errors
3. Test with real Google Ads data
4. Validate feature calculations
5. Build synthetic data generator
6. Add Constitution compliance

---

### ❌ CHUNK 4: Optimization Rule Library (NOT STARTED)
**Status:** 0% - Next Priority After Lighthouse  
**Goal:** Create 25-30 comprehensive optimization rules

**Planned Rules:**
- **Budget Rules** (5-10 rules)
  - Increase budget when ROAS > target + lost IS
  - Decrease budget when ROAS < target
  - Reallocate from underperforming to top performers
  
- **Bid Rules** (5-10 rules)
  - Adjust tCPA/tROAS based on performance
  - Increase bids for high-converting keywords losing rank
  - Decrease bids for high-CPA keywords

- **Keyword Rules** (5-10 rules)
  - Add winning search terms as keywords
  - Add negative keywords for wasted spend
  - Pause low-performing keywords

- **Creative Rules** (3-5 rules)
  - Pause low-CTR ads
  - Flag ads for testing

**Rule Structure:**
```python
class Rule:
    id: str              # e.g., "BUDGET-001"
    name: str            # Human-readable name
    risk_tier: str       # Low, Medium, High
    conditions: dict     # When to trigger
    actions: dict        # What to do
    guardrails: list     # Safety checks
    constitution_refs: list  # Rule IDs from Constitution
```

**Timeline:** Week 2 (Chat 3)

---

### ❌ CHUNK 5: Autopilot - Suggest-Only Engine (NOT STARTED)
**Status:** 0%  
**Goal:** Generate actionable recommendations (no execution yet)

**Features:**
- Apply rules to current account state
- Filter by client config (automation_mode, risk_tolerance)
- Rank by expected impact
- Explain reasoning (Rule ID, data window, confidence)
- Output recommendations for human review

**Approval Interface Options:**
- MVP: JSON file output → human reviews → marks approved
- Better: CLI with approve/reject/skip prompts
- Best: Web UI dashboard (later)

**Timeline:** Week 3 (Chat 4-5)

---

### ❌ CHUNK 6: Autopilot - Execution Engine (NOT STARTED)
**Status:** 0%  
**Goal:** Actually make changes to Google Ads

**Phase 6.1 - Budgets Only:**
- Google Ads API write functions (budget changes)
- Validation before execution
- Change logging (before/after, reason, timestamp)
- Dry-run mode

**Phase 6.2 - Add Bids:**
- tCPA/tROAS target changes
- Keyword bid adjustments

**Phase 6.3 - Add Keywords:**
- Add winning search terms
- Add negatives
- Pause underperformers

**Timeline:** Week 4-5 (Chat 6-7)

---

### ❌ CHUNK 7: Radar - Monitoring & Rollback (NOT STARTED)
**Status:** 0%  
**Goal:** Make it safe to run unsupervised

**Features:**
- Post-change monitoring (7-14 days)
- Rollback triggers (CPA/ROAS thresholds)
- Automatic rollback execution
- Alerts (email/Slack)

**Rollback Rules (from Constitution):**
- CPA clients: Rollback if CPA +20% AND conversions -10%
- ROAS clients: Rollback if ROAS -15% OR value -15%
- Lag-aware: Wait minimum 72 hours + median conversion lag

**Timeline:** Week 5-6 (Chat 8-9)

---

### ❌ CHUNK 8-11: Polish & Scale (NOT STARTED)
**Status:** 0% - Future Work

**Chunk 8 - ML Enhancements:**
- Bid elasticity prediction
- Budget-to-conversion curves
- Anomaly detection
- Seasonality adjustment

**Chunk 9 - LLM Integration:**
- Ad copy generation (using Claude API)
- Search term clustering
- Insight explanation
- Client-ready summaries

**Chunk 10 - Reporting & Trust:**
- Web dashboard (React or Flask)
- Before/after metrics
- Change history
- Impact tracking

**Chunk 11 - Multi-Client Scaling:**
- Client templates
- Risk profiles
- Better config UI (form-based)
- Multi-account support

**Timeline:** Week 7+ (After prototype proven)

---

## 🎯 ACCELERATED MVP PATH

Instead of building all 11 chunks sequentially, we're building a **working prototype first**:

### Week 1: Fix & Test Lighthouse
- ✅ Chat 2: Debug Lighthouse, validate features, test thoroughly

### Week 2: Build Rule Library
- ✅ Chat 3: Create 25-30 optimization rules
- ✅ All rules have: conditions, actions, risk tier, Constitution refs

### Week 3: Suggest-Only Engine
- ✅ Chat 4-5: Generate recommendations
- ✅ Simple approval interface
- ✅ Recommendation ranking

### Week 4: Execute (Budgets Only)
- ✅ Chat 6-7: Google Ads write capabilities
- ✅ Validation & guardrails
- ✅ Change logging
- ✅ Dry-run mode

### Week 5-6: Monitoring & Rollback
- ✅ Chat 8-9: Post-change monitoring
- ✅ Automatic rollback
- ✅ Alerts

### Week 7+: Polish & Scale
- Web dashboard
- Multi-client support
- ML enhancements

---

## 🎨 MODULE NAMING (Airport Theme)

**Ads Control Tower** = Overall platform

**Modules:**
- **Lighthouse** = Insights & diagnostics (Chunks 2-3) 🔦
- **Autopilot** = Execution engine (Chunks 4-5-6) ✈️
- **Radar** = Monitoring & anomaly detection (Chunk 7) 📡
- **Flight Plan** = Experiments & structured tests (Future) 🗺️

---

## 📊 CURRENT METRICS

**Lines of Code:** ~1,800 Python lines written  
**Time Invested:** 3 days with ChatGPT on Chunk 1  
**Test Account:** Configured and working  
**Real Client Accounts:** 0 (need Basic Access approval)  
**Database Size:** Small (test data only)  
**Reports Generated:** 1 (Lighthouse JSON from 2026-02-09)

---

## 🚧 KNOWN BLOCKERS

1. **No Basic Access:** Can only use test accounts
   - Need: Valid website, real MCC with clients
   - Timeline: Apply when ready for production testing

2. **No Real Client Data:** Can't test on real campaigns
   - Solution: Build synthetic data generator
   - Alternative: Use test account with small budgets

3. **Lighthouse Untested:** May have bugs
   - Next: Chat 2 - thorough testing & fixes

4. **No Execution Yet:** System is read-only
   - Next: Build rule library, then execution engine

---

## 📝 NEXT ACTIONS

**Immediate (Today):**
1. ✅ Push current code to GitHub (backup before changes)
2. ✅ Start Chat 2: Fix & Test Lighthouse

**This Week:**
- Complete Lighthouse testing
- Fix all bugs
- Validate features are correct
- Build data generator

**Week 2:**
- Design rule library structure
- Write 25-30 optimization rules
- Classify by risk tier

**Week 3:**
- Build recommendation engine
- Create approval interface
- Test on synthetic data

---

## 🎯 SUCCESS CRITERIA (MVP)

Prototype is "done" when:
- ✅ Reads Google Ads data daily (automated)
- ✅ Analyzes 10+ performance dimensions
- ✅ Generates 10-20 recommendations per client
- ✅ Executes budget changes (Low-risk auto, Medium-risk approved)
- ✅ Monitors changes for 7-14 days
- ✅ Auto-rolls back bad changes
- ✅ Logs all actions with full explainability
- ✅ Works on 1-3 test clients reliably

Then we scale to real clients! 🚀

---

**Status Key:**
- ✅ Complete
- 🔄 In Progress
- ⚠️ Needs Attention
- ❌ Not Started
- ⏸️ Deferred
