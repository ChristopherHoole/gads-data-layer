import duckdb
con = duckdb.connect(r'C:\Users\User\Desktop\gads-data-layer\warehouse.duckdb', read_only=True)
r = con.execute("""SELECT MIN(reviewed_at), MAX(reviewed_at), DATE_DIFF('minute', MIN(reviewed_at), MAX(reviewed_at)) FROM act_v2_search_term_reviews WHERE client_id='dbd001' AND analysis_date='2026-04-30' AND reviewed_at IS NOT NULL""").fetchone()
print('First review:', r[0])
print('Last review:', r[1])
print('Span (min):', r[2])
