import os

from common import DATA_DIR
from providers import fetch_top_assets, fetch_top_assets_histories


CURRENT_SNAPSHOT_FILE = DATA_DIR / "top_assets_current.csv"
HISTORY_FILE = DATA_DIR / "tracked_asset_history.csv"
TOP_ASSET_LIMIT = int(os.getenv("TOP_ASSET_LIMIT", "300"))


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    top_assets = fetch_top_assets(limit=TOP_ASSET_LIMIT)
    top_assets.to_csv(CURRENT_SNAPSHOT_FILE, index=False)
    print(f"Wrote current top-asset snapshot to {CURRENT_SNAPSHOT_FILE}")

    asset_history = fetch_top_assets_histories(top_assets)
    asset_history.to_csv(HISTORY_FILE, index=False)
    print(f"Wrote top-asset history to {HISTORY_FILE}")


if __name__ == "__main__":
    main()
