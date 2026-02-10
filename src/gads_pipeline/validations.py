from collections import Counter

def validate_nonempty(rows: list[dict]) -> tuple[bool, dict]:
    return (len(rows) > 0, {"row_count": len(rows)})

def validate_single_day(rows: list[dict], expected_date) -> tuple[bool, dict]:
    dates = {r["snapshot_date"] for r in rows}
    ok = (len(dates) == 1 and expected_date in dates)
    return (ok, {"dates_seen": [str(d) for d in sorted(dates)], "expected": str(expected_date)})

def validate_no_duplicate_keys(rows: list[dict]) -> tuple[bool, dict]:
    keys = [(r["customer_id"], r["snapshot_date"], r["campaign_id"]) for r in rows]
    c = Counter(keys)
    dups = [k for k, v in c.items() if v > 1]
    return (len(dups) == 0, {"duplicate_keys": [str(x) for x in dups][:20]})
