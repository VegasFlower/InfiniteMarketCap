from datetime import date

import pandas as pd

from common import DATA_DIR


RAW_FILE = DATA_DIR / "raw_assets.csv"


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(
        [
            ["gold", "GOLD", "Gold", "commodity", None, "USD", 20_100_000_000_000, 2920.0, 1],
            ["btc", "BTC", "Bitcoin", "crypto", None, "USD", 1_720_000_000_000, 87000.0, 8],
            ["eth", "ETH", "Ethereum", "crypto", None, "USD", 410_000_000_000, 3550.0, 31],
            ["nvda", "NVDA", "NVIDIA", "stock", "NASDAQ", "USD", 2_840_000_000_000, 116.0, 4],
        ],
        columns=[
            "asset_id",
            "symbol",
            "name",
            "asset_type",
            "exchange",
            "currency",
            "market_cap_usd",
            "price_usd",
            "rank_global",
        ],
    )
    df["snapshot_date"] = date.today().isoformat()
    df.to_csv(RAW_FILE, index=False)
    print(f"Wrote raw asset data to {RAW_FILE}")


if __name__ == "__main__":
    main()
