"""Configuration and paths for the event study."""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = REPO_ROOT / "data"
DB_PATH = DATA_DIR / "eventstudy.duckdb"
REPORTS_DIR = REPO_ROOT / "reports"
SEEDS_DIR = REPO_ROOT / "seeds"

LEGACY_EVENTS_PATH = Path(r"D:\AI\StockPrediction\data\events.json")

BENCHMARK_TICKER = "^GSPC"
HORIZONS = (1, 3, 5, 10)
EST_WINDOW = 250
MIN_EST_OBS = 120
PERM_DRAWS = 10_000
RNG_SEED = 20261025

DATA_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
SEEDS_DIR.mkdir(parents=True, exist_ok=True)
