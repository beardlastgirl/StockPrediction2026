"""Configuration and paths for the event study."""
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = REPO_ROOT / "data"
DB_PATH = DATA_DIR / "eventstudy.duckdb"
REPORTS_DIR = REPO_ROOT / "reports"
SEEDS_DIR = REPO_ROOT / "seeds"

DEFAULT_LEGACY_EVENTS_PATH = Path(r"D:\AI\StockPrediction\data\events.json")
LEGACY_EVENTS_PATH = Path(os.getenv("EVENTSTUDY_LEGACY_EVENTS", str(DEFAULT_LEGACY_EVENTS_PATH)))

DEFAULT_POLITICIAN_ANOMALIES_PATH = Path(r"D:\AI\StockPrediction\data\politician_anomalies.json")
POLITICIAN_ANOMALIES_PATH = Path(os.getenv("EVENTSTUDY_POLITICIAN_ANOMALIES", str(DEFAULT_POLITICIAN_ANOMALIES_PATH)))

BENCHMARK_TICKER = "^GSPC"
HORIZONS = (1, 3, 5, 10)
RNG_SEED = 20261025

POLITICIAN_DB_PATH = DATA_DIR / "politician_eventstudy.duckdb"


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    SEEDS_DIR.mkdir(parents=True, exist_ok=True)
