import {
  AssetEvent,
  AnomalyData,
  OverviewData,
  TopAssetRow,
  WatchlistData,
  fallbackAssetEvents,
  fallbackAnomalies,
  getFallbackAssetSummary,
  fallbackOverview,
  fallbackTopAssets,
  fallbackWatchlist,
} from "@/lib/mockData";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

async function fetchJson<T>(path: string, fallback: T): Promise<T> {
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      next: { revalidate: 3600 },
    });
    if (!response.ok) {
      return fallback;
    }
    return (await response.json()) as T;
  } catch {
    return fallback;
  }
}

export async function getOverview(topN = 100): Promise<OverviewData> {
  return fetchJson<OverviewData>(`/api/v1/dashboard/overview?top_n=${topN}`, fallbackOverview);
}

export async function getWatchlist(symbols: string[]): Promise<WatchlistData[]> {
  return fetchJson<WatchlistData[]>(
    `/api/v1/dashboard/watchlist?symbols=${encodeURIComponent(symbols.join(","))}`,
    fallbackWatchlist,
  );
}

export async function getTopAssets(limit: number): Promise<TopAssetRow[]> {
  return fetchJson<TopAssetRow[]>(`/api/v1/dashboard/top-assets?limit=${limit}`, fallbackTopAssets);
}

export async function getAnomalies(limit = 20): Promise<AnomalyData[]> {
  return fetchJson<AnomalyData[]>(`/api/v1/dashboard/anomalies?limit=${limit}`, fallbackAnomalies);
}

export async function getAssetSummary(assetId: string): Promise<WatchlistData> {
  return fetchJson<WatchlistData>(
    `/api/v1/assets/${encodeURIComponent(assetId)}/summary`,
    getFallbackAssetSummary(assetId),
  );
}

export async function getAssetEvents(assetId: string): Promise<AssetEvent[]> {
  return fetchJson<AssetEvent[]>(`/api/v1/assets/${encodeURIComponent(assetId)}/events`, fallbackAssetEvents);
}
