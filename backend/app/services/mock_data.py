from datetime import date, timedelta


def get_overview(top_n: int) -> dict:
    return {
        "date": date.today().isoformat(),
        "top_n": top_n,
        "total_market_cap_usd": 53_200_000_000_000,
        "top5_share": 0.318,
        "top10_share": 0.472,
        "advancers_ratio": 0.56,
        "median_return_7d": 0.018,
        "mean_return_7d": 0.024,
    }


def get_watchlist(symbols: list[str]) -> list[dict]:
    base = {
        "GOLD": {
            "symbol": "GOLD",
            "name": "Gold",
            "market_cap_usd": 20_100_000_000_000,
            "rank_global": 1,
            "return_7d": 0.012,
            "return_30d": 0.038,
            "rank_change_30d": 0,
            "share_in_top100": 0.181,
            "trend_score": 61.0,
        },
        "BTC": {
            "symbol": "BTC",
            "name": "Bitcoin",
            "market_cap_usd": 1_720_000_000_000,
            "rank_global": 8,
            "return_7d": 0.076,
            "return_30d": 0.164,
            "rank_change_30d": -2,
            "share_in_top100": 0.031,
            "trend_score": 82.0,
        },
        "ETH": {
            "symbol": "ETH",
            "name": "Ethereum",
            "market_cap_usd": 410_000_000_000,
            "rank_global": 31,
            "return_7d": 0.043,
            "return_30d": 0.092,
            "rank_change_30d": -1,
            "share_in_top100": 0.008,
            "trend_score": 73.0,
        },
        "NVDA": {
            "symbol": "NVDA",
            "name": "NVIDIA",
            "market_cap_usd": 2_840_000_000_000,
            "rank_global": 4,
            "return_7d": 0.035,
            "return_30d": 0.115,
            "rank_change_30d": -1,
            "share_in_top100": 0.054,
            "trend_score": 79.0,
        },
    }
    return [base[s] for s in symbols if s in base]


def get_rank_movers() -> list[dict]:
    return [
        {"symbol": "BTC", "name": "Bitcoin", "rank_global": 8, "rank_change": -2, "return_period": 0.164},
        {"symbol": "NVDA", "name": "NVIDIA", "rank_global": 4, "rank_change": -1, "return_period": 0.115},
        {"symbol": "META", "name": "Meta", "rank_global": 12, "rank_change": -3, "return_period": 0.128},
    ]


def get_anomalies() -> list[dict]:
    return [
        {
            "event_id": "evt_btc_trend_accel",
            "symbol": "BTC",
            "event_type": "TREND_ACCEL",
            "severity": "P1",
            "direction": "UP",
            "summary": "Trend score above 80 with rising rank momentum.",
            "trigger_value": 82.0,
            "threshold_value": 75.0,
        },
        {
            "event_id": "evt_nvda_return_spike",
            "symbol": "NVDA",
            "event_type": "RETURN_SPIKE_UP",
            "severity": "P2",
            "direction": "UP",
            "summary": "30-day return crossed configured threshold.",
            "trigger_value": 0.115,
            "threshold_value": 0.10,
        },
    ]


def get_asset_summary(asset_id: str) -> dict:
    lookup = {item["symbol"].lower(): item for item in get_watchlist(["GOLD", "BTC", "ETH", "NVDA"])}
    asset = lookup.get(asset_id.lower())
    if not asset:
        asset = lookup["btc"]
    return {
        "asset_id": asset_id.lower(),
        "symbol": asset["symbol"],
        "name": asset["name"],
        "market_cap_usd": asset["market_cap_usd"],
        "rank_global": asset["rank_global"],
        "return_7d": asset["return_7d"],
        "return_30d": asset["return_30d"],
        "return_90d": asset["return_30d"] * 1.8,
        "trend_score": asset["trend_score"],
        "share_in_top100": asset["share_in_top100"],
    }


def get_asset_timeseries(asset_id: str) -> list[dict]:
    points = []
    today = date.today()
    rank = 8 if asset_id.lower() == "btc" else 4
    price = 100.0 if asset_id.lower() == "btc" else 80.0
    market_cap = 1_000_000_000_000 if asset_id.lower() == "btc" else 2_000_000_000_000
    for offset in range(10, -1, -1):
        points.append(
            {
                "date": (today - timedelta(days=offset * 9)).isoformat(),
                "price_usd": round(price * (1 + (10 - offset) * 0.03), 2),
                "market_cap_usd": round(market_cap * (1 + (10 - offset) * 0.025), 2),
                "rank_global": max(1, rank - (10 - offset) // 4),
            }
        )
    return points


def get_asset_events(asset_id: str) -> list[dict]:
    return [
        {
            "date": (date.today() - timedelta(days=30)).isoformat(),
            "event_type": "RANK_JUMP_UP",
            "severity": "P2",
            "description": f"{asset_id.upper()} improved its rank over the last 30 days.",
        },
        {
            "date": (date.today() - timedelta(days=7)).isoformat(),
            "event_type": "TREND_ACCEL",
            "severity": "P1",
            "description": f"{asset_id.upper()} entered a stronger trend acceleration regime.",
        },
    ]
