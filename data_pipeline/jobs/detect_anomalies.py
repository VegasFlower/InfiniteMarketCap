from __future__ import annotations

from datetime import UTC, datetime
import json
import uuid

import pandas as pd

from common import ensure_db


def main() -> None:
    conn = ensure_db()
    latest_date = conn.execute("SELECT MAX(date) FROM fact_asset_factor_daily").fetchone()[0]
    if latest_date is None:
        raise RuntimeError("No factor data found. Run compute_factors.py first.")

    factors = conn.execute(
        "SELECT * FROM fact_asset_factor_daily WHERE date = ? ORDER BY trend_score DESC",
        [latest_date],
    ).fetchdf()
    assets = conn.execute("SELECT asset_id, symbol FROM dim_asset").fetchdf()
    merged = factors.merge(assets, on="asset_id", how="left")

    events: list[dict] = []
    for _, row in merged.iterrows():
        return_30d = row.get("return_30d")
        return_7d = row.get("return_7d")
        rank_change_30d = row.get("rank_change_30d")
        trend_score = row.get("trend_score")

        if pd.notna(return_7d) and float(return_7d) >= 0.10:
            events.append(
                {
                    "event_id": str(uuid.uuid4()),
                    "date": latest_date,
                    "asset_id": row["asset_id"],
                    "event_type": "RETURN_SPIKE_UP",
                    "severity": "P2",
                    "direction": "UP",
                    "trigger_value": float(return_7d),
                    "threshold_value": 0.10,
                    "context": json.dumps({"symbol": row["symbol"], "period": "7d"}),
                    "is_active": True,
                    "created_at": datetime.now(tz=UTC),
                }
            )
        if pd.notna(return_30d) and float(return_30d) <= -0.20:
            events.append(
                {
                    "event_id": str(uuid.uuid4()),
                    "date": latest_date,
                    "asset_id": row["asset_id"],
                    "event_type": "RETURN_SPIKE_DOWN",
                    "severity": "P2",
                    "direction": "DOWN",
                    "trigger_value": float(return_30d),
                    "threshold_value": -0.20,
                    "context": json.dumps({"symbol": row["symbol"], "period": "30d"}),
                    "is_active": True,
                    "created_at": datetime.now(tz=UTC),
                }
            )
        if pd.notna(rank_change_30d) and int(rank_change_30d) <= -5:
            events.append(
                {
                    "event_id": str(uuid.uuid4()),
                    "date": latest_date,
                    "asset_id": row["asset_id"],
                    "event_type": "RANK_JUMP_UP",
                    "severity": "P2",
                    "direction": "UP",
                    "trigger_value": float(rank_change_30d),
                    "threshold_value": -5.0,
                    "context": json.dumps({"symbol": row["symbol"], "period": "30d"}),
                    "is_active": True,
                    "created_at": datetime.now(tz=UTC),
                }
            )
        if pd.notna(trend_score) and float(trend_score) >= 75:
            events.append(
                {
                    "event_id": str(uuid.uuid4()),
                    "date": latest_date,
                    "asset_id": row["asset_id"],
                    "event_type": "TREND_ACCEL",
                    "severity": "P1" if float(trend_score) >= 85 else "P2",
                    "direction": "UP",
                    "trigger_value": float(trend_score),
                    "threshold_value": 75.0,
                    "context": json.dumps({"symbol": row["symbol"]}),
                    "is_active": True,
                    "created_at": datetime.now(tz=UTC),
                }
            )

    events_df = pd.DataFrame(events)
    conn.execute("DELETE FROM fact_anomaly_event WHERE date = ?", [latest_date])
    if events_df.empty:
        print(f"No anomalies detected for {latest_date}")
        return

    conn.register("events_df", events_df)
    conn.execute("INSERT INTO fact_anomaly_event SELECT * FROM events_df")
    print(f"Inserted {len(events_df)} anomaly events for {latest_date}")


if __name__ == "__main__":
    main()
