export type OverviewData = {
  date: string;
  top_n: number;
  total_market_cap_usd: number;
  top5_share: number;
  top10_share: number;
  advancers_ratio: number;
  median_return_7d: number;
  mean_return_7d: number;
};

export type WatchlistData = {
  asset_id: string;
  symbol: string;
  name: string;
  market_cap_usd: number;
  price_usd: number;
  change_24h_pct: number;
  rank_global: number;
  return_7d: number;
  return_30d: number;
  return_90d: number;
  return_180d: number;
  return_1y: number;
  return_3y: number;
  return_5y: number;
  rank_change_90d: number;
  rank_change_180d: number;
  rank_change_1y: number;
  share_in_top30: number;
  share_in_top50: number;
  share_in_top100: number;
  share_in_top500: number;
  trend_score: number;
};

export type TopAssetRow = {
  asset_id: string;
  name: string;
  symbol: string;
  rank_global: number;
  market_cap_usd: number;
  price_usd: number;
  change_24h_pct: number;
  return_7d: number;
  return_30d: number;
  return_60d: number;
  return_90d: number;
  return_180d: number;
  return_1y: number;
  return_3y: number;
  return_5y: number;
  rank_change_90d: number;
  rank_change_180d: number;
  rank_change_1y: number;
};

export type AnomalyData = {
  event_id: string;
  symbol: string;
  event_type: string;
  severity: string;
  direction: string;
  summary: string;
  trigger_value: number;
  threshold_value: number;
};

export type AssetEvent = {
  date: string;
  event_type: string;
  severity: string;
  description: string;
};

export const fallbackOverview: OverviewData = {
  date: "2026-03-06",
  top_n: 100,
  total_market_cap_usd: 53_200_000_000_000,
  top5_share: 0.318,
  top10_share: 0.472,
  advancers_ratio: 0.56,
  median_return_7d: 0.018,
  mean_return_7d: 0.024,
};

export const fallbackWatchlist: WatchlistData[] = [
  {
    asset_id: "gold",
    symbol: "GOLD",
    name: "Gold",
    market_cap_usd: 35_685_000_000_000,
    price_usd: 5132,
    change_24h_pct: 0.0197,
    rank_global: 1,
    return_7d: 0.012,
    return_30d: 0.038,
    return_90d: 0.081,
    return_180d: 0.146,
    return_1y: 0.234,
    return_3y: 0.462,
    return_5y: 0.781,
    rank_change_90d: 0,
    rank_change_180d: 0,
    rank_change_1y: 0,
    share_in_top30: 0.259,
    share_in_top50: 0.234,
    share_in_top100: 0.198,
    share_in_top500: 0.141,
    trend_score: 61,
  },
  {
    asset_id: "bitcoin",
    symbol: "BTC",
    name: "Bitcoin",
    market_cap_usd: 1_313_000_000_000,
    price_usd: 65676,
    change_24h_pct: -0.0307,
    rank_global: 13,
    return_7d: 0.076,
    return_30d: 0.164,
    return_90d: 0.243,
    return_180d: 0.311,
    return_1y: 0.398,
    return_3y: 0.864,
    return_5y: 1.722,
    rank_change_90d: -2,
    rank_change_180d: -3,
    rank_change_1y: -5,
    share_in_top30: 0.031,
    share_in_top50: 0.029,
    share_in_top100: 0.025,
    share_in_top500: 0.018,
    trend_score: 82,
  },
  {
    asset_id: "ethereum",
    symbol: "ETH",
    name: "Ethereum",
    market_cap_usd: 232_540_000_000,
    price_usd: 1926,
    change_24h_pct: -0.0566,
    rank_global: 81,
    return_7d: 0.043,
    return_30d: 0.092,
    return_90d: 0.141,
    return_180d: 0.193,
    return_1y: 0.244,
    return_3y: 0.522,
    return_5y: 1.138,
    rank_change_90d: -1,
    rank_change_180d: -1,
    rank_change_1y: -2,
    share_in_top30: 0,
    share_in_top50: 0,
    share_in_top100: 0.004,
    share_in_top500: 0.003,
    trend_score: 73,
  },
  {
    asset_id: "nvidia",
    symbol: "NVDA",
    name: "NVIDIA",
    market_cap_usd: 4_314_000_000_000,
    price_usd: 177.19,
    change_24h_pct: -0.0416,
    rank_global: 3,
    return_7d: 0.035,
    return_30d: 0.115,
    return_90d: 0.242,
    return_180d: 0.418,
    return_1y: 0.633,
    return_3y: 2.318,
    return_5y: 5.874,
    rank_change_90d: -1,
    rank_change_180d: -2,
    rank_change_1y: -3,
    share_in_top30: 0.076,
    share_in_top50: 0.071,
    share_in_top100: 0.061,
    share_in_top500: 0.044,
    trend_score: 79,
  },
];

export const fallbackTopAssets: TopAssetRow[] = fallbackWatchlist.map((asset) => ({
  asset_id: asset.asset_id,
  name: asset.name,
  symbol: asset.symbol,
  rank_global: asset.rank_global,
  market_cap_usd: asset.market_cap_usd,
  price_usd: asset.price_usd,
  change_24h_pct: asset.change_24h_pct,
  return_7d: asset.return_7d,
  return_30d: asset.return_30d,
  return_60d: (asset.return_30d + asset.return_90d) / 2,
  return_90d: asset.return_90d,
  return_180d: asset.return_180d,
  return_1y: asset.return_1y,
  return_3y: asset.return_3y,
  return_5y: asset.return_5y,
  rank_change_90d: asset.rank_change_90d,
  rank_change_180d: asset.rank_change_180d,
  rank_change_1y: asset.rank_change_1y,
}));

export const fallbackAnomalies: AnomalyData[] = [
  {
    event_id: "evt_btc_trend_accel",
    symbol: "BTC",
    event_type: "TREND_ACCEL",
    severity: "P1",
    direction: "UP",
    summary: "Trend score above 80 with rising rank momentum.",
    trigger_value: 82,
    threshold_value: 75,
  },
  {
    event_id: "evt_nvda_return_spike",
    symbol: "NVDA",
    event_type: "RETURN_SPIKE_UP",
    severity: "P2",
    direction: "UP",
    summary: "30-day return crossed configured threshold.",
    trigger_value: 0.115,
    threshold_value: 0.1,
  },
];

export function getFallbackAssetSummary(assetId: string): WatchlistData {
  const normalized = assetId.toLowerCase();
  return (
    fallbackWatchlist.find(
      (asset) => asset.asset_id.toLowerCase() === normalized || asset.symbol.toLowerCase() === normalized,
    ) ?? fallbackWatchlist[1]
  );
}

export const fallbackAssetEvents: AssetEvent[] = [
  {
    date: "2026-02-07",
    event_type: "TREND_ACCEL",
    severity: "P1",
    description: "Multi-period momentum remains positive while rank pressure improves.",
  },
  {
    date: "2026-01-15",
    event_type: "RANK_JUMP_UP",
    severity: "P2",
    description: "Rank moved up beyond configured threshold over medium horizon.",
  },
];
