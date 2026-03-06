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


def _watchlist_base() -> dict[str, dict]:
    return {
        "GOLD": {
            "asset_id": "gold",
            "symbol": "GOLD",
            "name": "Gold",
            "market_cap_usd": 35_685_000_000_000,
            "price_usd": 5132.0,
            "change_24h_pct": 0.0197,
            "rank_global": 1,
            "return_7d": 0.012,
            "return_30d": 0.038,
            "return_90d": 0.081,
            "return_180d": 0.146,
            "return_1y": 0.234,
            "return_3y": 0.462,
            "return_5y": 0.781,
            "rank_change_90d": 0,
            "rank_change_180d": 0,
            "rank_change_1y": 0,
            "share_in_top30": 0.259,
            "share_in_top50": 0.234,
            "share_in_top100": 0.198,
            "share_in_top500": 0.141,
            "trend_score": 61.0,
        },
        "BTC": {
            "asset_id": "bitcoin",
            "symbol": "BTC",
            "name": "Bitcoin",
            "market_cap_usd": 1_313_000_000_000,
            "price_usd": 65676.0,
            "change_24h_pct": -0.0307,
            "rank_global": 13,
            "return_7d": 0.076,
            "return_30d": 0.164,
            "return_90d": 0.243,
            "return_180d": 0.311,
            "return_1y": 0.398,
            "return_3y": 0.864,
            "return_5y": 1.722,
            "rank_change_90d": -2,
            "rank_change_180d": -3,
            "rank_change_1y": -5,
            "share_in_top30": 0.031,
            "share_in_top50": 0.029,
            "share_in_top100": 0.025,
            "share_in_top500": 0.018,
            "trend_score": 82.0,
        },
        "ETH": {
            "asset_id": "ethereum",
            "symbol": "ETH",
            "name": "Ethereum",
            "market_cap_usd": 232_540_000_000,
            "price_usd": 1926.0,
            "change_24h_pct": -0.0566,
            "rank_global": 81,
            "return_7d": 0.043,
            "return_30d": 0.092,
            "return_90d": 0.141,
            "return_180d": 0.193,
            "return_1y": 0.244,
            "return_3y": 0.522,
            "return_5y": 1.138,
            "rank_change_90d": -1,
            "rank_change_180d": -1,
            "rank_change_1y": -2,
            "share_in_top30": 0.0,
            "share_in_top50": 0.0,
            "share_in_top100": 0.004,
            "share_in_top500": 0.003,
            "trend_score": 73.0,
        },
        "NVDA": {
            "asset_id": "nvidia",
            "symbol": "NVDA",
            "name": "NVIDIA",
            "market_cap_usd": 4_314_000_000_000,
            "price_usd": 177.19,
            "change_24h_pct": -0.0416,
            "rank_global": 3,
            "return_7d": 0.035,
            "return_30d": 0.115,
            "return_90d": 0.242,
            "return_180d": 0.418,
            "return_1y": 0.633,
            "return_3y": 2.318,
            "return_5y": 5.874,
            "rank_change_90d": -1,
            "rank_change_180d": -2,
            "rank_change_1y": -3,
            "share_in_top30": 0.076,
            "share_in_top50": 0.071,
            "share_in_top100": 0.061,
            "share_in_top500": 0.044,
            "trend_score": 79.0,
        },
    }


def get_watchlist(symbols: list[str]) -> list[dict]:
    base = _watchlist_base()
    return [base[s] for s in symbols if s in base]


def get_top_assets(limit: int = 300) -> list[dict]:
    base = list(_watchlist_base().values())
    rows = []
    for item in base:
        rows.append(
            {
                "asset_id": item["asset_id"],
                "name": item["name"],
                "symbol": item["symbol"],
                "rank_global": item["rank_global"],
                "market_cap_usd": item["market_cap_usd"],
                "price_usd": item["price_usd"],
                "change_24h_pct": item["change_24h_pct"],
                "return_7d": item["return_7d"],
                "return_30d": item["return_30d"],
                "return_60d": (item["return_30d"] + item["return_90d"]) / 2,
                "return_90d": item["return_90d"],
                "return_180d": item["return_180d"],
                "return_1y": item["return_1y"],
                "return_3y": item["return_3y"],
                "return_5y": item["return_5y"],
                "rank_change_90d": item["rank_change_90d"],
                "rank_change_180d": item["rank_change_180d"],
                "rank_change_1y": item["rank_change_1y"],
            }
        )
    rows.sort(key=lambda row: row["rank_global"])
    return rows[:limit]


def get_rank_movers() -> list[dict]:
    return [
        {"symbol": "BTC", "name": "Bitcoin", "rank_global": 13, "rank_change": -2, "return_period": 0.243},
        {"symbol": "NVDA", "name": "NVIDIA", "rank_global": 3, "rank_change": -1, "return_period": 0.242},
        {"symbol": "META", "name": "Meta", "rank_global": 10, "rank_change": -3, "return_period": 0.128},
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
    lookup = {item["asset_id"]: item for item in _watchlist_base().values()}
    lookup.update({item["symbol"].lower(): item for item in _watchlist_base().values()})
    asset = lookup.get(asset_id.lower(), lookup["bitcoin"])
    return asset


def get_asset_timeseries(asset_id: str) -> list[dict]:
    points = []
    today = date.today()
    rank = 13 if asset_id.lower() in {"btc", "bitcoin"} else 3
    price = 100.0 if asset_id.lower() in {"btc", "bitcoin"} else 80.0
    market_cap = 1_000_000_000_000 if asset_id.lower() in {"btc", "bitcoin"} else 2_000_000_000_000
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
