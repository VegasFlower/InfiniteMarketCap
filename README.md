# InfiniteMarketCap

Global market-cap dashboard for tracking the world's largest assets, their rankings, concentration, and anomaly signals.

## Structure

- `docs/`: product and technical docs
- `backend/`: FastAPI service
- `data_pipeline/`: daily ingestion and factor jobs
- `frontend/`: Next.js dashboard
- `.github/workflows/`: CI and scheduled jobs

## Real data sources

- `CompaniesMarketCap`: top-asset ranking (paginated) and historical market-cap/price pages
- `Stooq`: fallback long-range daily price history for assets that have no historical chart page (e.g. BTC/ETH/Gold)

## Current limitations

- Historical global ranks are only available from snapshots collected by this project going forward.
- For some non-equity assets such as gold, historical market cap is available before historical price is.
- Some assets (especially specific crypto rows) may not expose full history pages on the source site.
- Historical global rank changes become more accurate as daily snapshots accumulate.

## Quick start

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Data pipeline

```bash
cd data_pipeline
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export TOP_ASSET_LIMIT=300  # can set to 500 or 1000
cd jobs
python pull_assets.py
python normalize_assets.py
python compute_factors.py
python detect_anomalies.py
```
