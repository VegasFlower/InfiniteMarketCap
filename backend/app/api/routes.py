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
from app.services import mock_data

router = APIRouter(prefix="/api/v1")


@router.get("/health")
def healthcheck() -> dict:
    return {"status": "ok"}


@router.get("/dashboard/overview", response_model=OverviewResponse)
def dashboard_overview(top_n: int = Query(default=100, ge=30, le=500)) -> dict:
    return mock_data.get_overview(top_n)


@router.get("/dashboard/watchlist", response_model=list[WatchlistAsset])
def dashboard_watchlist(symbols: str = "GOLD,BTC,ETH,NVDA") -> list[dict]:
    return mock_data.get_watchlist(symbols.split(","))


@router.get("/dashboard/rank-movers", response_model=list[RankMover])
def dashboard_rank_movers() -> list[dict]:
    return mock_data.get_rank_movers()


@router.get("/dashboard/anomalies", response_model=list[AnomalyEvent])
def dashboard_anomalies() -> list[dict]:
    return mock_data.get_anomalies()


@router.get("/assets/{asset_id}/summary", response_model=AssetSummary)
def asset_summary(asset_id: str) -> dict:
    return mock_data.get_asset_summary(asset_id)


@router.get("/assets/{asset_id}/timeseries", response_model=list[TimeseriesPoint])
def asset_timeseries(asset_id: str) -> list[dict]:
    return mock_data.get_asset_timeseries(asset_id)


@router.get("/assets/{asset_id}/events", response_model=list[AssetEvent])
def asset_events(asset_id: str) -> list[dict]:
    return mock_data.get_asset_events(asset_id)
