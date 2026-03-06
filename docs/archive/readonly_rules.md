# Readonly Rules — Chunk 1

## Databases

Writable database:
- warehouse.duckdb

Readonly database:
- warehouse_readonly.duckdb

## Mandatory Rules

- Humans (DBeaver, BI tools) MUST connect only to warehouse_readonly.duckdb
- Pipelines MUST write only to warehouse.duckdb
- warehouse_readonly.duckdb is refreshed by file copy only
- No script or tool may open warehouse_readonly.duckdb in write mode

## DBeaver Rule (Mandatory)

Before running any refresh script:

1. Disconnect warehouse_readonly.duckdb in DBeaver
2. Run PowerShell scripts
3. Reconnect warehouse_readonly.duckdb after completion

These rules are not optional.
