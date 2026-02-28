from datetime import datetime

import pandas as pd

from common import DATA_DIR, ensure_db


RAW_FILE = DATA_DIR / "raw_assets.csv"


def main() -> None:
    df = pd.read_csv(RAW_FILE)
    conn = ensure_db()

    dim_asset = df[["asset_id", "symbol", "name", "asset_type", "exchange", "currency"]].copy()
    dim_asset["is_active"] = True
    dim_asset["created_at"] = datetime.utcnow()
    dim_asset["updated_at"] = datetime.utcnow()

    snapshot = df[["snapshot_date", "asset_id", "price_usd", "market_cap_usd", "rank_global"]].copy()
    snapshot = snapshot.rename(columns={"snapshot_date": "date"})
    snapshot["volume_usd"] = None
    snapshot["rank_in_type"] = snapshot["rank_global"]
    snapshot["source"] = "mock_seed"
    snapshot["ingested_at"] = datetime.utcnow()

    conn.register("dim_asset_df", dim_asset)
    conn.register("snapshot_df", snapshot)
    conn.execute("DELETE FROM dim_asset WHERE asset_id IN (SELECT asset_id FROM dim_asset_df)")
    conn.execute("INSERT INTO dim_asset SELECT * FROM dim_asset_df")
    conn.execute("DELETE FROM fact_asset_snapshot_daily WHERE date IN (SELECT DISTINCT date FROM snapshot_df)")
    conn.execute("INSERT INTO fact_asset_snapshot_daily SELECT * FROM snapshot_df")
    print("Normalized assets loaded into DuckDB")


if __name__ == "__main__":
    main()
