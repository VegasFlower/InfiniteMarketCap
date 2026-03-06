from datetime import UTC, datetime

import pandas as pd

from common import DATA_DIR, ensure_db


CURRENT_SNAPSHOT_FILE = DATA_DIR / "top_assets_current.csv"
HISTORY_FILE = DATA_DIR / "tracked_asset_history.csv"


def _load_frames() -> tuple[pd.DataFrame, pd.DataFrame]:
    current_df = pd.read_csv(CURRENT_SNAPSHOT_FILE)
    if HISTORY_FILE.exists():
        history_df = pd.read_csv(HISTORY_FILE, low_memory=False)
    else:
        history_df = pd.DataFrame(columns=current_df.columns)

    combined = pd.concat([current_df, history_df], ignore_index=True)
    combined = combined.sort_values(["asset_id", "date", "source"]).drop_duplicates(["asset_id", "date"], keep="first")
    return current_df, combined


def main() -> None:
    current_df, combined = _load_frames()
    conn = ensure_db()

    dim_asset = current_df[["asset_id", "symbol", "name", "asset_type", "exchange", "currency"]].copy()
    dim_asset["is_active"] = True
    dim_asset["created_at"] = datetime.now(tz=UTC)
    dim_asset["updated_at"] = datetime.now(tz=UTC)

    snapshot = combined[
        ["date", "asset_id", "price_usd", "market_cap_usd", "change_24h_pct", "rank_global", "source"]
    ].copy()
    snapshot["price_usd"] = pd.to_numeric(snapshot["price_usd"], errors="coerce")
    snapshot["market_cap_usd"] = pd.to_numeric(snapshot["market_cap_usd"], errors="coerce")
    snapshot["change_24h_pct"] = pd.to_numeric(snapshot["change_24h_pct"], errors="coerce")
    snapshot["rank_global"] = pd.to_numeric(snapshot["rank_global"], errors="coerce")

    historical_missing_rank = snapshot["rank_global"].isna() & snapshot["market_cap_usd"].notna()
    if historical_missing_rank.any():
        inferred_rank = (
            snapshot.loc[historical_missing_rank, ["date", "market_cap_usd"]]
            .groupby("date")["market_cap_usd"]
            .rank(method="min", ascending=False)
        )
        snapshot.loc[historical_missing_rank, "rank_global"] = inferred_rank

    snapshot["volume_usd"] = None
    snapshot["rank_in_type"] = None
    snapshot["ingested_at"] = datetime.now(tz=UTC)
    snapshot = snapshot[
        [
            "date",
            "asset_id",
            "price_usd",
            "market_cap_usd",
            "change_24h_pct",
            "volume_usd",
            "rank_global",
            "rank_in_type",
            "source",
            "ingested_at",
        ]
    ]

    conn.register("dim_asset_df", dim_asset)
    conn.register("snapshot_df", snapshot)
    conn.execute("DELETE FROM dim_asset WHERE asset_id IN (SELECT asset_id FROM dim_asset_df)")
    conn.execute(
        """
        INSERT INTO dim_asset (asset_id, symbol, name, asset_type, exchange, currency, is_active, created_at, updated_at)
        SELECT asset_id, symbol, name, asset_type, exchange, currency, is_active, created_at, updated_at
        FROM dim_asset_df
        """
    )
    conn.execute(
        """
        DELETE FROM fact_asset_snapshot_daily
        WHERE rank_global IS NOT NULL
          AND date IN (
            SELECT DISTINCT CAST(date AS DATE)
            FROM snapshot_df
            WHERE rank_global IS NOT NULL
          )
        """
    )
    conn.execute(
        """
        DELETE FROM fact_asset_snapshot_daily
        WHERE EXISTS (
          SELECT 1
          FROM snapshot_df
          WHERE snapshot_df.date = fact_asset_snapshot_daily.date
            AND snapshot_df.asset_id = fact_asset_snapshot_daily.asset_id
        )
        """
    )
    conn.execute(
        """
        INSERT INTO fact_asset_snapshot_daily
        (date, asset_id, price_usd, market_cap_usd, change_24h_pct, volume_usd, rank_global, rank_in_type, source, ingested_at)
        SELECT
          date,
          asset_id,
          price_usd,
          market_cap_usd,
          change_24h_pct,
          volume_usd,
          rank_global,
          rank_in_type,
          source,
          ingested_at
        FROM snapshot_df
        """
    )
    print(f"Loaded {len(dim_asset)} assets and {len(snapshot)} snapshot rows into DuckDB")


if __name__ == "__main__":
    main()
