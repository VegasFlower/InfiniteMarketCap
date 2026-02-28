from common import DATA_DIR
from providers import fetch_top_assets, fetch_tracked_asset_histories


CURRENT_SNAPSHOT_FILE = DATA_DIR / "top_assets_current.csv"
TRACKED_HISTORY_FILE = DATA_DIR / "tracked_asset_history.csv"


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    top_assets = fetch_top_assets(limit=100)
    top_assets.to_csv(CURRENT_SNAPSHOT_FILE, index=False)
    print(f"Wrote current top-asset snapshot to {CURRENT_SNAPSHOT_FILE}")

    tracked_history = fetch_tracked_asset_histories(top_assets)
    tracked_history.to_csv(TRACKED_HISTORY_FILE, index=False)
    print(f"Wrote tracked asset history to {TRACKED_HISTORY_FILE}")


if __name__ == "__main__":
    main()
