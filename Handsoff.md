# Handoff

## Objective
Event-study S&P 500 reactions to dated events, with a separate politician-trade pipeline.

## Completed
- Phase 1 scaffold + smoke test.
- Implemented modules: db, events, taxonomy, migrate_legacy, prices, returns, stats, study, patterns, predict, migrate_politician.
- CLI: init-db, fetch-prices, migrate-legacy, run-study, pattern-detect, predict (polymorphic --db not implemented).
- Runners: run_eventstudy.ps1/bat, run_politician_study.ps1 + .py.
- World pipeline run: 288 events, 6747 prices, significant 3/5/10-day negative CAR.
- Politician pipeline run: 41 anomalies, significant CAR effects.
- Patterns saved to reports/patterns.json; study results to reports/study_results.csv and politician_study_results.csv.

## Validation
- ruff clean
- pytest 1 passed
- fetch-prices/migrate-legacy/run-study verified

## Next
- Slice patterns by event_type for stronger signals.
- Add sector-level abnormal returns and robustness tests.
- Optional: FRED macro context (ALFRED vintages).
- Politician DB/run-study separation currently relies on separate DB file; CLI --db flag not implemented.

## Constraints
- Keep world vs politician data separate.
- Do not ingest .venv/data/*.duckdb into git.
