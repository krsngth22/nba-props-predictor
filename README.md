# NBA Player Prop Predictor

An end-to-end machine learning system that predicts NBA player props (points, rebounds, assists) using XGBoost, with a PostgreSQL data pipeline, FastAPI backend, React dashboard, and AWS deployment.

## Tech Stack

- **Data**: Python, pandas, nba_api, PostgreSQL, Docker
- **ML**: XGBoost, scikit-learn, SHAP, MLflow, Optuna
- **Backend**: FastAPI, SQLAlchemy, Redis, JWT auth
- **Frontend**: React, TypeScript, Tailwind CSS, Recharts
- **DevOps**: Docker, AWS (EC2, RDS, S3, ECR), GitHub Actions

## Project Structure

    nba-props/
    ├── src/
    │   ├── ingestion/      # ETL pipeline (fetch, transform, load, validate)
    │   ├── models/         # ML model training and inference
    │   └── api/            # FastAPI backend
    ├── tests/              # pytest test suite (41 tests)
    ├── notebooks/          # Jupyter exploration notebooks
    ├── docs/               # Model cards and documentation
    ├── data/               # Local data and model artifacts
    └── logs/               # Pipeline log files

## Quick Start

### Prerequisites
- Docker Desktop
- Python 3.11+
- WSL (Windows) or Linux/Mac

### Setup

1. Clone the repo:

```bash
git clone https://github.com/krsngth22/nba-props-predictor.git
cd nba-props-predictor
```

2. Create virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Start the database:

```bash
make up
```

4. Apply the schema:

```bash
python src/ingestion/schema.py
```

5. Seed the data:

```bash
make pipeline
```

6. Check database health:

```bash
make health
```

## Make Commands

| Command | Description |
|---|---|
| `make up` | Start Docker containers |
| `make down` | Stop Docker containers |
| `make pipeline` | Run full data pipeline |
| `make pipeline-test` | Run pipeline with 3 players |
| `make test` | Run pytest suite |
| `make health` | Database health check |
| `make logs` | Tail pipeline logs |
| `make clean` | Remove cache files |

## Pipeline Architecture

```
NBA API → fetcher.py → transformer.py → validator.py → loader.py → PostgreSQL
```

- **fetcher.py** — pulls game logs from the NBA stats API with retry logic
- **transformer.py** — cleans and normalizes raw data into structured DataFrames
- **validator.py** — validates data quality before database insertion
- **loader.py** — bulk upserts data into PostgreSQL via psycopg2

## ML Architecture

```
PostgreSQL → features.py → trainer.py → tuner.py → predict.py
```

- **features.py** — engineers 39 features (rolling averages, lag features, efficiency metrics, opponent ratings)
- **trainer.py** — trains XGBoost models with TimeSeriesSplit cross-validation
- **tuner.py** — Optuna hyperparameter search (30 trials per model)
- **predict.py** — inference module for serving predictions
- **explainer.py** — SHAP feature importance and prediction explanations
- **backtest.py** — holdout evaluation simulating real prop betting

## Model Performance

| Metric | Points | Rebounds | Assists |
|---|---|---|---|
| MAE | 2.061 | 2.158 | 0.652 |
| Within 3 | 77.5% | 76.2% | 96.3% |
| Within 5 | 90.9% | 92.3% | 99.3% |
| Within 10 | 98.6% | 99.4% | 100.0% |
| Bet accuracy | 91.5% | 76.4% | 85.0% |

Models trained on 2 seasons of NBA data (~4,800 player-game records) across 50 active players.
Tuned with Optuna (30 trials), tracked with MLflow, explained with SHAP.

### Top Features (Points Model)
1. `points_per_minute` — scoring efficiency
2. `minutes_played_roll_10` — 10-game average minutes
3. `minutes_played_roll_20` — 20-game average minutes
4. `points_roll_20` — 20-game scoring average
5. `true_shooting_pct` — shooting efficiency

## Live Demo

*Coming soon after AWS deployment*

## Author

[@krsngth22](https://github.com/krsngth22)

## Running with Docker (Full Stack)

Start the entire stack — PostgreSQL, Redis, and the FastAPI backend — with one command:

```bash
docker compose up -d --build
```

Once running, the API is available at `http://localhost:8000` and the docs at `http://localhost:8000/docs`.

To seed data inside the dockerized environment, run the pipeline from your host machine — it connects to the same Postgres container via the exposed port 5433.

To stop everything:

```bash
docker compose down
```
