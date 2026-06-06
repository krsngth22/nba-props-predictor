.PHONY: up down pipeline pipeline-test scheduler test health logs clean

up:
	docker compose up -d

down:
	docker compose down

pipeline:
	python -c "import sys; sys.path.insert(0, 'src'); from ingestion.pipeline import run_pipeline; run_pipeline()"

pipeline-test:
	python -c "import sys; sys.path.insert(0, 'src'); from ingestion.pipeline import run_pipeline; run_pipeline(max_players=3)"

scheduler:
	python src/ingestion/scheduler.py

schema:
	python src/ingestion/schema.py

health:
	python src/ingestion/health_check.py

test:
	pytest -v

logs:
	tail -f logs/pipeline_*.log

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
