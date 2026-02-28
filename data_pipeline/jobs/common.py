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
    return conn
