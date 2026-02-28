CREATE TABLE IF NOT EXISTS dim_asset (
  asset_id TEXT PRIMARY KEY,
  symbol TEXT NOT NULL,
  name TEXT NOT NULL,
  asset_type TEXT NOT NULL,
  exchange TEXT,
  currency TEXT,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS fact_asset_snapshot_daily (
  date DATE NOT NULL,
  asset_id TEXT NOT NULL,
  price_usd DOUBLE,
  market_cap_usd DOUBLE NOT NULL,
  volume_usd DOUBLE,
  rank_global INTEGER,
  rank_in_type INTEGER,
  source TEXT NOT NULL,
  ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (date, asset_id)
);

CREATE TABLE IF NOT EXISTS agg_topn_daily (
  date DATE NOT NULL,
  top_n INTEGER NOT NULL,
  total_market_cap_usd DOUBLE NOT NULL,
  top5_share DOUBLE,
  top10_share DOUBLE,
  advancers_ratio DOUBLE,
  median_return_7d DOUBLE,
  mean_return_7d DOUBLE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (date, top_n)
);

CREATE TABLE IF NOT EXISTS fact_asset_factor_daily (
  date DATE NOT NULL,
  asset_id TEXT NOT NULL,
  return_7d DOUBLE,
  return_30d DOUBLE,
  return_60d DOUBLE,
  return_90d DOUBLE,
  mcap_change_30d DOUBLE,
  rank_change_7d INTEGER,
  rank_change_30d INTEGER,
  rank_change_90d INTEGER,
  share_in_top30 DOUBLE,
  share_in_top50 DOUBLE,
  share_in_top100 DOUBLE,
  share_in_top500 DOUBLE,
  rel_strength_vs_top100_30d DOUBLE,
  trend_score DOUBLE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (date, asset_id)
);

CREATE TABLE IF NOT EXISTS fact_anomaly_event (
  event_id TEXT PRIMARY KEY,
  date DATE NOT NULL,
  asset_id TEXT NOT NULL,
  event_type TEXT NOT NULL,
  severity TEXT NOT NULL,
  direction TEXT,
  trigger_value DOUBLE,
  threshold_value DOUBLE,
  context JSON,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
