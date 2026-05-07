"""Today's triage — clean breakdown."""
import duckdb
DB = r'C:\Users\User\Desktop\gads-data-layer\warehouse.duckdb'
con = duckdb.connect(DB, read_only=True)

print("=== Today's review_status counts ===")
rows = con.execute("""
    SELECT review_status, COUNT(*) n
    FROM act_v2_search_term_reviews
    WHERE client_id='dbd001' AND analysis_date='2026-04-30'
    GROUP BY 1 ORDER BY 1
""").fetchall()
for r in rows: print(f"  {r}")

print("\n=== Pushed today (pushed_to_ads_at IS NOT NULL) ===")
n = con.execute("""
    SELECT COUNT(*)
    FROM act_v2_search_term_reviews
    WHERE client_id='dbd001' AND analysis_date='2026-04-30'
      AND pushed_to_ads_at IS NOT NULL
""").fetchone()[0]
print(f"  Pushed to GAds today: {n}")

# Reviewed by
print("\n=== Reviewed_by breakdown today ===")
rows = con.execute("""
    SELECT reviewed_by, COUNT(*) n
    FROM act_v2_search_term_reviews
    WHERE client_id='dbd001' AND analysis_date='2026-04-30' AND reviewed_by IS NOT NULL
    GROUP BY 1
""").fetchall()
for r in rows: print(f"  {r}")

# Cost / volume of pushed terms
print("\n=== Today's pushed terms by total cost ===")
rows = con.execute("""
    SELECT search_term, total_cost, total_clicks, total_conversions, pass1_status, pass2_target_list_role
    FROM act_v2_search_term_reviews
    WHERE client_id='dbd001' AND analysis_date='2026-04-30'
      AND pushed_to_ads_at IS NOT NULL
    ORDER BY total_cost DESC
    LIMIT 15
""").fetchall()
for r in rows: print(f"  {r}")

# Pass 1 status breakdown
print("\n=== Pass1 status (rule decision before AI) ===")
rows = con.execute("""
    SELECT pass1_status, COUNT(*) n
    FROM act_v2_search_term_reviews
    WHERE client_id='dbd001' AND analysis_date='2026-04-30'
    GROUP BY 1 ORDER BY 2 DESC
""").fetchall()
for r in rows: print(f"  {r}")

# AI usage today
print("\n=== AI calls today ===")
rows = con.execute("""
    SELECT ai_verdict, COUNT(*) n,
           ROUND(AVG(ai_confidence),2) avg_conf
    FROM act_v2_ai_classifications
    WHERE client_id='dbd001' AND analysis_date='2026-04-30'
    GROUP BY 1 ORDER BY 1
""").fetchall()
for r in rows: print(f"  {r}")

# When was activity? Time spread
print("\n=== Reviewed_at time spread today ===")
rows = con.execute("""
    SELECT MIN(reviewed_at), MAX(reviewed_at),
           DATE_DIFF('minute', MIN(reviewed_at), MAX(reviewed_at)) AS span_minutes,
           COUNT(*) n
    FROM act_v2_search_term_reviews
    WHERE client_id='dbd001' AND analysis_date='2026-04-30' AND reviewed_at IS NOT NULL
""").fetchall()
for r in rows: print(f"  {r}")

con.close()
