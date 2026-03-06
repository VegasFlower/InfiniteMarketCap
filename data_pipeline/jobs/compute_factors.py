from __future__ import annotations

from datetime import UTC, datetime

import pandas as pd

from common import ensure_db


LOOKBACK_WINDOWS = [7, 30, 60, 90]


def _safe_return(current_value: float | None, previous_value: float | None) -> float | None:
    if current_value in (None, 0) or previous_value in (None, 0):
        return None
    return (current_value / previous_value) - 1


def _latest_valid(group: pd.DataFrame, column: str, on_or_before_date: pd.Timestamp) -> float | int | None:
    subset = group[(group["date_dt"] <= on_or_before_date) & group[column].notna()]
    if subset.empty:
        return None
    return subset.iloc[-1][column]


def main() -> None:
    conn = ensure_db()
    snapshots = conn.execute(
        "SELECT date, asset_id, price_usd, market_cap_usd, rank_global FROM fact_asset_snapshot_daily ORDER BY asset_id, date"
    ).fetchdf()

    if snapshots.empty:
        raise RuntimeError("No snapshot data found. Run pull_assets.py and normalize_assets.py first.")

    snapshots["date_dt"] = pd.to_datetime(snapshots["date"])
    as_of_date = snapshots[snapshots["rank_global"].notna()]["date_dt"].max()
    if pd.isna(as_of_date):
        as_of_date = snapshots["date_dt"].max()

    current_ranked = snapshots[(snapshots["date_dt"] == as_of_date) & snapshots["rank_global"].notna()].copy()
    current_ranked = current_ranked.sort_values("rank_global")
    assets = conn.execute("SELECT asset_id, symbol, name FROM dim_asset").fetchdf()

    records: list[dict] = []
    for asset_id, group in snapshots.groupby("asset_id"):
        group = group.sort_values("date_dt")
        current_row = group[group["date_dt"] <= as_of_date].iloc[-1]
        current_price = current_row["price_usd"] if pd.notna(current_row["price_usd"]) else None
        current_mcap = current_row["market_cap_usd"] if pd.notna(current_row["market_cap_usd"]) else None
        current_rank = current_row["rank_global"] if pd.notna(current_row["rank_global"]) else None

        factor_row: dict[str, object] = {
            "date": as_of_date.date().isoformat(),
            "asset_id": asset_id,
            "created_at": datetime.now(tz=UTC),
        }

        for window in LOOKBACK_WINDOWS:
            lookback_date = as_of_date - pd.Timedelta(days=window)
            prev_price = _latest_valid(group, "price_usd", lookback_date)
            prev_mcap = _latest_valid(group, "market_cap_usd", lookback_date)
            prev_rank = _latest_valid(group, "rank_global", lookback_date)

            price_return = _safe_return(current_price, prev_price)
            if price_return is None:
                price_return = _safe_return(current_mcap, prev_mcap)
            factor_row[f"return_{window}d"] = price_return
            if window in {30}:
                factor_row["mcap_change_30d"] = _safe_return(current_mcap, prev_mcap)
            if window in {7, 30, 90}:
                factor_row[f"rank_change_{window}d"] = int(current_rank - prev_rank) if current_rank is not None and prev_rank is not None else None

        factor_row.setdefault("mcap_change_30d", None)
        factor_row.setdefault("rank_change_7d", None)
        factor_row.setdefault("rank_change_30d", None)
        factor_row.setdefault("rank_change_90d", None)
        records.append(factor_row)

    factors = pd.DataFrame(records)

    totals_by_topn: dict[int, float] = {}
    for top_n in (30, 50, 100, 500):
        subset = current_ranked[current_ranked["rank_global"] <= top_n]
        totals_by_topn[top_n] = float(subset["market_cap_usd"].sum()) if not subset.empty else 0.0

    current_lookup = current_ranked[["asset_id", "market_cap_usd", "rank_global"]].copy()
    factors = factors.merge(current_lookup, on="asset_id", how="left")
    for top_n in (30, 50, 100, 500):
        denominator = totals_by_topn[top_n]
        factors[f"share_in_top{top_n}"] = factors["market_cap_usd"] / denominator if denominator else None

    top100_returns = factors[factors["rank_global"] <= 100]
    benchmark_30d = top100_returns["return_30d"].median(skipna=True)
    if pd.isna(benchmark_30d):
        benchmark_30d = 0.0
    factors["rel_strength_vs_top100_30d"] = factors["return_30d"].fillna(0) - benchmark_30d

    returns_score = pd.to_numeric(factors["return_30d"], errors="coerce").fillna(0).clip(-0.5, 1.0)
    rank_score = (-pd.to_numeric(factors["rank_change_30d"], errors="coerce").fillna(0)).clip(-20, 20) / 20
    strength_score = pd.to_numeric(factors["rel_strength_vs_top100_30d"], errors="coerce").fillna(0).clip(-0.5, 0.5)
    volatility_proxy = factors[["return_7d", "return_30d", "return_60d", "return_90d"]].std(axis=1).fillna(0).clip(0, 0.5)
    factors["trend_score"] = (
        ((returns_score + 0.5) / 1.5) * 35
        + ((rank_score + 1) / 2) * 30
        + ((strength_score + 0.5) / 1.0) * 20
        + ((0.5 - volatility_proxy) / 0.5) * 15
    ).round(2)

    factors = factors[
        [
            "date",
            "asset_id",
            "return_7d",
            "return_30d",
            "return_60d",
            "return_90d",
            "mcap_change_30d",
            "rank_change_7d",
            "rank_change_30d",
            "rank_change_90d",
            "share_in_top30",
            "share_in_top50",
            "share_in_top100",
            "share_in_top500",
            "rel_strength_vs_top100_30d",
            "trend_score",
            "created_at",
        ]
    ]

    agg_rows = []
    for top_n in (30, 50, 100, 500):
        subset = current_ranked[current_ranked["rank_global"] <= top_n].copy()
        if subset.empty:
            continue
        subset = subset.merge(factors[["asset_id", "return_7d"]], on="asset_id", how="left")
        total_market_cap = float(subset["market_cap_usd"].sum())
        agg_rows.append(
            {
                "date": as_of_date.date().isoformat(),
                "top_n": top_n,
                "total_market_cap_usd": total_market_cap,
                "top5_share": float(subset.nsmallest(min(5, len(subset)), "rank_global")["market_cap_usd"].sum() / total_market_cap),
                "top10_share": float(subset.nsmallest(min(10, len(subset)), "rank_global")["market_cap_usd"].sum() / total_market_cap),
                "advancers_ratio": float((subset["return_7d"] > 0).mean()) if subset["return_7d"].notna().any() else 0.0,
                "median_return_7d": float(subset["return_7d"].median(skipna=True)) if subset["return_7d"].notna().any() else 0.0,
                "mean_return_7d": float(subset["return_7d"].mean(skipna=True)) if subset["return_7d"].notna().any() else 0.0,
                "created_at": datetime.now(tz=UTC),
            }
        )
    agg = pd.DataFrame(agg_rows)

    conn.register("factors_df", factors)
    conn.execute("DELETE FROM fact_asset_factor_daily WHERE date = ?", [as_of_date.date().isoformat()])
    conn.execute("INSERT INTO fact_asset_factor_daily SELECT * FROM factors_df")
    if not agg.empty:
        conn.register("agg_df", agg)
        conn.execute("DELETE FROM agg_topn_daily WHERE date = ?", [as_of_date.date().isoformat()])
        conn.execute("INSERT INTO agg_topn_daily SELECT * FROM agg_df")
    print(f"Computed factor rows for {len(factors)} assets as of {as_of_date.date().isoformat()}")


if __name__ == "__main__":
    main()
