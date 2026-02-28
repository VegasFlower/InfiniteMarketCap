import Link from "next/link";

import { Card } from "@/components/Card";
import { anomalies, overview, watchlist } from "@/lib/mockData";

export default function Home() {
  return (
    <main className="page">
      <section className="hero">
        <div className="eyebrow">InfiniteMarketCap</div>
        <h1>See the market structure before the narrative catches up.</h1>
        <p>
          Track global asset rankings, concentration, and anomaly signals from gold to crypto to mega-cap equities.
          The dashboard is designed for daily macro check-ins and early trend detection.
        </p>
      </section>

      <section className="grid overview">
        <Card title="Top 100 Total Market Cap">
          <div className="metric">{overview.totalMarketCap}</div>
          <div className="metric-label">Daily macro footprint</div>
        </Card>
        <Card title="Top 5 Share">
          <div className="metric">{overview.top5Share}</div>
          <div className="metric-label">Concentration in the largest assets</div>
        </Card>
        <Card title="Top 10 Share">
          <div className="metric">{overview.top10Share}</div>
          <div className="metric-label">Breadth vs centralization</div>
        </Card>
        <Card title="Advancers Ratio">
          <div className="metric">{overview.advancersRatio}</div>
          <div className="metric-label">Share of assets rising over 7D</div>
        </Card>
      </section>

      <section className="grid main">
        <div className="grid">
          <Card title="Watchlist Snapshot">
            <div className="table">
              {watchlist.map((asset) => (
                <div className="table-row" key={asset.symbol}>
                  <div>
                    <div className="symbol">{asset.symbol}</div>
                    <div className="muted">{asset.name}</div>
                  </div>
                  <div>
                    <div>{asset.marketCap}</div>
                    <div className="muted">Rank #{asset.rank}</div>
                  </div>
                  <div>Trend {asset.trend}</div>
                  <Link href={`/asset/${asset.symbol.toLowerCase()}`}>Open</Link>
                </div>
              ))}
            </div>
          </Card>
          <Card title="Trend Shape">
            <div className="mini-chart" />
            <Link className="detail-link" href="/asset/btc">
              Inspect BTC detail
            </Link>
          </Card>
        </div>

        <Card title="Anomaly Radar">
          <div className="timeline">
            {anomalies.map((item) => (
              <div className="event" key={item.symbol + item.title}>
                <div className="badge">{item.severity}</div>
                <h3>{item.symbol}: {item.title}</h3>
                <p className="muted">{item.detail}</p>
              </div>
            ))}
          </div>
        </Card>
      </section>
    </main>
  );
}
