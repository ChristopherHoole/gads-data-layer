import os
from dataclasses import dataclass
from dotenv import load_dotenv

@dataclass(frozen=True)
class Settings:
    # Mode: mock | test_account | prod
    mode: str

    # Metadata Postgres
    meta_db_host: str
    meta_db_port: int
    meta_db_name: str
    meta_db_user: str
    meta_db_password: str

    # Warehouse (MOCK = DuckDB file)
    warehouse_duckdb_path: str

    # Mock
    mock_seed: int

def get_settings() -> Settings:
    load_dotenv()  # reads .env if present

    mode = os.getenv("GADS_MODE", "mock").strip().lower()

    return Settings(
        mode=mode,
        meta_db_host=os.getenv("META_DB_HOST", "localhost"),
        meta_db_port=int(os.getenv("META_DB_PORT", "5432")),
        meta_db_name=os.getenv("META_DB_NAME", "gads_meta"),
        meta_db_user=os.getenv("META_DB_USER", "gads"),
        meta_db_password=os.getenv("META_DB_PASSWORD", "gads_password"),
        warehouse_duckdb_path=os.getenv("WAREHOUSE_DUCKDB_PATH", "./warehouse.duckdb"),
        mock_seed=int(os.getenv("MOCK_SEED", "42")),
    )
