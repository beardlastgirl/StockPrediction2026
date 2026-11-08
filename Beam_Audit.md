# Comprehensive Repository Audit: StockPrediction2026

## A. Executive Summary

**Overall project health:** A working, small-scale Python data pipeline for event studies of S&P 500 reactions. Core flow (fetch prices → migrate events → run study → pattern detect → predict) runs and produces outputs. Code is lint-clean and the single smoke test passes. However, it is research-grade rather than production-grade, with minimal tests, loose architecture, canonical-data issues, and reliance on external machine-local data.

**Architecture assessment:** Simple layered modules (`db`, `events`, `prices`, `returns`, `stats`, `study`, `patterns`, `predict`) are easy to follow, but boundaries are blurry: event taxonomy is declared but not enforced; world and politician pipelines overlap conceptually; report generation and DB writes are mixed; daily-return table exists but is unused. The architecture is adequate for one user's research, not for reproducible or multi-developer work.

**Most important discoveries:**
1. Event types are not canonicalized; the DB contains 50+ inconsistent variants of ~7 intended categories, so pattern/prediction keys are fragmented and prediction coverage is poor.
2. `study.run_study` stores placeholder `NULL` `t_stat` values even though it computes summary statistics, so DB-side analytics are incomplete.
3. Canonical taxonomy (`taxonomy.EVENT_TYPES`) is unused; `normalize_event` accepts arbitrary values and `normalize_scope` silently drops unknown scopes (27/288 world events have NULL scope).
4. politician pipeline anomalies are collapsed to a single coarse `event_type="Politician Trade"`, discarding anomaly type from predictive granularity.
5. Only one smoke test covers parser construction; statistical and ETL logic is untested.
6. Paths to source data are hardcoded to `D:\AI\StockPrediction\data\...`, making the repo non-portable.

**General recommendation:** Keep architecture and incrementally harden it: canonicalize event taxonomy at ingest, complete DB persistence, add focused tests and validation, and document/port configuration. Do not redesign the pipeline; the current shape is appropriate for scope, but it needs correctness and reproducibility improvements before heavier use.

## B. Repository Overview

- **Language/framework:** Python 3.15 (venv), pandas, numpy, scipy, duckdb, yfinance, pydantic, pytest/ruff.
- **Structure:**
  - `src/eventstudy/*.py`: package modules.
  - `src/eventstudy/__main__.py`: argparse CLI.
  - `tests/test_smoke.py`: parser smoke test.
  - `data/*.duckdb`: generated (gitignored).
  - `reports/*`: generated outputs (gitignored).
  - `seeds/legacy_macro_events.csv`: empty placeholder.
  - External inputs: `D:\AI\StockPrediction\data\events.json`, `.../politician_anomalies.json` (machine-local, not in repo).
- **Entry points:** `run_eventstudy.bat/ps1`, `run_politician_study.py/ps1`, console script `eventstudy`.
- **Execution flow:** init-db creates schema → fetch-prices downloads `^GSPC` → migrate-legacy inserts external events → run-study computes CARs (1/3/5/10-day) and one-sample t-tests vs 0 → pattern-detect aggregates mean CAR by `(event_type, horizon)` → predict reads `reports/patterns.json`.
- **Dependencies:** broad/unpinned in `pyproject.toml`; lockfile is UTF-16 and appears repository-local tooling output, not a reproducible CI artifact.

## C. Findings

### F-001 — Event types are not canonicalized (HIGH)
- **File:** `src/eventstudy/events.py:46-57` (`normalize_event`), `src/eventstudy/taxonomy.py:4-12` (`EVENT_TYPES` unused)
- **Evidence:** DB query shows 50+ variants (`Geopolitical shock` vs `Geopolitical shocks`, `Corporate bankruptcy` vs `Corporate Bankruptcy`, casing differences, free-form labels such as `commodity_policy`, `Stock`).
- **Explanation:** `normalize_event` passes through raw `event_type`/`type` without using the declared taxonomy. `predict_event` filters patterns on exact equality.
- **Impact:** Pattern aggregation and prediction fragmentation; predictions often return neutral due to no exact match.
- **Recommendation:** Add an explicit `normalize_event_type` mapping in `taxonomy.py` and apply at ingest/migration. Preserve raw original in `notes` or a new column if needed.

### F-002 — Incomplete persistence of study statistics (MEDIUM)
- **File:** `src/eventstudy/study.py:34-50`
- **Evidence:** Insert uses `INSERT INTO study_results VALUES (?,?,?,NULL,NULL)` while `summary = summarize(rows)` is computed and written to CSV.
- **Explanation:** `t_stat` and `p_value` are computed but not stored in DuckDB.
- **Impact:** DB consumers cannot audit significance; only latest CSV retains summary.
- **Recommendation:** Insert computed t/p values (join by horizon or store summary separately).

### F-003 — Scope normalization drops unknown values silently (MEDIUM)
- **File:** `src/eventstudy/taxonomy.py:17-23`, `src/eventstudy/events.py:31` (`normalize_scope`)
- **Evidence:** 27/288 world events have NULL `geographic_scope`.
- **Impact:** Silent data loss and untraceable missing business attribute.
- **Recommendation:** Either extend allowed scopes, keep raw with a `scope_raw` field, or log dropped values. Current behavior should be documented.

### F-004 — Daily returns table unused (LOW/INFORMATIONAL)
- **File:** `src/eventstudy/db.py:24-28`, `src/eventstudy/returns.py:6-14`
- **Evidence:** DB query showed `daily_returns` count 0 in both DBs; `compute_daily_returns` is runtime-only.
- **Impact:** Schema promises persisted returns but none exist; some expected SQL-based analytics cannot run.
- **Recommendation:** Either populate `daily_returns` during fetch or remove table.

### F-005 — Hardcoded external data paths (MEDIUM)
- **File:** `src/eventstudy/config.py:9,23`
- **Evidence:** `LEGACY_EVENTS_PATH = Path(r"D:\AI\StockPrediction\data\events.json")`, `POLITICIAN_ANOMALIES_PATH = Path(r"D:\AI\StockPrediction\data\politician_anomalies.json")`.
- **Impact:** Project cannot be cloned/run elsewhere; core pipeline fails without machine-specific data.
- **Recommendation:** Support environment overrides and document setup; bundle sanitized seeds where feasible.

### F-006 — Minimal test coverage (HIGH)
- **File:** `tests/test_smoke.py`
- **Evidence:** Only parser construction tested. No tests for `window_return`, `find_event_index`, `normalize_event`, `taxonomy`, stats.
- **Impact:** Statistical correctness cannot be verified; regressions likely undetected.
- **Recommendation:** Add unit tests for return windows, event alignment, taxonomy normalization, and stats.

### F-007 — Politician pipeline loses anomaly granularity (MEDIUM)
- **File:** `src/eventstudy/migrate_politician.py:36-44`
- **Evidence:** All rows inserted with `event_type="Politician Trade"`; anomaly type used only in description/notes.
- **Impact:** Pattern/prediction cannot distinguish anomaly types.
- **Recommendation:** Store anomaly type in `event_type` or an additional field.

### F-008 — Severity normalization discards falsy-zero semantics and errors (LOW)
- **File:** `src/eventstudy/events.py:23-24` (`severity_rating=raw.get(...) or raw.get(...)`), `src/eventstudy/taxonomy.py:25-35`
- **Evidence:** `raw.get("severity_rating") or raw.get("severity")` treats `0` as missing; `normalize_severity` rejects outside 1-10.
- **Impact:** Minor; if a severity 0 is intended (none), it is lost.
- **Recommendation:** Use explicit `None` checks instead of truthiness.

### F-009 — Monolithic config side effects (LOW)
- **File:** `src/eventstudy/config.py:27-31`
- **Evidence:** Module import creates `DATA_DIR`, `REPORTS_DIR`, `SEEDS_DIR`.
- **Impact:** Import has filesystem side effects; tests cannot easily isolate.
- **Recommendation:** Move directory creation into explicit setup function.

### F-010 — Prediction model is descriptive, not statistical (INFORMATIONAL)
- **File:** `src/eventstudy/predict.py:17-32`, `src/eventstudy/patterns.py:13-31`
- **Evidence:** `predict_event` returns historical mean CAR and direction from patterns; no significance, uncertainty, or horizon interpolation.
- **Impact:** Output may be overinterpreted as forecast.
- **Recommendation:** Clearly label as historical average; include n, significance, and confidence bounds.

## D. Architecture Assessment

**Works well:**
- Clear module split for pure-ish functions.
- Parameterized SQL; no obvious injection.
- Database init idempotent.
- Separate DBs for pipelines.

**Does not work well:**
- Taxonomy declared but not used, making code misleading.
- Event ingestion does not validate required fields (`event_id` can become `"None"` if missing).
- Report writing and DB writes are interleaved; failures can leave partial state.
- `warnings.filterwarnings("ignore")` in `prices.py` hides operational issues.
- PYTHON 3.15 is ahead of declared support and lockfile; compatibility risk.
- External data dependency makes reproducibility weak.

**Recommendation:** Incremental hardening, not redesign. Keep DuckDB and pipeline separation.

## E. Security Assessment

- No credentials/API keys found in repo.
- SQL is parameterized; no injection paths identified.
- CLI does not accept untrusted network input except ticker via code.
- Main risks are operational: external paths, lack of input validation, broad dependency versions, HTTPS/GPG etc not in scope.
- Lockfile is UTF-16, which can break dependency tooling.
- No authentication because this is a local tool; acceptable for scope.
- **No exploitable vulnerability identified** in current local-only design.

## F. Testing Assessment

- **Current:** 1 test, 0.04s, passes.
- **Ruff:** clean.
- **Missing:** unit/integration tests for ETL and stats; no tests for migration, prices, DB schema, pattern aggregation.
- **Danger:** passing test gives false confidence; as noted in skill guidance, a passing parser test does not prove functionality.

## G. Technical Debt

- Unused `daily_returns` table.
- Unused taxonomy enforcement.
- Hardcoded Windows paths.
- Inconsistent event labels.
- Placeholder t_stat persistence.
- Loose dependency specs.
- Mixed plural/singular event type variants.
- Research outputs checked/ignored but produced locally.
- UTF-16 lockfile.

## H. Prioritized Roadmap

### P0 — Critical
1. **Canonicalize event types at ingest** (F-001, F-007)
   - Why: Prediction and pattern aggregation depend on consistent keys.
   - Benefit: Reliable grouping/reporting.
   - Risk: Existing reports become non-comparable after relabeling.
   - Validation: Add regression test + re-run study.

2. **Complete test suite for statistical logic** (F-006)
   - Why: Core numerical claims currently unverified.
   - Benefit: Catch alignment/window errors.
   - Risk: Low.
   - Validation: pytest with edge cases.

### P1 — High
3. **Store computed t_stat/p_value** (F-002)
4. **Portabilize config paths** (F-005)
5. **Document/validate scope handling** (F-003)

### P2 — Important
6. **Populate or remove daily_returns** (F-004)
7. **Fix severity truthiness** (F-008)
8. **Annotate prediction outputs with uncertainty** (F-010)

### P3 — Optional
9. Move directory creation out of import (F-009)
10. Normalize lockfile encoding and dependency pins

## I. Final Verdict

- **Is the project fundamentally sound?** Yes, for a local research scaffold. Core flow works and code is readable.
- **Is it production-ready?** No. Minimal tests, non-portable data paths, uncanonicalized taxonomy, incomplete persisted statistics, and fragile statistical validation.
- **What should NOT be changed?** Keep the pipeline separation, DuckDB local store, and simple module layering; they fit the project scale.
- **What should be fixed first?** Event-type canonicalization and tests for return-window/statistical logic.
- **What should the next development phase accomplish?** Deterministic, tested, reproducible event-study computation with consistent labels and persisted significance statistics; then basic hardening of config/path portability.
