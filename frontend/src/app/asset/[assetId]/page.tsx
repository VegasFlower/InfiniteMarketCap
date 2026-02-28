import Link from "next/link";

import { Card } from "@/components/Card";
import { watchlist } from "@/lib/mockData";

export default async function AssetDetail({ params }: { params: Promise<{ assetId: string }> }) {
  const { assetId } = await params;
  const asset = watchlist.find((item) => item.symbol.toLowerCase() === assetId) ?? watchlist[1];

  return (
    <main className="page">
      <section className="hero">
        <div className="eyebrow">Asset Detail</div>
        <h1>
          {asset.name} <span className="muted">{asset.symbol}</span>
        </h1>
        <p>
          Single-asset drilldown for market cap, rank persistence, and anomaly history. This page is wired for
          the future `/api/v1/assets/{assetId}` endpoints defined in the MVP spec.
        </p>
      </section>

      <section className="grid overview">
        <Card title="Market Cap">
          <div className="metric">{asset.marketCap}</div>
          <div className="metric-label">Current market cap</div>
        </Card>
        <Card title="Global Rank">
          <div className="metric">#{asset.rank}</div>
          <div className="metric-label">Latest known rank</div>
        </Card>
        <Card title="Trend Score">
          <div className="metric">{asset.trend}</div>
          <div className="metric-label">Composite trend score</div>
        </Card>
        <Card title="Mode">
          <div className="metric">Tracking</div>
          <div className="metric-label">Detail page scaffold</div>
        </Card>
      </section>

      <section className="grid main">
        <Card title="Price / Market Cap / Rank">
          <div className="mini-chart" />
          <div className="muted" style={{ marginTop: 12 }}>
            Chart placeholder. Replace with ECharts once backend timeseries is connected.
          </div>
        </Card>
        <Card title="Recent Events">
          <div className="timeline">
            <div className="event">
              <div className="badge">P1</div>
              <h3>Trend acceleration</h3>
              <p className="muted">Multi-period momentum remains positive while rank pressure improves.</p>
            </div>
            <div className="event">
              <div className="badge">P2</div>
              <h3>Ranking improvement</h3>
              <p className="muted">30-day rank change crossed the configured threshold.</p>
            </div>
          </div>
          <Link className="detail-link" href="/">
            Back to dashboard
          </Link>
        </Card>
      </section>
    </main>
  );
}
