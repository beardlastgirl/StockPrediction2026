# StockPrediction2026

Event study of S&P 500 reactions to dated events.

## Commands
- `run_eventstudy.bat init-db`
- `run_eventstudy.bat fetch-prices`
- `run_eventstudy.bat migrate-legacy`
- `run_eventstudy.bat run-study`
- `run_eventstudy.bat pattern-detect`
- `run_eventstudy.bat predict --type "Geopolitical shock" --horizon 5`

Politician pipeline:
- `python run_politician_study.py`

Outputs: `reports/study_results.csv`, `reports/politician_study_results.csv`, `reports/patterns.json`.
