# Ads Control Tower - System Architecture

**Last Updated:** 2026-02-11

---

## 🏗️ HIGH-LEVEL ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                        GOOGLE ADS ACCOUNTS                      │
│  (Client Campaigns, Ad Groups, Keywords, Ads, Search Terms)    │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ Google Ads API
                     │ (Read: Daily)
                     │ (Write: When approved)
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                      📥 DATA COLLECTOR                           │
│                   (gads_pipeline - Chunk 1)                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  • API Authentication & MCC Management                   │  │
│  │  • Daily Performance Pull (Campaign/AdGroup/Keyword)     │  │
│  │  • Immutable Snapshot Storage                            │  │
│  │  • Conversion Lag Handling                               │  │
│  │  • Idempotent Loading (No Duplicates)                    │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    🗄️ DATA WAREHOUSE LAYER                       │
│                                                                 │
│  ┌────────────────────┐          ┌──────────────────────┐      │
│  │  warehouse.duckdb  │          │ PostgreSQL           │      │
│  │  (Build/Write)     │          │ (Metadata Store)     │      │
│  │                    │          │                      │      │
│  │  • raw_*           │          │  • Run logs          │      │
│  │  • snap_*          │          │  • Change history    │      │
│  │  • analytics.*     │          │  • Client configs    │      │
│  └────────┬───────────┘          └──────────────────────┘      │
│           │                                                     │
│           │ File Copy (refresh_readonly.ps1)                   │
│           ▼                                                     │
│  ┌────────────────────┐                                        │
│  │ warehouse_readonly │                                        │
│  │ .duckdb            │                                        │
│  │ (Read-Only)        │                                        │
│  │                    │                                        │
│  │ For:               │                                        │
│  │  • DBeaver         │                                        │
│  │  • Dashboards      │                                        │
│  │  • Analysis        │                                        │
│  └────────────────────┘                                        │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                 🔦 LIGHTHOUSE (Chunks 2-3)                       │
│                 Insights & Diagnostics Engine                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  FEATURE ENGINEERING:                                    │  │
│  │  • Rolling Windows (1d/3d/7d/14d/30d)                    │  │
│  │  • Trend Analysis (Period-over-Period Δ)                 │  │
│  │  • Efficiency Metrics (CTR, CPC, CVR, CPA, ROAS)        │  │
│  │  • Opportunity Detection (Lost IS, Low CTR, etc.)       │  │
│  │                                                          │  │
│  │  DIAGNOSTICS:                                            │  │
│  │  • Performance Classification (Good/Bad/Opportunity)     │  │
│  │  • Diagnosis Codes (LOW_DATA, UNDERPERFORMING, etc.)    │  │
│  │  • Confidence Scoring (0-1 based on data quality)       │  │
│  │  • Risk Tier Assignment (Low/Medium/High)               │  │
│  │                                                          │  │
│  │  OUTPUT:                                                 │  │
│  │  • JSON Reports                                          │  │
│  │  • Ranked Insights (Top 5-10 per client)                │  │
│  │  • Evidence & Reasoning                                  │  │
│  │  • Guardrail References                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│              ✈️ AUTOPILOT (Chunks 4-5-6) - NOT BUILT YET        │
│                    Decision & Execution Engine                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  RULE LIBRARY (Chunk 4):                                 │  │
│  │  • Budget Rules (Increase/Decrease/Reallocate)           │  │
│  │  • Bid Rules (tCPA/tROAS Adjustments)                    │  │
│  │  • Keyword Rules (Add/Pause/Negatives)                   │  │
│  │  • Creative Rules (Ad Testing/Pausing)                   │  │
│  │                                                          │  │
│  │  SUGGESTION ENGINE (Chunk 5):                            │  │
│  │  • Apply Rules to Current State                          │  │
│  │  • Filter by Client Config (automation_mode, risk)       │  │
│  │  • Rank by Expected Impact                               │  │
│  │  • Generate Recommendations with Reasoning               │  │
│  │                                                          │  │
│  │  APPROVAL LAYER:                                         │  │
│  │  • automation_mode: insights → No execution              │  │
│  │  • automation_mode: suggest → Show all, execute none    │  │
│  │  • automation_mode: auto_low_risk → Auto Low, approve Rest│ │
│  │  • automation_mode: auto_expanded → Auto Low+Medium     │  │
│  │                                                          │  │
│  │  EXECUTION ENGINE (Chunk 6):                             │  │
│  │  • Google Ads API Write Functions                        │  │
│  │  • Validation Before Execution                           │  │
│  │  • Change Logging (Before/After/Reason/Timestamp)        │  │
│  │  • Dry-Run Mode                                          │  │
│  │  • Batch Updates                                         │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│              📡 RADAR (Chunk 7) - NOT BUILT YET                  │
│              Monitoring, Rollback & Safety Net                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  POST-CHANGE MONITORING:                                 │  │
│  │  • Track Performance for 7-14 Days                        │  │
│  │  • Compare to Pre-Change Baseline                         │  │
│  │  • Detect Performance Regression                          │  │
│  │                                                          │  │
│  │  ROLLBACK TRIGGERS:                                      │  │
│  │  • CPA Clients: CPA +20% AND Conversions -10%           │  │
│  │  • ROAS Clients: ROAS -15% OR Value -15%                │  │
│  │  • Lag-Aware: Wait 72hr + median conversion lag         │  │
│  │                                                          │  │
│  │  AUTOMATIC ROLLBACK:                                     │  │
│  │  • Reverse Change via Google Ads API                     │  │
│  │  • Log Rollback Reason                                   │  │
│  │  • Send Alert (Email/Slack)                              │  │
│  │                                                          │  │
│  │  ANOMALY DETECTION:                                      │  │
│  │  • Spend Spikes                                          │  │
│  │  • Conversion Drops                                      │  │
│  │  • Quality Score Changes                                 │  │
│  │  • Policy Violations                                     │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                 📊 REPORTING & CLIENT INTERFACE                  │
│                    (Chunks 8-11) - FUTURE                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  • Web Dashboard (React/Flask)                           │  │
│  │  • Client-Facing Reports                                 │  │
│  │  • Change History & Audit Logs                           │  │
│  │  • Before/After Performance Metrics                      │  │
│  │  • Explainability (Why Changes Were Made)                │  │
│  │  • Multi-Client Management                               │  │
│  │  • Client Config UI (Form-Based)                         │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 DATA FLOW DIAGRAM

```
                        ┌──────────────┐
                        │ Google Ads   │
                        │   Account    │
                        └──────┬───────┘
                               │
                               │ Daily API Pull
                               │
                        ┌──────▼───────┐
                        │ gads_pipeline│
                        │     CLI      │
                        └──────┬───────┘
                               │
                        ┌──────▼───────────────────┐
                        │ DuckDB Warehouse         │
                        │                          │
                        │ raw_campaign_daily       │
                        │ snap_campaign_daily      │
                        │ analytics.campaign_daily │
                        └──────┬───────────────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
            ┌───────▼──────┐      ┌──────▼────────┐
            │  Lighthouse  │      │   DBeaver     │
            │  (Analysis)  │      │  (Human View) │
            └───────┬──────┘      └───────────────┘
                    │
            ┌───────▼────────────────┐
            │ Features Engineering   │
            │  • Rolling windows     │
            │  • Trends & deltas     │
            │  • Efficiency metrics  │
            └───────┬────────────────┘
                    │
            ┌───────▼───────────┐
            │   Diagnostics     │
            │  • Classify perf  │
            │  • Find issues    │
            │  • Rank insights  │
            └───────┬───────────┘
                    │
            ┌───────▼───────────────┐
            │   JSON Report         │
            │  • Top insights       │
            │  • Evidence           │
            │  • Recommendations    │
            └───────┬───────────────┘
                    │
                    │ (FUTURE)
                    │
            ┌───────▼───────────┐
            │   Autopilot       │
            │  • Apply rules    │
            │  • Generate recs  │
            │  • Get approval   │
            └───────┬───────────┘
                    │
            ┌───────▼───────────┐
            │  Execute Changes  │
            │  • Budgets        │
            │  • Bids           │
            │  • Keywords       │
            └───────┬───────────┘
                    │
            ┌───────▼───────────┐
            │  Google Ads API   │
            │  (Write Changes)  │
            └───────┬───────────┘
                    │
            ┌───────▼───────────┐
            │   Monitor         │
            │  • Track perf     │
            │  • Detect issues  │
            │  • Rollback bad   │
            └───────────────────┘
```

---

## 🗂️ FILE STRUCTURE

```
gads-data-layer/
│
├── 📁 configs/                    # Client configurations
│   ├── client_001.yaml           # Test client config
│   ├── client_001_mcc.yaml       # MCC-level config
│   └── google-ads.example.yaml   # Credentials template
│
├── 📁 secrets/                    # NEVER COMMIT (gitignored)
│   ├── google-ads.yaml           # Real API credentials
│   └── google_ads_client_secret.json  # OAuth client secret
│
├── 📁 src/
│   └── 📁 gads_pipeline/         # Chunk 1: Data Layer
│       ├── cli.py                # Command-line interface
│       ├── v1_runner.py          # Main ingestion logic
│       ├── warehouse_duckdb.py   # DuckDB operations
│       ├── config_models.py      # Configuration schemas
│       ├── meta_db.py            # PostgreSQL metadata
│       └── ...
│
├── 📁 act_lighthouse/            # Chunks 2-3: Analysis
│   ├── cli.py                    # Lighthouse command interface
│   ├── features.py               # Feature engineering (636 lines)
│   ├── diagnostics.py            # Insight generation
│   ├── report.py                 # JSON report output
│   ├── config.py                 # Config loading
│   └── db.py                     # Database connections
│
├── 📁 docs/                       # Documentation
│   ├── GAds_Project_Constitution_v0.2.md  # Chunk 0: Rules
│   ├── CHUNK_1_HANDOFF.md        # Chunk 1 status
│   └── ...
│
├── 📁 scripts/                    # Helper scripts
│   └── google_ads_oauth.py       # OAuth token generator
│
├── 📁 tools/                      # PowerShell automation
│   ├── check_health.ps1          # Health checks
│   ├── refresh_readonly.ps1      # DB refresh
│   └── apply_analytics.py        # Create analytics views
│
├── 📁 sql/                        # SQL scripts
│   └── analytics_views.sql       # View definitions
│
├── 📁 reports/                    # Generated reports
│   └── lighthouse/
│       └── Test_Client_001/
│           └── 2026-02-09.json   # Sample output
│
├── 📄 docker-compose.yml          # PostgreSQL setup
├── 📄 requirements.txt            # Python dependencies
├── 📄 pyproject.toml              # Package configuration
├── 📄 .gitignore                  # Git exclusions
├── 📄 .env.example                # Environment template
│
├── 🗄️ warehouse.duckdb            # Build database (write)
└── 🗄️ warehouse_readonly.duckdb   # Browse database (read-only)
```

---

## 📊 DATABASE SCHEMA

### Raw Tables (Internal - Do Not Query Directly)

**`raw_campaign_daily`**
- Append-only immutable history
- All ingestion runs preserved

**`snap_campaign_daily`**
- Latest snapshot per (customer_id, snapshot_date, campaign_id)
- Idempotent upserts

### Analytics Layer (Query These)

**`analytics.campaign_daily`**
```sql
-- Core fields from Google Ads
customer_id          VARCHAR
snapshot_date        DATE
campaign_id          BIGINT
campaign_name        VARCHAR
campaign_status      VARCHAR
channel_type         VARCHAR
impressions          BIGINT
clicks               BIGINT
cost_micros          BIGINT
conversions          DOUBLE
conversions_value    DOUBLE

-- Derived metrics (calculated)
cost                 DOUBLE   -- cost_micros / 1M
ctr                  DOUBLE   -- clicks / impressions
cpc                  DOUBLE   -- cost / clicks
cpm                  DOUBLE   -- cost / (impressions / 1000)
roas                 DOUBLE   -- conversions_value / cost
```

**`analytics.campaign_features_daily`** (Lighthouse output)
```sql
-- Identifiers
client_id            TEXT
customer_id          TEXT
campaign_id          TEXT
snapshot_date        DATE
campaign_name        TEXT

-- Rolling window aggregations (w1/w3/w7/w14/w30)
impressions_w7_sum   BIGINT
impressions_w7_mean  DOUBLE
impressions_w7_vs_prev_abs  DOUBLE
impressions_w7_vs_prev_pct  DOUBLE
-- (Similar for clicks, cost, conversions, conversion_value)

-- Efficiency metrics
ctr_w7_mean          DOUBLE
cpc_w7_mean          DOUBLE
cvr_w7_mean          DOUBLE
cpa_w7_mean          DOUBLE
roas_w7_mean         DOUBLE
-- (vs_prev_pct for each)

-- Metadata
feature_set_version  TEXT
schema_version       INTEGER
generated_at_utc     TIMESTAMP
has_conversion_value BOOLEAN
```

**`analytics.lighthouse_insights_daily`** (Lighthouse output)
```sql
client_id            TEXT
customer_id          TEXT
snapshot_date        DATE
insight_rank         INTEGER
entity_type          TEXT     -- CAMPAIGN, AD_GROUP, KEYWORD, etc.
entity_id            TEXT
diagnosis_code       TEXT     -- LOW_DATA, UNDERPERFORMING, etc.
confidence           DOUBLE   -- 0-1
risk_tier            TEXT     -- low, medium, high
evidence             JSON     -- Supporting metrics
recommended_action   TEXT
guardrail_rule_ids   TEXT[]   -- Constitution references
```

---

## 🔐 SECURITY & SECRETS MANAGEMENT

**Files That Are NEVER Committed:**
```
secrets/
  google-ads.yaml                 # API credentials
  google_ads_client_secret.json   # OAuth client secret
.env                               # Environment variables
warehouse.duckdb                   # Contains client data
warehouse_readonly.duckdb          # Contains client data
*.log                              # May contain sensitive info
```

**Committed Safely:**
```
configs/
  google-ads.example.yaml         # Template only (no real creds)
  client_001.yaml                 # Config (no secrets)
.env.example                       # Template
.gitignore                         # Protection list
```

---

## 🎯 CLIENT CONFIG FLOW

```
Client Config File (YAML)
        ↓
    Loaded by gads_pipeline or Lighthouse
        ↓
    Parsed into Python Objects (config_models.py)
        ↓
    Validated Against Constitution Rules
        ↓
    Used to Filter/Configure Optimizations
        ↓
    Determines automation_mode:
      • insights → No execution
      • suggest → Show recommendations, no execution
      • auto_low_risk → Execute Low-risk only
      • auto_expanded → Execute Low+Medium (approved)
```

**Client Config Structure:**
```yaml
client_name: "Test_Client_001"
client_type: "ecom"              # or lead_gen, mixed
primary_kpi: "roas"              # or cpa

# Required targets
target_roas: 3.0                 # or target_cpa: 50.0

# Google Ads connection
google_ads:
  customer_id: "7372844356"
  mcc_id: "2077923976"

# Safety settings
automation_mode: "suggest"       # insights | suggest | auto_low_risk
risk_tolerance: "conservative"   # conservative | balanced | aggressive

# Spend limits
spend_caps:
  daily: 50
  monthly: 1500

# Protected campaigns (never touch)
protected_entities:
  brand_is_protected: true
  entities: []                   # Optional campaign IDs

# Exclusions
exclusions:
  campaign_types_ignore: ["hotel", "app"]
```

---

## ⚙️ EXECUTION MODES

```
┌─────────────────────────────────────────────────────┐
│  automation_mode: "insights"                        │
│  ┌───────────────────────────────────────────────┐  │
│  │  • Run diagnostics only                       │  │
│  │  • Classify performance                       │  │
│  │  • NO suggestions                             │  │
│  │  • NO execution                               │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  automation_mode: "suggest"                         │
│  ┌───────────────────────────────────────────────┐  │
│  │  • Run full analysis                          │  │
│  │  • Generate recommendations (ALL)             │  │
│  │  • Show in reports                            │  │
│  │  • NO execution                               │  │
│  │  • Human reviews and approves manually        │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  automation_mode: "auto_low_risk"                   │
│  ┌───────────────────────────────────────────────┐  │
│  │  • Generate all recommendations               │  │
│  │  • EXECUTE: Low-risk only (auto)              │  │
│  │  • SUGGEST: Medium/High (need approval)       │  │
│  │  • All changes logged                         │  │
│  │  • Monitored for rollback                     │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│  automation_mode: "auto_expanded"                   │
│  ┌───────────────────────────────────────────────┐  │
│  │  • EXECUTE: Low-risk (auto)                   │  │
│  │  • EXECUTE: Medium-risk (if approved)         │  │
│  │  • SUGGEST: High-risk (always manual)         │  │
│  │  • Requires explicit approval list           │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## 🛡️ GUARDRAILS IN ACTION

**Every optimization passes through these gates:**

```
1. CLIENT CONFIG CHECK
   ├─ Is automation_mode allowing execution?
   ├─ Is risk_tier permitted?
   └─ Are protected_entities respected?

2. DATA QUALITY CHECK
   ├─ Minimum clicks threshold met? (30 clicks / 7d)
   ├─ Minimum conversions met? (15 conv / 30d for bid changes)
   └─ No low-data state?

3. SAFETY LIMITS CHECK
   ├─ Change within ±10% (default)?
   ├─ Cooldown respected? (7 days)
   └─ Not changing multiple levers at once?

4. SPEND CAP CHECK
   ├─ Daily cap not breached?
   ├─ Monthly projection OK?
   └─ No overspend risk?

5. TRACKING INTEGRITY CHECK
   ├─ Conversions tracking properly?
   ├─ No recent tracking anomalies?
   └─ Value data reliable?

6. BUSINESS RULES CHECK
   ├─ Campaign not in protected list?
   ├─ Brand campaigns safe?
   └─ Campaign type allowed?

     ✅ ALL PASSED?
          ↓
    EXECUTE CHANGE
          ↓
    LOG + MONITOR + READY TO ROLLBACK
```

---

## 🎯 KEY METRICS TRACKED

**Performance Metrics:**
- Impressions, Clicks, Cost
- Conversions, Conversion Value
- CTR, CPC, CVR, CPA, ROAS

**Diagnostic Metrics:**
- Impression Share (Total, Lost to Budget, Lost to Rank)
- Quality Score
- Search Impression Share
- Ad Strength

**Trend Metrics (Lighthouse):**
- 7-day vs 30-day deltas
- Period-over-period % change
- Acceleration/deceleration

**Opportunity Metrics:**
- Budget-constrained campaigns (Lost IS Budget > 15%)
- Rank-constrained keywords (Lost IS Rank > 20%)
- Low-CTR ads (CTR < avg - 30%)
- High-CPA keywords (CPA > target * 1.5)
- Wasted spend queries (Cost > X, Conv = 0)

---

This architecture is designed for **safety, transparency, and scalability** while maintaining full human oversight where needed. 🚀
