from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data_pipeline" / "local_data"
DB_PATH = DATA_DIR / "infinite_market_cap.duckdb"
SCHEMA_PATH = ROOT / "data_pipeline" / "sql" / "schema.sql"


def ensure_db() -> duckdb.DuckDBPyConnection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(str(DB_PATH))
    conn.execute(SCHEMA_PATH.read_text())
    conn.execute("ALTER TABLE fact_asset_snapshot_daily ADD COLUMN IF NOT EXISTS change_24h_pct DOUBLE")
    conn.execute("ALTER TABLE fact_asset_factor_daily ADD COLUMN IF NOT EXISTS return_1d DOUBLE")
    conn.execute("ALTER TABLE fact_asset_factor_daily ADD COLUMN IF NOT EXISTS return_180d DOUBLE")
    conn.execute("ALTER TABLE fact_asset_factor_daily ADD COLUMN IF NOT EXISTS return_365d DOUBLE")
    conn.execute("ALTER TABLE fact_asset_factor_daily ADD COLUMN IF NOT EXISTS return_3y DOUBLE")
    conn.execute("ALTER TABLE fact_asset_factor_daily ADD COLUMN IF NOT EXISTS return_5y DOUBLE")
    conn.execute("ALTER TABLE fact_asset_factor_daily ADD COLUMN IF NOT EXISTS rank_change_180d INTEGER")
    conn.execute("ALTER TABLE fact_asset_factor_daily ADD COLUMN IF NOT EXISTS rank_change_365d INTEGER")
    return conn
