# ACT v2 Database Migrations

## Scripts

| Script | Purpose |
|--------|---------|
| `create_act_v2_schema.py` | Creates all 11 `act_v2_*` tables, 5 sequences, 5 indexes, and populates the 35 checks reference table |
| `seed_objection_experts.py` | Seeds Objection Experts as the first client with 6 level states, 45 settings, and 9 negative keyword lists |
| `rollback_act_v2_schema.py` | **DESTRUCTIVE** — drops all `act_v2_*` tables and sequences (interactive confirmation required) |
| `verify_act_v2_schema.py` | Verifies all tables, columns, sequences, indexes, and seed data exist correctly |

## Execution Order

1. **Stop Flask first** — DuckDB locks the database file:
   ```
   taskkill /IM python.exe /F
   ```

2. **Create schema:**
   ```
   python -m act_dashboard.db.migrations.create_act_v2_schema
   ```

3. **Seed first client:**
   ```
   python -m act_dashboard.db.migrations.seed_objection_experts
   ```

4. **Verify everything:**
   ```
   python -m act_dashboard.db.migrations.verify_act_v2_schema
   ```

All scripts must be run from the **project root directory**.

## Rollback (emergency only)

```
python -m act_dashboard.db.migrations.rollback_act_v2_schema
```

Requires typing `YES` to confirm. Drops all `act_v2_*` tables and data permanently.

## Idempotency

All scripts (except rollback) are idempotent — safe to run multiple times.

## Log File

All operations are logged to `act_dashboard/db/migrations/migration.log` (append mode).
