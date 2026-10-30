import warnings; warnings.filterwarnings("ignore")
from eventstudy.db import init_db, get_connection
from eventstudy.migrate_politician import migrate
from eventstudy.prices import fetch_and_store
from eventstudy.study import run_study
from eventstudy.config import REPORTS_DIR, POLITICIAN_DB_PATH, BENCHMARK_TICKER
init_db(POLITICIAN_DB_PATH)
print("migrated:", migrate())
try:
    print("prices:", fetch_and_store(BENCHMARK_TICKER, db_path=POLITICIAN_DB_PATH))
except Exception as e:
    print("fetch skipped/failed:", e)
summary = run_study(db_path=POLITICIAN_DB_PATH, report_path=REPORTS_DIR / "politician_study_results.csv")
for row in summary:
    print(row)
