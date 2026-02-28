# InfiniteMarketCap

Global market-cap dashboard for tracking the world's largest assets, their rankings, concentration, and anomaly signals.

## Structure

- `docs/`: product and technical docs
- `backend/`: FastAPI service
- `data_pipeline/`: daily ingestion and factor jobs
- `frontend/`: Next.js dashboard
- `.github/workflows/`: CI and scheduled jobs

## Real data sources

- `CompaniesMarketCap`: current top-asset ranking and historical market-cap/price pages for supported assets
- `CoinGecko API`: historical price and market-cap data for crypto assets such as BTC and ETH

## Current limitations

- Historical global ranks are only available from snapshots collected by this project going forward.
- For some non-equity assets such as gold, historical market cap is available before historical price is.
- The system currently backfills detailed history only for tracked assets: `GOLD`, `BTC`, `ETH`, `NVDA`.

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
cd jobs
python pull_assets.py
python normalize_assets.py
python compute_factors.py
python detect_anomalies.py
```
