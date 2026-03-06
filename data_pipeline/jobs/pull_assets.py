import os

import pandas as pd

from common import DATA_DIR
from providers import fetch_top_assets, fetch_top_assets_histories


CURRENT_SNAPSHOT_FILE = DATA_DIR / "top_assets_current.csv"
HISTORY_FILE = DATA_DIR / "tracked_asset_history.csv"
TOP_ASSET_LIMIT = int(os.getenv("TOP_ASSET_LIMIT", "300"))

HISTORY_COLUMNS = [
    "date",
    "asset_id",
    "symbol",
    "name",
    "asset_type",
    "exchange",
    "currency",
    "market_cap_usd",
    "price_usd",
    "change_24h_pct",
    "rank_global",
    "source",
    "source_slug",
]


def _ensure_history_columns(df: pd.DataFrame) -> pd.DataFrame:
    aligned = df.copy()
    for column in HISTORY_COLUMNS:
        if column not in aligned.columns:
            aligned[column] = None
    return aligned[HISTORY_COLUMNS]


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    top_assets = fetch_top_assets(limit=TOP_ASSET_LIMIT)
    top_assets.to_csv(CURRENT_SNAPSHOT_FILE, index=False)
    print(f"Wrote current top-asset snapshot to {CURRENT_SNAPSHOT_FILE}")

    if HISTORY_FILE.exists():
        existing_history = pd.read_csv(HISTORY_FILE, low_memory=False)
        existing_history = _ensure_history_columns(existing_history)
    else:
        existing_history = pd.DataFrame(columns=HISTORY_COLUMNS)

    top_assets = _ensure_history_columns(top_assets)
    current_asset_ids = set(top_assets["asset_id"].astype(str).tolist())
    existing_history = existing_history[existing_history["asset_id"].astype(str).isin(current_asset_ids)]

    existing_asset_ids = set(existing_history["asset_id"].dropna().astype(str).tolist())
    new_asset_ids = sorted(current_asset_ids - existing_asset_ids)

    if new_asset_ids:
        to_backfill = top_assets[top_assets["asset_id"].astype(str).isin(new_asset_ids)]
        print(f"Backfilling historical data for {len(new_asset_ids)} newly included assets...")
        new_history = fetch_top_assets_histories(to_backfill)
        new_history = _ensure_history_columns(new_history)
    else:
        print("No new assets to backfill. Reusing existing history.")
        new_history = pd.DataFrame(columns=HISTORY_COLUMNS)

    frames = [frame for frame in [existing_history, new_history, top_assets] if not frame.empty]
    if frames:
        combined_history = pd.concat(frames, ignore_index=True)
    else:
        combined_history = pd.DataFrame(columns=HISTORY_COLUMNS)
    combined_history = (
        combined_history.sort_values(["asset_id", "date", "source"]).drop_duplicates(["asset_id", "date"], keep="last")
    )
    combined_history.to_csv(HISTORY_FILE, index=False)
    print(f"Wrote top-asset history to {HISTORY_FILE}")


if __name__ == "__main__":
    main()
