from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import duckdb
except ImportError:  # pragma: no cover
    duckdb = None

DB_PATH = Path(__file__).resolve().parents[3] / "data_pipeline" / "local_data" / "infinite_market_cap.duckdb"


def has_real_data() -> bool:
    return duckdb is not None and DB_PATH.exists()


def _connect() -> "duckdb.DuckDBPyConnection":
    if duckdb is None:
        raise RuntimeError("duckdb is not installed")
    return duckdb.connect(str(DB_PATH), read_only=True)


def _latest_date() -> str:
    with _connect() as conn:
        row = conn.execute("SELECT MAX(date) FROM fact_asset_factor_daily").fetchone()
    if not row or row[0] is None:
        raise RuntimeError("No factor data available")
    return str(row[0])


def get_overview(top_n: int) -> dict[str, Any]:
    with _connect() as conn:
        row = conn.execute(
            "SELECT date, top_n, total_market_cap_usd, top5_share, top10_share, advancers_ratio, median_return_7d, mean_return_7d FROM agg_topn_daily WHERE top_n = ? ORDER BY date DESC LIMIT 1",
            [top_n],
        ).fetchone()
    if row is None:
        raise RuntimeError("No aggregate data available")
    return {
        "date": str(row[0]),
        "top_n": row[1],
        "total_market_cap_usd": float(row[2]),
        "top5_share": float(row[3] or 0),
        "top10_share": float(row[4] or 0),
        "advancers_ratio": float(row[5] or 0),
        "median_return_7d": float(row[6] or 0),
        "mean_return_7d": float(row[7] or 0),
    }


def get_watchlist(symbols: list[str]) -> list[dict[str, Any]]:
    if not symbols:
        return []

    placeholders = ",".join("?" for _ in symbols)
    query = f"""
        WITH latest AS (
          SELECT MAX(date) AS latest_date FROM fact_asset_factor_daily
        )
        SELECT
          a.asset_id,
          a.symbol,
          a.name,
          s.market_cap_usd,
          s.price_usd,
          s.change_24h_pct,
          s.rank_global,
          f.return_7d,
          f.return_30d,
          f.return_90d,
          f.return_180d,
          f.return_365d,
          f.return_3y,
          f.return_5y,
          f.rank_change_90d,
          f.rank_change_180d,
          f.rank_change_365d,
          f.share_in_top30,
          f.share_in_top50,
          f.share_in_top100,
          f.share_in_top500,
          f.trend_score
        FROM dim_asset a
        JOIN latest l ON TRUE
        LEFT JOIN fact_asset_snapshot_daily s ON s.asset_id = a.asset_id AND s.date = l.latest_date
        LEFT JOIN fact_asset_factor_daily f ON f.asset_id = a.asset_id AND f.date = l.latest_date
        WHERE a.symbol IN ({placeholders})
        ORDER BY COALESCE(s.rank_global, 999999), a.symbol
    """
    with _connect() as conn:
        rows = conn.execute(query, symbols).fetchall()
    return [
        {
            "asset_id": row[0],
            "symbol": row[1],
            "name": row[2],
            "market_cap_usd": float(row[3] or 0),
            "price_usd": float(row[4] or 0),
            "change_24h_pct": float(row[5] or 0),
            "rank_global": int(row[6]) if row[6] is not None else 0,
            "return_7d": float(row[7] or 0),
            "return_30d": float(row[8] or 0),
            "return_90d": float(row[9] or 0),
            "return_180d": float(row[10] or 0),
            "return_1y": float(row[11] or 0),
            "return_3y": float(row[12] or 0),
            "return_5y": float(row[13] or 0),
            "rank_change_90d": int(row[14]) if row[14] is not None else 0,
            "rank_change_180d": int(row[15]) if row[15] is not None else 0,
            "rank_change_1y": int(row[16]) if row[16] is not None else 0,
            "share_in_top30": float(row[17] or 0),
            "share_in_top50": float(row[18] or 0),
            "share_in_top100": float(row[19] or 0),
            "share_in_top500": float(row[20] or 0),
            "trend_score": float(row[21] or 0),
        }
        for row in rows
    ]


def get_top_assets(limit: int = 300) -> list[dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute(
            """
            WITH latest AS (
              SELECT MAX(date) AS latest_date FROM fact_asset_factor_daily
            )
            SELECT
              a.asset_id,
              a.name,
              a.symbol,
              s.rank_global,
              s.market_cap_usd,
              s.price_usd,
              s.change_24h_pct,
              f.return_7d,
              f.return_30d,
              f.return_60d,
              f.return_90d,
              f.return_180d,
              f.return_365d,
              f.return_3y,
              f.return_5y,
              f.rank_change_90d,
              f.rank_change_180d,
              f.rank_change_365d
            FROM dim_asset a
            JOIN latest l ON TRUE
            LEFT JOIN fact_asset_snapshot_daily s ON s.asset_id = a.asset_id AND s.date = l.latest_date
            LEFT JOIN fact_asset_factor_daily f ON f.asset_id = a.asset_id AND f.date = l.latest_date
            WHERE s.rank_global IS NOT NULL
            ORDER BY s.rank_global ASC
            LIMIT ?
            """,
            [limit],
        ).fetchall()
    return [
        {
            "asset_id": row[0],
            "name": row[1],
            "symbol": row[2],
            "rank_global": int(row[3]) if row[3] is not None else 0,
            "market_cap_usd": float(row[4] or 0),
            "price_usd": float(row[5] or 0),
            "change_24h_pct": float(row[6] or 0),
            "return_7d": float(row[7] or 0),
            "return_30d": float(row[8] or 0),
            "return_60d": float(row[9] or 0),
            "return_90d": float(row[10] or 0),
            "return_180d": float(row[11] or 0),
            "return_1y": float(row[12] or 0),
            "return_3y": float(row[13] or 0),
            "return_5y": float(row[14] or 0),
            "rank_change_90d": int(row[15]) if row[15] is not None else 0,
            "rank_change_180d": int(row[16]) if row[16] is not None else 0,
            "rank_change_1y": int(row[17]) if row[17] is not None else 0,
        }
        for row in rows
    ]


def get_rank_movers(limit: int = 20) -> list[dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute(
            """
            WITH latest AS (
              SELECT MAX(date) AS latest_date FROM fact_asset_factor_daily
            )
            SELECT a.symbol, a.name, s.rank_global, f.rank_change_90d, f.return_90d
            FROM fact_asset_factor_daily f
            JOIN latest l ON l.latest_date = f.date
            JOIN dim_asset a ON a.asset_id = f.asset_id
            LEFT JOIN fact_asset_snapshot_daily s ON s.asset_id = f.asset_id AND s.date = f.date
            WHERE f.rank_change_90d IS NOT NULL
            ORDER BY f.rank_change_90d ASC, COALESCE(s.rank_global, 999999) ASC
            LIMIT ?
            """,
            [limit],
        ).fetchall()
    return [
        {
            "symbol": row[0],
            "name": row[1],
            "rank_global": int(row[2]) if row[2] is not None else 0,
            "rank_change": int(row[3]),
            "return_period": float(row[4] or 0),
        }
        for row in rows
    ]


def get_anomalies(limit: int = 50) -> list[dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT e.event_id, a.symbol, e.event_type, e.severity, COALESCE(e.direction, ''), e.trigger_value, e.threshold_value, e.context
            FROM fact_anomaly_event e
            JOIN dim_asset a ON a.asset_id = e.asset_id
            ORDER BY e.date DESC, e.severity ASC
            LIMIT ?
            """,
            [limit],
        ).fetchall()
    return [
        {
            "event_id": row[0],
            "symbol": row[1],
            "event_type": row[2],
            "severity": row[3],
            "direction": row[4] or "UP",
            "summary": row[7] or row[2],
            "trigger_value": float(row[5] or 0),
            "threshold_value": float(row[6] or 0),
        }
        for row in rows
    ]


def get_asset_summary(asset_id: str) -> dict[str, Any]:
    with _connect() as conn:
        row = conn.execute(
            """
            WITH latest AS (
              SELECT MAX(date) AS latest_date FROM fact_asset_factor_daily
            )
            SELECT
              a.asset_id,
              a.symbol,
              a.name,
              s.market_cap_usd,
              s.price_usd,
              s.change_24h_pct,
              s.rank_global,
              f.return_7d,
              f.return_30d,
              f.return_90d,
              f.return_180d,
              f.return_365d,
              f.return_3y,
              f.return_5y,
              f.rank_change_90d,
              f.rank_change_180d,
              f.rank_change_365d,
              f.trend_score,
              f.share_in_top30,
              f.share_in_top50,
              f.share_in_top100,
              f.share_in_top500
            FROM dim_asset a
            JOIN latest l ON TRUE
            LEFT JOIN fact_asset_snapshot_daily s ON s.asset_id = a.asset_id AND s.date = l.latest_date
            LEFT JOIN fact_asset_factor_daily f ON f.asset_id = a.asset_id AND f.date = l.latest_date
            WHERE a.asset_id = ? OR lower(a.symbol) = lower(?)
            LIMIT 1
            """,
            [asset_id, asset_id],
        ).fetchone()
    if row is None:
        raise RuntimeError(f"Unknown asset: {asset_id}")
    return {
        "asset_id": row[0],
        "symbol": row[1],
        "name": row[2],
        "market_cap_usd": float(row[3] or 0),
        "price_usd": float(row[4] or 0),
        "change_24h_pct": float(row[5] or 0),
        "rank_global": int(row[6]) if row[6] is not None else 0,
        "return_7d": float(row[7] or 0),
        "return_30d": float(row[8] or 0),
        "return_90d": float(row[9] or 0),
        "return_180d": float(row[10] or 0),
        "return_1y": float(row[11] or 0),
        "return_3y": float(row[12] or 0),
        "return_5y": float(row[13] or 0),
        "rank_change_90d": int(row[14]) if row[14] is not None else 0,
        "rank_change_180d": int(row[15]) if row[15] is not None else 0,
        "rank_change_1y": int(row[16]) if row[16] is not None else 0,
        "trend_score": float(row[17] or 0),
        "share_in_top30": float(row[18] or 0),
        "share_in_top50": float(row[19] or 0),
        "share_in_top100": float(row[20] or 0),
        "share_in_top500": float(row[21] or 0),
    }


def get_asset_timeseries(asset_id: str) -> list[dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT s.date, s.price_usd, s.market_cap_usd, s.rank_global
            FROM fact_asset_snapshot_daily s
            JOIN dim_asset a ON a.asset_id = s.asset_id
            WHERE a.asset_id = ? OR lower(a.symbol) = lower(?)
            ORDER BY s.date ASC
            """,
            [asset_id, asset_id],
        ).fetchall()
    return [
        {
            "date": str(row[0]),
            "price_usd": float(row[1] or 0),
            "market_cap_usd": float(row[2] or 0),
            "rank_global": int(row[3]) if row[3] is not None else 0,
        }
        for row in rows
    ]


def get_asset_events(asset_id: str) -> list[dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT e.date, e.event_type, e.severity, e.context
            FROM fact_anomaly_event e
            JOIN dim_asset a ON a.asset_id = e.asset_id
            WHERE a.asset_id = ? OR lower(a.symbol) = lower(?)
            ORDER BY e.date DESC
            LIMIT 50
            """,
            [asset_id, asset_id],
        ).fetchall()
    return [
        {
            "date": str(row[0]),
            "event_type": row[1],
            "severity": row[2],
            "description": row[3] or row[1],
        }
        for row in rows
    ]
