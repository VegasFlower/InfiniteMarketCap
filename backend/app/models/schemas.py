from pydantic import BaseModel


class OverviewResponse(BaseModel):
    date: str
    top_n: int
    total_market_cap_usd: float
    top5_share: float
    top10_share: float
    advancers_ratio: float
    median_return_7d: float
    mean_return_7d: float


class WatchlistAsset(BaseModel):
    asset_id: str
    symbol: str
    name: str
    market_cap_usd: float
    price_usd: float
    change_24h_pct: float
    rank_global: int
    return_7d: float
    return_30d: float
    return_90d: float
    return_180d: float
    return_1y: float
    return_3y: float
    return_5y: float
    rank_change_90d: int
    rank_change_180d: int
    rank_change_1y: int
    share_in_top30: float
    share_in_top50: float
    share_in_top100: float
    share_in_top500: float
    trend_score: float


class TopAssetRow(BaseModel):
    asset_id: str
    name: str
    symbol: str
    rank_global: int
    market_cap_usd: float
    price_usd: float
    change_24h_pct: float
    return_7d: float
    return_30d: float
    return_60d: float
    return_90d: float
    return_180d: float
    return_1y: float
    return_3y: float
    return_5y: float
    rank_change_90d: int
    rank_change_180d: int
    rank_change_1y: int


class RankMover(BaseModel):
    symbol: str
    name: str
    rank_global: int
    rank_change: int
    return_period: float


class AnomalyEvent(BaseModel):
    event_id: str
    symbol: str
    event_type: str
    severity: str
    direction: str
    summary: str
    trigger_value: float
    threshold_value: float


class AssetSummary(BaseModel):
    asset_id: str
    symbol: str
    name: str
    market_cap_usd: float
    price_usd: float
    change_24h_pct: float
    rank_global: int
    return_7d: float
    return_30d: float
    return_90d: float
    return_180d: float
    return_1y: float
    return_3y: float
    return_5y: float
    rank_change_90d: int
    rank_change_180d: int
    rank_change_1y: int
    trend_score: float
    share_in_top30: float
    share_in_top50: float
    share_in_top100: float
    share_in_top500: float


class TimeseriesPoint(BaseModel):
    date: str
    price_usd: float
    market_cap_usd: float
    rank_global: int


class AssetEvent(BaseModel):
    date: str
    event_type: str
    severity: str
    description: str
