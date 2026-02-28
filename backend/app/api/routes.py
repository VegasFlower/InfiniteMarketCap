from fastapi import APIRouter, Query

from app.models.schemas import (
    AnomalyEvent,
    AssetEvent,
    AssetSummary,
    OverviewResponse,
    RankMover,
    TimeseriesPoint,
    WatchlistAsset,
)
from app.services import data_store, mock_data

router = APIRouter(prefix="/api/v1")


@router.get("/health")
def healthcheck() -> dict:
    return {"status": "ok"}


@router.get("/dashboard/overview", response_model=OverviewResponse)
def dashboard_overview(top_n: int = Query(default=100, ge=30, le=500)) -> dict:
    if data_store.has_real_data():
        return data_store.get_overview(top_n)
    return mock_data.get_overview(top_n)


@router.get("/dashboard/watchlist", response_model=list[WatchlistAsset])
def dashboard_watchlist(symbols: str = "GOLD,BTC,ETH,NVDA") -> list[dict]:
    symbol_list = [symbol.strip().upper() for symbol in symbols.split(",") if symbol.strip()]
    if data_store.has_real_data():
        return data_store.get_watchlist(symbol_list)
    return mock_data.get_watchlist(symbol_list)


@router.get("/dashboard/rank-movers", response_model=list[RankMover])
def dashboard_rank_movers(limit: int = Query(default=20, ge=1, le=100)) -> list[dict]:
    if data_store.has_real_data():
        return data_store.get_rank_movers(limit)
    return mock_data.get_rank_movers()[:limit]


@router.get("/dashboard/anomalies", response_model=list[AnomalyEvent])
def dashboard_anomalies(limit: int = Query(default=50, ge=1, le=100)) -> list[dict]:
    if data_store.has_real_data():
        return data_store.get_anomalies(limit)
    return mock_data.get_anomalies()[:limit]


@router.get("/assets/{asset_id}/summary", response_model=AssetSummary)
def asset_summary(asset_id: str) -> dict:
    if data_store.has_real_data():
        return data_store.get_asset_summary(asset_id)
    return mock_data.get_asset_summary(asset_id)


@router.get("/assets/{asset_id}/timeseries", response_model=list[TimeseriesPoint])
def asset_timeseries(asset_id: str) -> list[dict]:
    if data_store.has_real_data():
        return data_store.get_asset_timeseries(asset_id)
    return mock_data.get_asset_timeseries(asset_id)


@router.get("/assets/{asset_id}/events", response_model=list[AssetEvent])
def asset_events(asset_id: str) -> list[dict]:
    if data_store.has_real_data():
        return data_store.get_asset_events(asset_id)
    return mock_data.get_asset_events(asset_id)
