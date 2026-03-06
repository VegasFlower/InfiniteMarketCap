import Link from "next/link";

import { Card } from "@/components/Card";
import { getAssetEvents, getAssetSummary } from "@/lib/api";

function formatCurrency(value: number): string {
  if (!Number.isFinite(value) || value === 0) return "-";
  if (Math.abs(value) >= 1_000_000_000_000) return `$${(value / 1_000_000_000_000).toFixed(3)}T`;
  if (Math.abs(value) >= 1_000_000_000) return `$${(value / 1_000_000_000).toFixed(3)}B`;
  return `$${value.toFixed(2)}`;
}

function formatPercent(value: number): string {
  const sign = value > 0 ? "+" : "";
  return `${sign}${(value * 100).toFixed(2)}%`;
}

function pctClass(value: number): string {
  if (value > 0) return "pct-up";
  if (value < 0) return "pct-down";
  return "pct-flat";
}

export default async function AssetDetail({ params }: { params: Promise<{ assetId: string }> }) {
  const { assetId } = await params;
  const [asset, events] = await Promise.all([getAssetSummary(assetId), getAssetEvents(assetId)]);

  return (
    <main className="page">
      <section className="hero">
        <div className="eyebrow">Asset Detail</div>
        <h1>
          {asset.name} <span className="muted">{asset.symbol}</span>
        </h1>
        <p>
          Daily snapshot with long-horizon returns, rank shifts, and concentration share in Top30/50/100/500.
        </p>
      </section>

      <section className="grid overview">
        <Card title="Market Cap">
          <div className="metric">{formatCurrency(asset.market_cap_usd)}</div>
          <div className="metric-label">Current market cap</div>
        </Card>
        <Card title="Global Rank">
          <div className="metric">#{asset.rank_global}</div>
          <div className="metric-label">3M/6M/1Y: {asset.rank_change_90d} / {asset.rank_change_180d} / {asset.rank_change_1y}</div>
        </Card>
        <Card title="24H / 90D / 1Y">
          <div className={`metric ${pctClass(asset.change_24h_pct)}`}>{formatPercent(asset.change_24h_pct)}</div>
          <div className="metric-label">
            <span className={pctClass(asset.return_90d)}>90D {formatPercent(asset.return_90d)}</span> ·{" "}
            <span className={pctClass(asset.return_1y)}>1Y {formatPercent(asset.return_1y)}</span>
          </div>
        </Card>
        <Card title="TopN Share">
          <div className="metric">{formatPercent(asset.share_in_top100)}</div>
          <div className="metric-label">Top30/50/500: {formatPercent(asset.share_in_top30)} / {formatPercent(asset.share_in_top50)} / {formatPercent(asset.share_in_top500)}</div>
        </Card>
      </section>

      <section className="grid main">
        <Card title="Return Regime">
          <div className="table">
            <div className="table-row simple-row"><div>7D</div><div className={pctClass(asset.return_7d)}>{formatPercent(asset.return_7d)}</div></div>
            <div className="table-row simple-row"><div>30D</div><div className={pctClass(asset.return_30d)}>{formatPercent(asset.return_30d)}</div></div>
            <div className="table-row simple-row"><div>90D</div><div className={pctClass(asset.return_90d)}>{formatPercent(asset.return_90d)}</div></div>
            <div className="table-row simple-row"><div>180D</div><div className={pctClass(asset.return_180d)}>{formatPercent(asset.return_180d)}</div></div>
            <div className="table-row simple-row"><div>1Y</div><div className={pctClass(asset.return_1y)}>{formatPercent(asset.return_1y)}</div></div>
            <div className="table-row simple-row"><div>3Y</div><div className={pctClass(asset.return_3y)}>{formatPercent(asset.return_3y)}</div></div>
            <div className="table-row simple-row"><div>5Y</div><div className={pctClass(asset.return_5y)}>{formatPercent(asset.return_5y)}</div></div>
          </div>
        </Card>

        <Card title="Recent Events">
          <div className="timeline">
            {events.map((event) => (
              <div className="event" key={`${event.date}-${event.event_type}`}>
                <div className="badge">{event.severity}</div>
                <h3>{event.event_type}</h3>
                <p className="muted">{event.description}</p>
              </div>
            ))}
          </div>
          <Link className="detail-link" href="/">
            Back to dashboard
          </Link>
        </Card>
      </section>
    </main>
  );
}
