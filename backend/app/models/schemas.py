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
    symbol: str
    name: str
    market_cap_usd: float
    rank_global: int
    return_7d: float
    return_30d: float
    rank_change_30d: int
    share_in_top100: float
    trend_score: float


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
    rank_global: int
    return_7d: float
    return_30d: float
    return_90d: float
    trend_score: float
    share_in_top100: float


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
