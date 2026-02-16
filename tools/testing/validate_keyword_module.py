r"""
Keyword Module — Full Validation Suite
========================================
Tests all keyword components end-to-end:
  1. Schema integrity (tables, columns, views)
  2. Synthetic data integrity (row counts, value ranges, scenarios)
  3. Keyword features correctness (calculations, windows, derived metrics)
  4. Keyword diagnostics (insight generation, codes, confidence)
  5. Keyword rules (14 rules, trigger conditions, recommendation quality)
  6. Cross-module consistency (features → diagnostics → rules alignment)
  7. Dashboard route smoke test

Usage:
  cd C:\Users\User\Desktop\gads-data-layer
  .\.venv\Scripts\Activate.ps1
  python tools/testing/validate_keyword_module.py
"""

import sys
from datetime import date, timedelta
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import duckdb

# ═══════════════════════════════════════════════════════════════
# Test infrastructure
# ═══════════════════════════════════════════════════════════════

PASS_COUNT = 0
FAIL_COUNT = 0
WARN_COUNT = 0
RESULTS = []


def check(name, condition, detail=""):
    global PASS_COUNT, FAIL_COUNT
    if condition:
        PASS_COUNT += 1
        RESULTS.append(("PASS", name, detail))
        print(f"  \033[92mPASS\033[0m  {name}")
    else:
        FAIL_COUNT += 1
        RESULTS.append(("FAIL", name, detail))
        print(f"  \033[91mFAIL\033[0m  {name}  — {detail}")


def warn(name, detail=""):
    global WARN_COUNT
    WARN_COUNT += 1
    RESULTS.append(("WARN", name, detail))
    print(f"  \033[93mWARN\033[0m  {name}  — {detail}")


def section(title):
    print()
    print(f"{'─' * 60}")
    print(f"  {title}")
    print(f"{'─' * 60}")


# ═══════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════

DB_PATH = str(PROJECT_ROOT / "warehouse.duckdb")
RO_PATH = str(PROJECT_ROOT / "warehouse_readonly.duckdb")
CONFIG_PATH = str(PROJECT_ROOT / "configs" / "client_synthetic.yaml")
SNAPSHOT_DATE = date(2026, 2, 13)
CLIENT_ID = "Synthetic_Test_Client"
CUSTOMER_ID = "1234567890"
TARGET_CPA_DOLLARS = 25.0
TARGET_CPA_MICROS = TARGET_CPA_DOLLARS * 1_000_000


def main():
    print("=" * 60)
    print("  KEYWORD MODULE — FULL VALIDATION SUITE")
    print("=" * 60)
    print(f"  DB:       {DB_PATH}")
    print(f"  RO DB:    {RO_PATH}")
    print(f"  Config:   {CONFIG_PATH}")
    print(f"  Snapshot: {SNAPSHOT_DATE}")
    print(f"  Client:   {CLIENT_ID}")

    con = duckdb.connect(DB_PATH)
    con.execute(f"ATTACH '{RO_PATH}' AS ro (READ_ONLY);")

    # Auto-detect customer_id from features table (synthetic data)
    global CUSTOMER_ID
    try:
        detected = con.execute("""
            SELECT DISTINCT CAST(customer_id AS VARCHAR)
            FROM analytics.keyword_features_daily
            WHERE client_id = ? LIMIT 1
        """, [CLIENT_ID]).fetchone()
        if detected:
            CUSTOMER_ID = detected[0]
            print(f"  Customer ID (from features): {CUSTOMER_ID}")
        else:
            # Fallback: raw data
            detected2 = con.execute("""
                SELECT DISTINCT CAST(customer_id AS VARCHAR)
                FROM ro.analytics.keyword_daily LIMIT 1
            """).fetchone()
            if detected2:
                CUSTOMER_ID = detected2[0]
                print(f"  Customer ID (from raw): {CUSTOMER_ID}")
    except Exception:
        pass

    test_1_schema(con)
    test_2_synthetic_data(con)
    test_3_keyword_features(con)
    test_4_keyword_diagnostics(con)
    test_5_keyword_rules(con)
    test_6_cross_module(con)
    test_7_dashboard()

    con.close()

    # ── Final report ──
    print()
    print("=" * 60)
    print("  FINAL REPORT")
    print("=" * 60)
    print(f"  PASS: {PASS_COUNT}")
    print(f"  FAIL: {FAIL_COUNT}")
    print(f"  WARN: {WARN_COUNT}")
    print()

    if FAIL_COUNT > 0:
        print("  FAILURES:")
        for status, name, detail in RESULTS:
            if status == "FAIL":
                print(f"    • {name}: {detail}")
        print()
        print(f"  RESULT: \033[91mFAIL ({FAIL_COUNT} failures)\033[0m")
    else:
        print(f"  RESULT: \033[92mALL {PASS_COUNT} CHECKS PASSED\033[0m")
        if WARN_COUNT > 0:
            print(f"  ({WARN_COUNT} warnings)")

    return 1 if FAIL_COUNT > 0 else 0


# ═══════════════════════════════════════════════════════════════
# TEST 1: Schema Integrity
# ═══════════════════════════════════════════════════════════════

def test_1_schema(con):
    section("1. SCHEMA INTEGRITY")

    # Check keyword_daily table in readonly
    try:
        cols = con.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_schema = 'analytics' AND table_name = 'keyword_daily'
            AND table_catalog = 'ro'
        """).fetchall()
        col_names = {c[0] for c in cols}
        check("keyword_daily table exists", len(col_names) > 0)

        required_kw_cols = {
            "customer_id", "campaign_id", "ad_group_id", "keyword_id",
            "keyword_text", "match_type", "status", "quality_score",
            "impressions", "clicks", "cost_micros", "conversions",
            "snapshot_date"
        }
        missing = required_kw_cols - col_names
        check("keyword_daily has required columns", len(missing) == 0,
              f"Missing: {missing}" if missing else "")
    except Exception as e:
        check("keyword_daily table exists", False, str(e))

    # Check search_term_daily table in readonly
    try:
        cols = con.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_schema = 'analytics' AND table_name = 'search_term_daily'
            AND table_catalog = 'ro'
        """).fetchall()
        col_names = {c[0] for c in cols}
        check("search_term_daily table exists", len(col_names) > 0)

        required_st_cols = {
            "customer_id", "campaign_id", "search_term",
            "search_term_status", "impressions", "clicks",
            "cost_micros", "conversions", "snapshot_date"
        }
        missing = required_st_cols - col_names
        check("search_term_daily has required columns", len(missing) == 0,
              f"Missing: {missing}" if missing else "")
    except Exception as e:
        check("search_term_daily table exists", False, str(e))

    # Check keyword_features_daily in analytics
    try:
        cols = con.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_schema = 'analytics' AND table_name = 'keyword_features_daily'
        """).fetchall()
        col_names = {c[0] for c in cols}
        check("keyword_features_daily table exists", len(col_names) > 0)

        required_feat_cols = {
            "client_id", "customer_id", "keyword_id", "snapshot_date",
            "clicks_w7_sum", "clicks_w30_sum", "cost_micros_w30_sum",
            "conversions_w30_sum", "ctr_w7", "cvr_w30", "cpa_w30",
            "quality_score", "low_data_flag"
        }
        missing = required_feat_cols - col_names
        check("keyword_features_daily has required columns", len(missing) == 0,
              f"Missing: {missing}" if missing else "")
    except Exception as e:
        check("keyword_features_daily table exists", False, str(e))


# ═══════════════════════════════════════════════════════════════
# TEST 2: Synthetic Data Integrity
# ═══════════════════════════════════════════════════════════════

def test_2_synthetic_data(con):
    section("2. SYNTHETIC DATA INTEGRITY")

    # Keyword row count
    kw_count = con.execute("""
        SELECT COUNT(*) FROM ro.analytics.keyword_daily
        WHERE customer_id = ?
    """, [CUSTOMER_ID]).fetchone()[0]
    check("keyword_daily has data", kw_count > 0, f"{kw_count} rows")
    check("keyword_daily >= 50k rows", kw_count >= 50000, f"{kw_count} rows")

    # Search term row count
    st_count = con.execute("""
        SELECT COUNT(*) FROM ro.analytics.search_term_daily
        WHERE customer_id = ?
    """, [CUSTOMER_ID]).fetchone()[0]
    check("search_term_daily has data", st_count > 0, f"{st_count} rows")
    check("search_term_daily >= 30k rows", st_count >= 30000, f"{st_count} rows")

    # Unique keywords
    unique_kw = con.execute("""
        SELECT COUNT(DISTINCT keyword_id) FROM ro.analytics.keyword_daily
        WHERE customer_id = ?
    """, [CUSTOMER_ID]).fetchone()[0]
    check("unique keywords >= 50", unique_kw >= 50, f"{unique_kw} unique")

    # Unique search terms
    unique_st = con.execute("""
        SELECT COUNT(DISTINCT search_term) FROM ro.analytics.search_term_daily
        WHERE customer_id = ?
    """, [CUSTOMER_ID]).fetchone()[0]
    check("unique search terms >= 50", unique_st >= 50, f"{unique_st} unique")

    # Date range coverage
    date_range = con.execute("""
        SELECT MIN(snapshot_date), MAX(snapshot_date)
        FROM ro.analytics.keyword_daily
        WHERE customer_id = ?
    """, [CUSTOMER_ID]).fetchone()
    min_date, max_date = date_range
    days_covered = (max_date - min_date).days if min_date and max_date else 0
    check("keyword data covers >= 90 days", days_covered >= 89, f"{days_covered} days ({min_date} to {max_date})")

    # No negative values in key metrics
    neg_check = con.execute("""
        SELECT
            COUNT(CASE WHEN impressions < 0 THEN 1 END) as neg_impr,
            COUNT(CASE WHEN clicks < 0 THEN 1 END) as neg_clicks,
            COUNT(CASE WHEN cost_micros < 0 THEN 1 END) as neg_cost,
            COUNT(CASE WHEN conversions < 0 THEN 1 END) as neg_conv
        FROM ro.analytics.keyword_daily
        WHERE customer_id = ?
    """, [CUSTOMER_ID]).fetchone()
    total_neg = sum(neg_check)
    check("no negative metric values", total_neg == 0,
          f"negatives: impr={neg_check[0]} clicks={neg_check[1]} cost={neg_check[2]} conv={neg_check[3]}")

    # Quality score distribution (should be 1-10)
    qs_range = con.execute("""
        SELECT MIN(quality_score), MAX(quality_score),
               COUNT(DISTINCT quality_score)
        FROM ro.analytics.keyword_daily
        WHERE customer_id = ? AND quality_score IS NOT NULL
    """, [CUSTOMER_ID]).fetchone()
    if qs_range[0] is not None:
        check("quality score range 1-10", qs_range[0] >= 1 and qs_range[1] <= 10,
              f"range: {qs_range[0]}-{qs_range[1]}, {qs_range[2]} distinct values")
    else:
        warn("quality score data", "No quality scores found")

    # Match type distribution
    mt_dist = con.execute("""
        SELECT match_type, COUNT(DISTINCT keyword_id) as cnt
        FROM ro.analytics.keyword_daily
        WHERE customer_id = ?
        GROUP BY match_type ORDER BY cnt DESC
    """, [CUSTOMER_ID]).fetchall()
    match_types = {m[0] for m in mt_dist}
    expected_mt = {"EXACT", "PHRASE", "BROAD"}
    check("all 3 match types present", expected_mt.issubset(match_types),
          f"found: {match_types}")

    # Campaign coverage
    campaigns = con.execute("""
        SELECT COUNT(DISTINCT campaign_id)
        FROM ro.analytics.keyword_daily
        WHERE customer_id = ?
    """, [CUSTOMER_ID]).fetchone()[0]
    check("multiple campaigns", campaigns >= 5, f"{campaigns} campaigns")


# ═══════════════════════════════════════════════════════════════
# TEST 3: Keyword Features Correctness
# ═══════════════════════════════════════════════════════════════

def test_3_keyword_features(con):
    section("3. KEYWORD FEATURES")

    # Feature row count for snapshot
    feat_count = con.execute("""
        SELECT COUNT(*) FROM analytics.keyword_features_daily
        WHERE client_id = ? AND snapshot_date = ?
    """, [CLIENT_ID, SNAPSHOT_DATE]).fetchone()[0]
    check("features generated for snapshot", feat_count > 0, f"{feat_count} rows")
    check("features count 900-1000", 900 <= feat_count <= 1000, f"{feat_count} rows")

    # No features for paused keywords
    paused_feats = con.execute("""
        SELECT COUNT(*) FROM analytics.keyword_features_daily f
        WHERE f.client_id = ? AND f.snapshot_date = ?
          AND f.status = 'PAUSED'
    """, [CLIENT_ID, SNAPSHOT_DATE]).fetchone()[0]
    check("no paused keywords in features", paused_feats == 0, f"{paused_feats} paused")

    # Spot-check: CTR calculation (clicks / impressions)
    spot = con.execute("""
        SELECT keyword_id, clicks_w7_sum, impressions_w7_sum, ctr_w7
        FROM analytics.keyword_features_daily
        WHERE client_id = ? AND snapshot_date = ?
          AND impressions_w7_sum > 100 AND clicks_w7_sum > 0
        LIMIT 5
    """, [CLIENT_ID, SNAPSHOT_DATE]).fetchall()
    ctr_errors = 0
    for row in spot:
        kid, clicks, impr, ctr = row
        expected_ctr = float(clicks) / float(impr) if impr > 0 else 0
        if ctr is not None and abs(float(ctr) - expected_ctr) > 0.001:
            ctr_errors += 1
    check("CTR calculation correct (spot check)", ctr_errors == 0,
          f"{ctr_errors} mismatches in {len(spot)} checked")

    # Spot-check: CPA calculation (cost / conversions)
    spot_cpa = con.execute("""
        SELECT keyword_id, cost_micros_w30_sum, conversions_w30_sum, cpa_w30
        FROM analytics.keyword_features_daily
        WHERE client_id = ? AND snapshot_date = ?
          AND conversions_w30_sum > 0
        LIMIT 5
    """, [CLIENT_ID, SNAPSHOT_DATE]).fetchall()
    cpa_errors = 0
    for row in spot_cpa:
        kid, cost, conv, cpa = row
        expected_cpa = float(cost) / float(conv) if conv > 0 else 0
        if cpa is not None and abs(float(cpa) - expected_cpa) > 1:  # allow 1 micro tolerance
            cpa_errors += 1
    check("CPA calculation correct (spot check)", cpa_errors == 0,
          f"{cpa_errors} mismatches in {len(spot_cpa)} checked")

    # Low data flags
    low_data = con.execute("""
        SELECT
            COUNT(*) as total,
            COUNT(CASE WHEN low_data_flag = TRUE THEN 1 END) as flagged,
            COUNT(CASE WHEN low_data_clicks_7d = TRUE THEN 1 END) as ld_clicks,
            COUNT(CASE WHEN low_data_conversions_30d = TRUE THEN 1 END) as ld_conv
        FROM analytics.keyword_features_daily
        WHERE client_id = ? AND snapshot_date = ?
    """, [CLIENT_ID, SNAPSHOT_DATE]).fetchone()
    check("low_data_flag populated", low_data[1] > 0,
          f"{low_data[1]}/{low_data[0]} flagged (clicks:{low_data[2]}, conv:{low_data[3]})")

    # Window completeness: 7d, 14d, 30d columns exist and populated
    windows = con.execute("""
        SELECT
            COUNT(CASE WHEN clicks_w7_sum IS NOT NULL THEN 1 END) as w7,
            COUNT(CASE WHEN clicks_w14_sum IS NOT NULL THEN 1 END) as w14,
            COUNT(CASE WHEN clicks_w30_sum IS NOT NULL THEN 1 END) as w30
        FROM analytics.keyword_features_daily
        WHERE client_id = ? AND snapshot_date = ?
    """, [CLIENT_ID, SNAPSHOT_DATE]).fetchone()
    check("7d window populated", windows[0] == feat_count)
    check("14d window populated", windows[1] == feat_count)
    check("30d window populated", windows[2] == feat_count)

    # Quality score tracking
    qs_pop = con.execute("""
        SELECT COUNT(CASE WHEN quality_score IS NOT NULL THEN 1 END)
        FROM analytics.keyword_features_daily
        WHERE client_id = ? AND snapshot_date = ?
    """, [CLIENT_ID, SNAPSHOT_DATE]).fetchone()[0]
    check("quality score populated in features", qs_pop > feat_count * 0.5,
          f"{qs_pop}/{feat_count} have QS")


# ═══════════════════════════════════════════════════════════════
# TEST 4: Keyword Diagnostics
# ═══════════════════════════════════════════════════════════════

def test_4_keyword_diagnostics(con):
    section("4. KEYWORD DIAGNOSTICS")

    from act_lighthouse.config import load_client_config
    from act_lighthouse.keyword_diagnostics import (
        run_keyword_diagnostics,
        run_search_term_diagnostics,
        compute_campaign_averages,
        load_search_term_aggregates,
    )

    cfg = load_client_config(CONFIG_PATH)
    targets = (cfg.raw or {}).get("targets", {})
    target_cpa_micros = float(targets.get("target_cpa", TARGET_CPA_DOLLARS)) * 1_000_000
    target_roas = float(targets.get("target_roas", 3.0))

    # Load features
    kw_rows = con.execute("""
        SELECT * FROM analytics.keyword_features_daily
        WHERE client_id = ? AND snapshot_date = ?
    """, [CLIENT_ID, SNAPSHOT_DATE]).fetchall()
    kw_cols = [d[0] for d in con.description]
    features = [dict(zip(kw_cols, r)) for r in kw_rows]

    # Campaign averages
    avg_ctrs, avg_cvrs = compute_campaign_averages(
        con, CUSTOMER_ID, SNAPSHOT_DATE, 7
    )
    check("campaign avg CTRs computed", len(avg_ctrs) > 0, f"{len(avg_ctrs)} campaigns")
    check("campaign avg CVRs computed", len(avg_cvrs) > 0, f"{len(avg_cvrs)} campaigns")

    # Run keyword diagnostics
    kw_insights = []
    for feat in features:
        cid = str(feat.get("campaign_id", ""))
        campaign_avg_ctr = avg_ctrs.get(cid, 0)
        insights = run_keyword_diagnostics(
            feat, target_cpa_micros, target_roas, campaign_avg_ctr,
            cfg.protected_campaign_ids
        )
        kw_insights.extend(insights)

    check("keyword insights generated", len(kw_insights) > 0, f"{len(kw_insights)} insights")

    # Count by code
    code_counts = {}
    for ins in kw_insights:
        code = ins.diagnosis_code
        code_counts[code] = code_counts.get(code, 0) + 1

    expected_codes = {"KEYWORD_HIGH_CPA", "KEYWORD_LOW_QS", "KEYWORD_WASTED_SPEND", "KEYWORD_LOW_CTR"}
    found_codes = set(code_counts.keys())
    check("all 4 keyword diagnosis codes fire", expected_codes.issubset(found_codes),
          f"found: {found_codes}, missing: {expected_codes - found_codes}")

    for code in sorted(expected_codes):
        cnt = code_counts.get(code, 0)
        check(f"  {code} > 0", cnt > 0, f"{cnt} insights")

    # Confidence bounds
    bad_conf = [i for i in kw_insights if i.confidence < 0 or i.confidence > 1.0]
    check("all confidences in [0, 1]", len(bad_conf) == 0,
          f"{len(bad_conf)} out of range")

    # Search term diagnostics
    st_rows = load_search_term_aggregates(con, CUSTOMER_ID, SNAPSHOT_DATE, 30)
    _, avg_cvrs_30 = compute_campaign_averages(con, CUSTOMER_ID, SNAPSHOT_DATE, 30)
    st_insights = run_search_term_diagnostics(st_rows, avg_cvrs_30)

    check("search term insights generated", len(st_insights) > 0, f"{len(st_insights)} insights")

    st_codes = {}
    for ins in st_insights:
        st_codes[ins.diagnosis_code] = st_codes.get(ins.diagnosis_code, 0) + 1

    expected_st_codes = {"SEARCH_TERM_WINNER", "SEARCH_TERM_NEGATIVE"}
    check("both search term codes fire", expected_st_codes.issubset(set(st_codes.keys())),
          f"found: {set(st_codes.keys())}")


# ═══════════════════════════════════════════════════════════════
# TEST 5: Keyword Rules (14 rules)
# ═══════════════════════════════════════════════════════════════

def test_5_keyword_rules(con):
    section("5. KEYWORD RULES (14)")

    from act_lighthouse.config import load_client_config
    from act_lighthouse.keyword_diagnostics import compute_campaign_averages
    from act_autopilot.models import AutopilotConfig, RuleContext, _safe_float
    from act_autopilot.rules.keyword_rules import (
        KEYWORD_RULES, SEARCH_TERM_RULES, ALL_KEYWORD_RULES,
        _target_cpa_micros,
    )
    from act_lighthouse.keyword_diagnostics import load_search_term_aggregates

    cfg = load_client_config(CONFIG_PATH)
    raw = cfg.raw or {}
    targets = raw.get("targets", {})

    ap_config = AutopilotConfig(
        customer_id=cfg.customer_id,
        automation_mode="suggest",
        risk_tolerance="conservative",
        daily_spend_cap=cfg.spend_caps.daily or 0,
        monthly_spend_cap=cfg.spend_caps.monthly or 0,
        brand_is_protected=False,
        protected_entities=[],
        client_name=CLIENT_ID,
        client_type="ecom",
        primary_kpi="roas",
        target_roas=targets.get("target_roas"),
        target_cpa=targets.get("target_cpa", 25),
    )

    # Verify target CPA helper
    tcpa = _target_cpa_micros(ap_config)
    check("_target_cpa_micros converts correctly",
          abs(tcpa - TARGET_CPA_MICROS) < 1000,
          f"expected {TARGET_CPA_MICROS}, got {tcpa}")

    # Load features
    kw_rows = con.execute("""
        SELECT * FROM analytics.keyword_features_daily
        WHERE client_id = ? AND snapshot_date = ?
    """, [CLIENT_ID, SNAPSHOT_DATE]).fetchall()
    kw_cols = [d[0] for d in con.description]
    features = [dict(zip(kw_cols, r)) for r in kw_rows]

    avg_ctrs, avg_cvrs = compute_campaign_averages(
        con, CUSTOMER_ID, SNAPSHOT_DATE, 7
    )
    _, avg_cvrs_30 = compute_campaign_averages(
        con, CUSTOMER_ID, SNAPSHOT_DATE, 30
    )

    for f in features:
        cid = str(f.get("campaign_id", ""))
        f["_campaign_avg_ctr"] = avg_ctrs.get(cid, 0)
        f["_campaign_avg_cvr"] = avg_cvrs.get(cid, 0)

    # Run keyword rules
    kw_recs = []
    errors = 0
    for feat in features:
        ctx = RuleContext(
            customer_id=CUSTOMER_ID,
            campaign_id=str(feat.get("campaign_id", "")),
            snapshot_date=SNAPSHOT_DATE,
            features=feat,
            insights=[],
            config=ap_config,
            db_path=DB_PATH,
        )
        for rule_fn in KEYWORD_RULES:
            try:
                rec = rule_fn(ctx)
                if rec is not None:
                    kw_recs.append(rec)
            except Exception as e:
                errors += 1

    check("keyword rules execute without errors", errors == 0, f"{errors} errors")
    check("keyword rules generate recommendations", len(kw_recs) > 0, f"{len(kw_recs)} recs")

    # Count by rule
    kw_counts = {}
    for r in kw_recs:
        kw_counts[r.rule_id] = kw_counts.get(r.rule_id, 0) + 1

    # Expected keyword rules
    kw_expected = {
        "KW-PAUSE-001", "KW-PAUSE-002", "KW-PAUSE-003",
        "KW-BID-001", "KW-BID-002", "KW-BID-003",
        "KW-REVIEW-001", "KW-REVIEW-002",
    }
    kw_optional = {"KW-REVIEW-003"}  # May not fire on synthetic data

    for rule_id in sorted(kw_expected):
        cnt = kw_counts.get(rule_id, 0)
        check(f"  {rule_id} fires", cnt > 0, f"{cnt} recs")

    for rule_id in sorted(kw_optional):
        cnt = kw_counts.get(rule_id, 0)
        if cnt == 0:
            warn(f"  {rule_id} did not fire", "Expected on real data, OK for synthetic")
        else:
            check(f"  {rule_id} fires", True, f"{cnt} recs")

    # Run search term rules
    st_rows = load_search_term_aggregates(con, CUSTOMER_ID, SNAPSHOT_DATE, 30)
    for st in st_rows:
        cid = str(st.get("campaign_id", ""))
        st["_campaign_avg_cvr"] = avg_cvrs_30.get(cid, 0)
        st["_campaign_avg_cpc"] = 0

    st_recs = []
    st_errors = 0
    for st in st_rows:
        ctx = RuleContext(
            customer_id=CUSTOMER_ID,
            campaign_id=str(st.get("campaign_id", "")),
            snapshot_date=SNAPSHOT_DATE,
            features=st,
            insights=[],
            config=ap_config,
            db_path=DB_PATH,
        )
        for rule_fn in SEARCH_TERM_RULES:
            try:
                rec = rule_fn(ctx)
                if rec is not None:
                    st_recs.append(rec)
            except Exception as e:
                st_errors += 1

    check("search term rules execute without errors", st_errors == 0, f"{st_errors} errors")
    check("search term rules generate recommendations", len(st_recs) > 0, f"{len(st_recs)} recs")

    st_counts = {}
    for r in st_recs:
        st_counts[r.rule_id] = st_counts.get(r.rule_id, 0) + 1

    st_expected = {"ST-ADD-001", "ST-ADD-002", "ST-NEG-001", "ST-NEG-003"}
    st_optional = {"ST-NEG-002"}  # Requires very specific CPC pattern, may not fire on synthetic
    for rule_id in sorted(st_expected):
        cnt = st_counts.get(rule_id, 0)
        check(f"  {rule_id} fires", cnt > 0, f"{cnt} recs")
    for rule_id in sorted(st_optional):
        cnt = st_counts.get(rule_id, 0)
        if cnt == 0:
            warn(f"  {rule_id} did not fire", "Requires specific CPC pattern, OK for synthetic")
        else:
            check(f"  {rule_id} fires", True, f"{cnt} recs")

    # Recommendation quality checks
    all_recs = kw_recs + st_recs

    # All have required fields
    bad_recs = [r for r in all_recs if not r.rule_id or not r.entity_type or not r.risk_tier]
    check("all recs have required fields", len(bad_recs) == 0,
          f"{len(bad_recs)} incomplete")

    # Risk tiers are valid
    valid_tiers = {"low", "med", "medium", "high"}
    bad_tiers = [r for r in all_recs if r.risk_tier not in valid_tiers]
    check("all risk tiers valid", len(bad_tiers) == 0,
          f"{len(bad_tiers)} invalid tiers")

    # Confidence in [0, 1]
    bad_conf = [r for r in all_recs if r.confidence < 0 or r.confidence > 1.0]
    check("all rec confidences in [0, 1]", len(bad_conf) == 0,
          f"{len(bad_conf)} out of range")

    # Change pct within Constitution limits (max ±20% for bids)
    bid_recs = [r for r in all_recs if "bid" in r.action_type and r.change_pct is not None]
    bad_pct = [r for r in bid_recs if abs(r.change_pct) > 0.20]
    check("bid changes within ±20% limit", len(bad_pct) == 0,
          f"{len(bad_pct)} exceed limit")

    # CPA ratios are sensible (not millions:1)
    for r in kw_recs:
        if r.evidence and "cpa_ratio" in r.evidence:
            ratio = r.evidence["cpa_ratio"]
            if ratio > 100:
                check("CPA ratios sensible (not micros vs dollars)", False,
                      f"{r.rule_id} entity {r.entity_id}: ratio={ratio}")
                break
    else:
        check("CPA ratios sensible (not micros vs dollars)", True)


# ═══════════════════════════════════════════════════════════════
# TEST 6: Cross-Module Consistency
# ═══════════════════════════════════════════════════════════════

def test_6_cross_module(con):
    section("6. CROSS-MODULE CONSISTENCY")

    # Features count matches active keyword count in raw data
    raw_active = con.execute("""
        SELECT COUNT(DISTINCT keyword_id) FROM ro.analytics.keyword_daily
        WHERE customer_id = ? AND snapshot_date = ?
          AND status = 'ENABLED'
    """, [CUSTOMER_ID, SNAPSHOT_DATE]).fetchone()[0]

    feat_count = con.execute("""
        SELECT COUNT(*) FROM analytics.keyword_features_daily
        WHERE client_id = ? AND snapshot_date = ?
    """, [CLIENT_ID, SNAPSHOT_DATE]).fetchone()[0]

    check("features count ≈ active keywords",
          abs(feat_count - raw_active) <= raw_active * 0.1,
          f"features={feat_count}, raw_active={raw_active}")

    # Wasted spend keywords in features should trigger KW-PAUSE-001
    wasted = con.execute("""
        SELECT COUNT(*) FROM analytics.keyword_features_daily
        WHERE client_id = ? AND snapshot_date = ?
          AND conversions_w30_sum = 0
          AND cost_micros_w30_sum > 50000000
          AND clicks_w30_sum >= 10
    """, [CLIENT_ID, SNAPSHOT_DATE]).fetchone()[0]
    check("wasted spend keywords identified in features", wasted > 0, f"{wasted} keywords")

    # Low QS keywords in features should trigger diagnostics
    low_qs = con.execute("""
        SELECT COUNT(*) FROM analytics.keyword_features_daily
        WHERE client_id = ? AND snapshot_date = ?
          AND quality_score IS NOT NULL AND quality_score <= 3
    """, [CLIENT_ID, SNAPSHOT_DATE]).fetchone()[0]
    check("low QS keywords in features", low_qs > 0, f"{low_qs} keywords")

    # Search terms aggregate correctly
    st_raw_count = con.execute("""
        SELECT COUNT(DISTINCT search_term) FROM ro.analytics.search_term_daily
        WHERE customer_id = ?
          AND snapshot_date BETWEEN ? AND ?
    """, [CUSTOMER_ID, SNAPSHOT_DATE - timedelta(days=29), SNAPSHOT_DATE]).fetchone()[0]
    check("search terms found in 30d window", st_raw_count > 0, f"{st_raw_count} terms")


# ═══════════════════════════════════════════════════════════════
# TEST 7: Dashboard Smoke Test
# ═══════════════════════════════════════════════════════════════

def test_7_dashboard():
    section("7. DASHBOARD SMOKE TEST")

    try:
        from act_dashboard.app import create_app
        app = create_app()

        with app.test_client() as client:
            # Login first
            client.post("/login", data={"username": "admin", "password": "admin123"})

            # Hit keywords page
            resp = client.get("/keywords")
            check("GET /keywords returns 200", resp.status_code == 200,
                  f"status={resp.status_code}")

            html = resp.data.decode("utf-8")
            check("/keywords contains keyword table", "kw-table" in html)
            check("/keywords contains search terms tab", "tab-search-terms" in html)
            check("/keywords contains recommendations tab", "tab-recommendations" in html)
            check("/keywords shows keyword count", "940" in html or "Keywords (" in html)

    except Exception as e:
        check("dashboard imports and runs", False, str(e))
        import traceback
        traceback.print_exc()


# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    raise SystemExit(main())
