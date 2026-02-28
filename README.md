# InfiniteMarketCap

Global market-cap dashboard for tracking the world's largest assets, their rankings, concentration, and anomaly signals.

## Structure

- `docs/`: product and technical docs
- `backend/`: FastAPI service
- `data_pipeline/`: daily ingestion and factor jobs
- `frontend/`: Next.js dashboard
- `.github/workflows/`: CI and scheduled jobs

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
python jobs/pull_assets.py
python jobs/normalize_assets.py
python jobs/compute_factors.py
python jobs/detect_anomalies.py
```
