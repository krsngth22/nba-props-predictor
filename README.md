# NBA Player Prop Predictor

An end-to-end machine learning system that predicts NBA player props (points, rebounds, assists) using XGBoost, with a PostgreSQL data pipeline, FastAPI backend, React dashboard, and AWS deployment.

## Tech Stack

- **Data**: Python, pandas, nba_api, PostgreSQL, Docker
- **ML**: XGBoost, scikit-learn, SHAP, MLflow
- **Backend**: FastAPI, SQLAlchemy, Redis, JWT auth
- **Frontend**: React, TypeScript, Tailwind CSS, Recharts
- **DevOps**: Docker, AWS (EC2, RDS, S3, ECR), GitHub Actions

## Project Structure

    nba-props/
    ├── src/
    │   ├── ingestion/      # ETL pipeline (fetch, transform, load, validate)
    │   ├── models/         # ML model training and inference
    │   └── api/            # FastAPI backend
    ├── tests/              # pytest test suite
    ├── notebooks/          # Jupyter exploration notebooks
    ├── data/               # Local data files
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

## Model Performance

*Coming soon in Phase 2*

## Live Demo

*Coming soon after AWS deployment*

## Author

[@krsngth22](https://github.com/krsngth22)
