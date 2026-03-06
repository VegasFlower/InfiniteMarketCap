import Link from "next/link";

import { Card } from "@/components/Card";
import { getAnomalies, getOverview, getTopAssets, getWatchlist } from "@/lib/api";

function formatCurrency(value: number): string {
  if (!Number.isFinite(value) || value === 0) return "-";
  if (Math.abs(value) >= 1_000_000_000_000) return `$${(value / 1_000_000_000_000).toFixed(3)}T`;
  if (Math.abs(value) >= 1_000_000_000) return `$${(value / 1_000_000_000).toFixed(3)}B`;
  if (Math.abs(value) >= 1_000_000) return `$${(value / 1_000_000).toFixed(3)}M`;
  return `$${value.toFixed(2)}`;
}

function formatPercent(value: number): string {
  if (!Number.isFinite(value) || value === 0) return "0.00%";
  const sign = value > 0 ? "+" : "";
  return `${sign}${(value * 100).toFixed(2)}%`;
}

function pctClass(value: number): string {
  if (value > 0) return "pct-up";
  if (value < 0) return "pct-down";
  return "pct-flat";
}

export default async function Home() {
  const topAssetLimit = Number(process.env.NEXT_PUBLIC_TOP_ASSET_LIMIT ?? 300);
  const [overview, watchlist, topAssets, anomalies] = await Promise.all([
    getOverview(100),
    getWatchlist(["GOLD", "BTC", "ETH", "NVDA"]),
    getTopAssets(topAssetLimit),
    getAnomalies(12),
  ]);

  const gold = watchlist.find((asset) => asset.symbol === "GOLD");
  const btc = watchlist.find((asset) => asset.symbol === "BTC");

  return (
    <main className="page">
      <section className="hero">
        <div className="eyebrow">InfiniteMarketCap</div>
        <h1>Global Top Assets, Long-Term Trends, and Rank Regime Shifts.</h1>
        <p>
          Built for daily macro monitoring: top asset leaderboard, long-horizon returns, concentration shares, and
          anomaly signals for early trend detection.
        </p>
      </section>

      <section className="grid overview">
        <Card title="Top 100 Total Market Cap">
          <div className="metric">{formatCurrency(overview.total_market_cap_usd)}</div>
          <div className="metric-label">Data date: {overview.date}</div>
        </Card>
        <Card title="Gold Share in Top 100">
          <div className="metric">{formatPercent(gold?.share_in_top100 ?? 0)}</div>
          <div className="metric-label">Gold market cap: {formatCurrency(gold?.market_cap_usd ?? 0)}</div>
        </Card>
        <Card title="BTC Rank Trend (1Y)">
          <div className="metric">{btc ? `#${btc.rank_global}` : "-"}</div>
          <div className="metric-label">Rank change 3M/6M/1Y: {btc?.rank_change_90d ?? 0} / {btc?.rank_change_180d ?? 0} / {btc?.rank_change_1y ?? 0}</div>
        </Card>
        <Card title="Market Breadth 7D">
          <div className="metric">{formatPercent(overview.advancers_ratio)}</div>
          <div className="metric-label">Median 7D return: {formatPercent(overview.median_return_7d)}</div>
        </Card>
      </section>

      <section className="grid main">
        <div className="grid">
          <Card title="Watchlist Snapshot (GOLD / BTC / ETH / NVDA)">
            <div className="table">
              {watchlist.map((asset) => (
                <div className="table-row watchlist-row" key={asset.symbol}>
                  <div>
                    <div className="symbol">{asset.symbol}</div>
                    <div className="muted">{asset.name}</div>
                  </div>
                  <div>
                    <div>{formatCurrency(asset.market_cap_usd)}</div>
                    <div className="muted">Rank #{asset.rank_global}</div>
                  </div>
                  <div className={pctClass(asset.return_90d)}>90D {formatPercent(asset.return_90d)}</div>
                  <div className={pctClass(asset.return_1y)}>1Y {formatPercent(asset.return_1y)}</div>
                  <Link href={`/asset/${asset.symbol.toLowerCase()}`}>Open</Link>
                </div>
              ))}
            </div>
          </Card>
        </div>

        <Card title="Anomaly Radar">
          <div className="timeline">
            {anomalies.map((item) => (
              <div className="event" key={item.event_id}>
                <div className="badge">{item.severity}</div>
                <h3>
                  {item.symbol}: {item.event_type}
                </h3>
                <p className="muted">{item.summary}</p>
              </div>
            ))}
          </div>
        </Card>
      </section>

      <section className="grid leaderboard-section">
        <Card title={`Asset Leaderboard (Top ${topAssetLimit})`}>
          <div className="leaderboard-table-wrap">
            <table className="leaderboard-table">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Name</th>
                  <th>Symbol</th>
                  <th>Market Cap</th>
                  <th>Price</th>
                  <th>24H</th>
                  <th>7D</th>
                  <th>30D</th>
                  <th>60D</th>
                  <th>90D</th>
                  <th>180D</th>
                  <th>1Y</th>
                  <th>3Y</th>
                  <th>5Y</th>
                  <th>Rank Δ 3M</th>
                  <th>Rank Δ 6M</th>
                  <th>Rank Δ 1Y</th>
                </tr>
              </thead>
              <tbody>
                {topAssets.map((row) => (
                  <tr key={row.asset_id}>
                    <td>{row.rank_global}</td>
                    <td className="strong">{row.name}</td>
                    <td>{row.symbol}</td>
                    <td>{formatCurrency(row.market_cap_usd)}</td>
                    <td>{formatCurrency(row.price_usd)}</td>
                    <td className={pctClass(row.change_24h_pct)}>{formatPercent(row.change_24h_pct)}</td>
                    <td className={pctClass(row.return_7d)}>{formatPercent(row.return_7d)}</td>
                    <td className={pctClass(row.return_30d)}>{formatPercent(row.return_30d)}</td>
                    <td className={pctClass(row.return_60d)}>{formatPercent(row.return_60d)}</td>
                    <td className={pctClass(row.return_90d)}>{formatPercent(row.return_90d)}</td>
                    <td className={pctClass(row.return_180d)}>{formatPercent(row.return_180d)}</td>
                    <td className={pctClass(row.return_1y)}>{formatPercent(row.return_1y)}</td>
                    <td className={pctClass(row.return_3y)}>{formatPercent(row.return_3y)}</td>
                    <td className={pctClass(row.return_5y)}>{formatPercent(row.return_5y)}</td>
                    <td>{row.rank_change_90d}</td>
                    <td>{row.rank_change_180d}</td>
                    <td>{row.rank_change_1y}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      </section>
    </main>
  );
}
