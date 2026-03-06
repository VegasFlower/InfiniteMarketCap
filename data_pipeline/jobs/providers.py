from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import pandas as pd
import requests

COMPANIES_MARKET_CAP_BASE_URL = "https://companiesmarketcap.com"
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
USER_AGENT = "InfiniteMarketCap/0.1 (+https://github.com/VegasFlower/InfiniteMarketCap)"
TIMEOUT_SECONDS = 30
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")

TRACKED_ASSETS = {
    "gold": {
        "asset_id": "gold",
        "symbol": "GOLD",
        "name": "Gold",
        "asset_type": "commodity",
        "companiesmarketcap_slug": "gold",
        "history_provider": "companiesmarketcap_marketcap",
    },
    "bitcoin": {
        "asset_id": "bitcoin",
        "symbol": "BTC",
        "name": "Bitcoin",
        "asset_type": "crypto",
        "coingecko_id": "bitcoin",
        "history_provider": "coingecko",
    },
    "ethereum": {
        "asset_id": "ethereum",
        "symbol": "ETH",
        "name": "Ethereum",
        "asset_type": "crypto",
        "coingecko_id": "ethereum",
        "history_provider": "coingecko",
    },
    "nvidia": {
        "asset_id": "nvidia",
        "symbol": "NVDA",
        "name": "NVIDIA",
        "asset_type": "stock",
        "companiesmarketcap_slug": "nvidia",
        "history_provider": "companiesmarketcap_marketcap_and_price",
    },
}

SYMBOL_TO_ASSET_ID = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "GOLD": "gold",
    "NVDA": "nvidia",
}

ROW_PATTERN = re.compile(
    r'<tr(?: class="(?P<row_class>[^"]*)")?>\s*'
    r'<td class="rank-td[^>]*" data-sort="(?P<rank>\d+)">.*?</td>\s*'
    r'<td class="name-td">(?P<name_block>.*?)</td>\s*'
    r'<td class="td-right" data-sort="(?P<market_cap>[^"]+)">.*?</td>\s*'
    r'<td class="td-right" data-sort="(?P<price>[^"]+)">.*?</td>',
    re.S,
)
HREF_PATTERN = re.compile(r'href="/(?P<slug>[^/"]+)/marketcap/"')
NAME_PATTERN = re.compile(r'<div class="company-name">(?P<name>[^<]+)</div>')
SYMBOL_PATTERN = re.compile(r'<div class="company-code"><span class="rank d-none"></span>(?P<symbol>[^<]+)</div>')
JSON_DATA_PATTERN = re.compile(r'data = (\[.*?\]);', re.S)


@dataclass
class SourceSnapshot:
    asset_id: str
    symbol: str
    name: str
    asset_type: str
    exchange: str | None
    currency: str
    market_cap_usd: float
    price_usd: float | None
    rank_global: int | None
    source: str
    source_slug: str | None
    date: str


def _http_get(url: str, params: dict[str, Any] | None = None) -> requests.Response:
    response = requests.get(
        url,
        params=params,
        headers={"User-Agent": USER_AGENT},
        timeout=TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response


def _normalize_asset_type(row_class: str | None, symbol: str) -> str:
    row_class = row_class or ""
    lowered = row_class.lower()
    if "crypto" in lowered:
        return "crypto"
    if "precious" in lowered:
        return "commodity"
    if "etf" in lowered:
        return "etf"
    if symbol.endswith(".X"):
        return "crypto"
    return "stock"


def _parse_float(raw_value: str) -> float | None:
    cleaned = raw_value.replace(",", "").strip()
    if cleaned in {"", "-", "None"}:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def fetch_top_assets(limit: int = 100) -> pd.DataFrame:
    html = _http_get(f"{COMPANIES_MARKET_CAP_BASE_URL}/assets-by-market-cap/").text
    rows: list[dict[str, Any]] = []
    snapshot_date = datetime.now(tz=UTC).date().isoformat()

    for match in ROW_PATTERN.finditer(html):
        name_block = match.group("name_block")
        name_match = NAME_PATTERN.search(name_block)
        symbol_match = SYMBOL_PATTERN.search(name_block)
        if not name_match or not symbol_match:
            continue

        name = name_match.group("name").strip()
        symbol = symbol_match.group("symbol").strip().upper()
        href_match = HREF_PATTERN.search(name_block)
        slug = href_match.group("slug") if href_match else None
        asset_id = SYMBOL_TO_ASSET_ID.get(symbol, slug or symbol.lower())
        asset_type = _normalize_asset_type(match.group("row_class"), symbol)
        exchange = "CRYPTO" if asset_type == "crypto" else None
        rows.append(
            {
                "asset_id": asset_id,
                "symbol": symbol,
                "name": name,
                "asset_type": asset_type,
                "exchange": exchange,
                "currency": "USD",
                "market_cap_usd": _parse_float(match.group("market_cap")),
                "price_usd": _parse_float(match.group("price")),
                "rank_global": int(match.group("rank")),
                "source": "companiesmarketcap_top_assets",
                "source_slug": slug,
                "date": snapshot_date,
            }
        )
        if len(rows) >= limit:
            break

    if not rows:
        raise RuntimeError("Failed to parse top assets from CompaniesMarketCap.")

    return pd.DataFrame(rows)


def _parse_companiesmarketcap_series(slug: str, path: str, value_key: str) -> pd.DataFrame:
    html = _http_get(f"{COMPANIES_MARKET_CAP_BASE_URL}/{slug}/{path}/").text
    match = JSON_DATA_PATTERN.search(html)
    if not match:
        return pd.DataFrame(columns=["date", "value"])
    series = json.loads(match.group(1))
    if not series:
        return pd.DataFrame(columns=["date", "value"])
    data = pd.DataFrame(series)
    data["date"] = pd.to_datetime(data["d"], unit="s", utc=True).dt.date.astype(str)
    data = data.rename(columns={value_key: "value"})[["date", "value"]]
    return data


def fetch_companiesmarketcap_marketcap_history(slug: str) -> pd.DataFrame:
    data = _parse_companiesmarketcap_series(slug, "marketcap", "m")
    return data.rename(columns={"value": "market_cap_usd"})


def fetch_companiesmarketcap_price_history(slug: str) -> pd.DataFrame:
    data = _parse_companiesmarketcap_series(slug, "stock-price-history", "v")
    return data.rename(columns={"value": "price_usd"})


def fetch_coingecko_history(coin_id: str) -> pd.DataFrame:
    headers = {"User-Agent": USER_AGENT}
    if COINGECKO_API_KEY:
        headers["x-cg-demo-api-key"] = COINGECKO_API_KEY
    response = requests.get(
        f"{COINGECKO_BASE_URL}/coins/{coin_id}/market_chart",
        params={"vs_currency": "usd", "days": "max", "interval": "daily"},
        headers=headers,
        timeout=TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    payload = response.json()
    prices = pd.DataFrame(payload["prices"], columns=["timestamp_ms", "price_usd"])
    market_caps = pd.DataFrame(payload["market_caps"], columns=["timestamp_ms", "market_cap_usd"])
    history = prices.merge(market_caps, on="timestamp_ms", how="inner")
    history["date"] = pd.to_datetime(history["timestamp_ms"], unit="ms", utc=True).dt.date.astype(str)
    return history[["date", "price_usd", "market_cap_usd"]]


def fetch_tracked_asset_histories(current_snapshot: pd.DataFrame) -> pd.DataFrame:
    snapshot_lookup = current_snapshot.set_index("asset_id").to_dict("index")
    history_frames: list[pd.DataFrame] = []

    for asset_id, config in TRACKED_ASSETS.items():
        current_row = snapshot_lookup.get(asset_id, {})
        try:
            if config["history_provider"] == "coingecko":
                history = fetch_coingecko_history(config["coingecko_id"])
            elif config["history_provider"] == "companiesmarketcap_marketcap_and_price":
                market_caps = fetch_companiesmarketcap_marketcap_history(config["companiesmarketcap_slug"])
                prices = fetch_companiesmarketcap_price_history(config["companiesmarketcap_slug"])
                history = market_caps.merge(prices, on="date", how="left")
            else:
                history = fetch_companiesmarketcap_marketcap_history(config["companiesmarketcap_slug"])
                history["price_usd"] = None
        except Exception as error:
            print(f"[WARN] Failed to fetch history for {asset_id}: {error}")
            history = pd.DataFrame(columns=["date", "price_usd", "market_cap_usd"])

        if history.empty:
            if current_row:
                history = pd.DataFrame(
                    [
                        {
                            "date": current_snapshot["date"].iloc[0],
                            "price_usd": current_row.get("price_usd"),
                            "market_cap_usd": current_row.get("market_cap_usd"),
                        }
                    ]
                )
            else:
                print(f"[WARN] No current snapshot for tracked asset {asset_id}, skipping.")
                continue

        history["asset_id"] = config["asset_id"]
        history["symbol"] = config["symbol"]
        history["name"] = config["name"]
        history["asset_type"] = config["asset_type"]
        history["exchange"] = current_row.get("exchange")
        history["currency"] = "USD"
        history["rank_global"] = None
        history["source"] = f"historical_{config['history_provider']}"
        history["source_slug"] = config.get("companiesmarketcap_slug") or config.get("coingecko_id")
        history_frames.append(history)

    if not history_frames:
        return pd.DataFrame(
            columns=[
                "date",
                "asset_id",
                "symbol",
                "name",
                "asset_type",
                "exchange",
                "currency",
                "market_cap_usd",
                "price_usd",
                "rank_global",
                "source",
                "source_slug",
            ]
        )

    combined = pd.concat(history_frames, ignore_index=True)
    combined = combined[
        [
            "date",
            "asset_id",
            "symbol",
            "name",
            "asset_type",
            "exchange",
            "currency",
            "market_cap_usd",
            "price_usd",
            "rank_global",
            "source",
            "source_slug",
        ]
    ]
    combined = combined.sort_values(["asset_id", "date"]).drop_duplicates(["asset_id", "date"], keep="last")
    return combined
