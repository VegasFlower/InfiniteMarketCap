from __future__ import annotations

import io
import json
import re
import time
from datetime import UTC, date, datetime, timedelta
from typing import Any

import pandas as pd
import requests

COMPANIES_MARKET_CAP_BASE_URL = "https://companiesmarketcap.com"
USER_AGENT = "InfiniteMarketCap/0.1 (+https://github.com/VegasFlower/InfiniteMarketCap)"
TIMEOUT_SECONDS = 30

STOOQ_SYMBOL_BY_ASSET_ID = {
    "bitcoin": "btc.v",
    "ethereum": "eth.v",
    "gold": "xauusd",
    "nvidia": "nvda.us",
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
    r'<td class="td-right" data-sort="(?P<price>[^"]+)">.*?</td>\s*'
    r'<td class="rh-sm" data-sort="(?P<change_24h>[^"]+)">',
    re.S,
)
HREF_PATTERN = re.compile(r'href="/(?P<slug>[^/"]+)/marketcap/"')
NAME_PATTERN = re.compile(r'<div class="company-name">(?P<name>[^<]+)</div>')
SYMBOL_PATTERN = re.compile(r'<div class="company-code"><span class="rank d-none"></span>(?P<symbol>[^<]+)</div>')
JSON_DATA_PATTERN = re.compile(r'data = (\[.*?\]);', re.S)


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


def _parse_change_24h(raw_value: str) -> float | None:
    parsed = _parse_float(raw_value)
    if parsed is None:
        return None
    return parsed / 10_000.0


def _parse_price(raw_value: str) -> float | None:
    parsed = _parse_float(raw_value)
    if parsed is None:
        return None
    return parsed / 100.0


def fetch_top_assets(limit: int = 100) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    snapshot_date = datetime.now(tz=UTC).date().isoformat()
    page = 1

    while len(rows) < limit:
        response = _http_get(
            f"{COMPANIES_MARKET_CAP_BASE_URL}/assets-by-market-cap/",
            params={"page": page},
        )
        html = response.text
        matched_rows = 0

        for match in ROW_PATTERN.finditer(html):
            matched_rows += 1
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
                    "price_usd": _parse_price(match.group("price")),
                    "change_24h_pct": _parse_change_24h(match.group("change_24h")),
                    "rank_global": int(match.group("rank")),
                    "source": "companiesmarketcap_top_assets",
                    "source_slug": slug,
                    "date": snapshot_date,
                }
            )
            if len(rows) >= limit:
                break

        if matched_rows == 0:
            break
        page += 1

    if not rows:
        raise RuntimeError("Failed to parse top assets from CompaniesMarketCap.")
    return pd.DataFrame(rows).sort_values("rank_global").head(limit)


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
    if data.empty:
        return data.rename(columns={"value": "market_cap_usd"})
    # The chart payload stores values in 100,000 USD units.
    data["value"] = pd.to_numeric(data["value"], errors="coerce") * 100_000.0
    return data.rename(columns={"value": "market_cap_usd"})


def fetch_companiesmarketcap_price_history(slug: str) -> pd.DataFrame:
    data = _parse_companiesmarketcap_series(slug, "stock-price-history", "v")
    if data.empty:
        return data.rename(columns={"value": "price_usd"})
    data["value"] = pd.to_numeric(data["value"], errors="coerce")
    return data.rename(columns={"value": "price_usd"})


def fetch_stooq_price_history(stooq_symbol: str) -> pd.DataFrame:
    response = _http_get("https://stooq.com/q/d/l/", params={"s": stooq_symbol, "i": "d"})
    text = response.text.strip()
    if not text or text.startswith("No data"):
        return pd.DataFrame(columns=["date", "price_usd"])

    data = pd.read_csv(io.StringIO(text))
    if "Date" not in data.columns or "Close" not in data.columns:
        return pd.DataFrame(columns=["date", "price_usd"])

    data = data[["Date", "Close"]].rename(columns={"Date": "date", "Close": "price_usd"})
    data["date"] = pd.to_datetime(data["date"], errors="coerce").dt.date.astype(str)
    data["price_usd"] = pd.to_numeric(data["price_usd"], errors="coerce")
    data = data.dropna(subset=["date", "price_usd"]).sort_values("date")
    return data


def _build_fallback_history(asset_row: pd.Series) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "date": asset_row["date"],
                "market_cap_usd": asset_row["market_cap_usd"],
                "price_usd": asset_row["price_usd"],
            }
        ]
    )


def fetch_top_assets_histories(current_snapshot: pd.DataFrame, lookback_years: int = 6) -> pd.DataFrame:
    history_frames: list[pd.DataFrame] = []
    min_date = (date.today() - timedelta(days=lookback_years * 365)).isoformat()

    for _, asset_row in current_snapshot.sort_values("rank_global").iterrows():
        asset_history = pd.DataFrame(columns=["date", "market_cap_usd", "price_usd"])
        source = "historical_fallback"
        source_slug: str | None = None

        slug = asset_row.get("source_slug")
        if isinstance(slug, str) and slug:
            try:
                market_caps = fetch_companiesmarketcap_marketcap_history(slug)
                if not market_caps.empty:
                    prices = fetch_companiesmarketcap_price_history(slug)
                    if prices.empty:
                        market_caps["price_usd"] = None
                        asset_history = market_caps
                    else:
                        asset_history = market_caps.merge(prices, on="date", how="left")
                    source = "historical_companiesmarketcap"
                    source_slug = slug
            except Exception as error:
                print(f"[WARN] History fetch failed for {asset_row['symbol']} via CompaniesMarketCap: {error}")

        if asset_history.empty:
            stooq_symbol = STOOQ_SYMBOL_BY_ASSET_ID.get(str(asset_row["asset_id"]))
            if stooq_symbol:
                try:
                    prices = fetch_stooq_price_history(stooq_symbol)
                    if not prices.empty:
                        current_price = asset_row.get("price_usd")
                        current_market_cap = asset_row.get("market_cap_usd")
                        prices = prices.copy()
                        if pd.notna(current_price) and pd.notna(current_market_cap) and float(current_price) > 0:
                            prices["market_cap_usd"] = float(current_market_cap) * prices["price_usd"] / float(current_price)
                        else:
                            prices["market_cap_usd"] = float(current_market_cap)
                        asset_history = prices[["date", "market_cap_usd", "price_usd"]]
                        source = "historical_stooq_scaled"
                        source_slug = stooq_symbol
                except Exception as error:
                    print(f"[WARN] History fetch failed for {asset_row['symbol']} via Stooq: {error}")

        if asset_history.empty:
            asset_history = _build_fallback_history(asset_row)
            source = "historical_current_only"
            source_slug = None

        asset_history = asset_history[asset_history["date"] >= min_date].copy()
        if asset_history.empty:
            asset_history = _build_fallback_history(asset_row)
            source = "historical_current_only"
            source_slug = None

        asset_history["asset_id"] = asset_row["asset_id"]
        asset_history["symbol"] = asset_row["symbol"]
        asset_history["name"] = asset_row["name"]
        asset_history["asset_type"] = asset_row["asset_type"]
        asset_history["exchange"] = asset_row["exchange"]
        asset_history["currency"] = "USD"
        asset_history["rank_global"] = None
        asset_history["change_24h_pct"] = None
        asset_history["source"] = source
        asset_history["source_slug"] = source_slug

        history_frames.append(asset_history)
        time.sleep(0.05)

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
                "change_24h_pct",
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
            "change_24h_pct",
            "rank_global",
            "source",
            "source_slug",
        ]
    ]
    combined = combined.sort_values(["asset_id", "date"]).drop_duplicates(["asset_id", "date"], keep="last")
    return combined
