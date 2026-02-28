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
    placeholders = ",".join("?" for _ in symbols)
    query = f"""
        WITH latest AS (
          SELECT MAX(date) AS latest_date FROM fact_asset_factor_daily
        )
        SELECT
          a.symbol,
          a.name,
          s.market_cap_usd,
          s.rank_global,
          f.return_7d,
          f.return_30d,
          f.rank_change_30d,
          f.share_in_top100,
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
            "symbol": row[0],
            "name": row[1],
            "market_cap_usd": float(row[2] or 0),
            "rank_global": int(row[3]) if row[3] is not None else 0,
            "return_7d": float(row[4] or 0),
            "return_30d": float(row[5] or 0),
            "rank_change_30d": int(row[6]) if row[6] is not None else 0,
            "share_in_top100": float(row[7] or 0),
            "trend_score": float(row[8] or 0),
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
            SELECT a.symbol, a.name, s.rank_global, f.rank_change_30d, f.return_30d
            FROM fact_asset_factor_daily f
            JOIN latest l ON l.latest_date = f.date
            JOIN dim_asset a ON a.asset_id = f.asset_id
            LEFT JOIN fact_asset_snapshot_daily s ON s.asset_id = f.asset_id AND s.date = f.date
            WHERE f.rank_change_30d IS NOT NULL
            ORDER BY f.rank_change_30d ASC, COALESCE(s.rank_global, 999999) ASC
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
            SELECT a.asset_id, a.symbol, a.name, s.market_cap_usd, s.rank_global, f.return_7d, f.return_30d, f.return_90d, f.trend_score, f.share_in_top100
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
        "rank_global": int(row[4]) if row[4] is not None else 0,
        "return_7d": float(row[5] or 0),
        "return_30d": float(row[6] or 0),
        "return_90d": float(row[7] or 0),
        "trend_score": float(row[8] or 0),
        "share_in_top100": float(row[9] or 0),
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
