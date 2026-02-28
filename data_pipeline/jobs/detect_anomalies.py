from datetime import date, datetime
import json

import pandas as pd

from common import ensure_db


def main() -> None:
    conn = ensure_db()
    factors = conn.execute(
        "SELECT * FROM fact_asset_factor_daily WHERE date = ? ORDER BY trend_score DESC",
        [date.today().isoformat()],
    ).fetchdf()
    if factors.empty:
        raise RuntimeError("No factor data found. Run compute_factors.py first.")

    assets = conn.execute("SELECT asset_id, symbol FROM dim_asset").fetchdf()
    merged = factors.merge(assets, on="asset_id", how="left")
    events = []
    for _, row in merged.iterrows():
        if row["return_30d"] >= 0.10:
            events.append(
                {
                    "event_id": f"{row['asset_id']}_return_spike_up",
                    "date": date.today().isoformat(),
                    "asset_id": row["asset_id"],
                    "event_type": "RETURN_SPIKE_UP",
                    "severity": "P2",
                    "direction": "UP",
                    "trigger_value": row["return_30d"],
                    "threshold_value": 0.10,
                    "context": json.dumps({"symbol": row["symbol"], "period": "30d"}),
                    "is_active": True,
                    "created_at": datetime.utcnow(),
                }
            )
        if row["trend_score"] >= 75:
            events.append(
                {
                    "event_id": f"{row['asset_id']}_trend_accel",
                    "date": date.today().isoformat(),
                    "asset_id": row["asset_id"],
                    "event_type": "TREND_ACCEL",
                    "severity": "P1" if row["trend_score"] >= 80 else "P2",
                    "direction": "UP",
                    "trigger_value": row["trend_score"],
                    "threshold_value": 75.0,
                    "context": json.dumps({"symbol": row["symbol"]}),
                    "is_active": True,
                    "created_at": datetime.utcnow(),
                }
            )

    events_df = pd.DataFrame(events)
    if events_df.empty:
        print("No anomalies detected")
        return

    conn.register("events_df", events_df)
    conn.execute("DELETE FROM fact_anomaly_event WHERE date = ?", [date.today().isoformat()])
    conn.execute("INSERT INTO fact_anomaly_event SELECT * FROM events_df")
    print(f"Inserted {len(events_df)} anomaly events")


if __name__ == "__main__":
    main()
