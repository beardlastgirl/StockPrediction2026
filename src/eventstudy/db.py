"""DuckDB schema and connection helpers."""
from __future__ import annotations

from pathlib import Path

import duckdb

from eventstudy.config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    event_id VARCHAR PRIMARY KEY,
    event_date DATE NOT NULL,
    event_type VARCHAR,
    event_description TEXT,
    geographic_scope VARCHAR,
    severity_rating INTEGER,
    sector_impact VARCHAR,
    notes TEXT
);
CREATE TABLE IF NOT EXISTS prices (
    ticker VARCHAR NOT NULL,
    price_date DATE NOT NULL,
    open DOUBLE,
    high DOUBLE,
    low DOUBLE,
    close DOUBLE,
    adj_close DOUBLE,
    volume DOUBLE,
    PRIMARY KEY (ticker, price_date)
);
CREATE TABLE IF NOT EXISTS daily_returns (
    ticker VARCHAR NOT NULL,
    return_date DATE NOT NULL,
    ret DOUBLE,
    PRIMARY KEY (ticker, return_date)
);
CREATE TABLE IF NOT EXISTS study_results (
    event_id VARCHAR,
    horizon INTEGER,
    car DOUBLE,
    t_stat DOUBLE,
    p_value DOUBLE
);
"""


def get_connection(db_path: Path = DB_PATH):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(db_path))


def init_db(db_path: Path = DB_PATH) -> None:
    con = get_connection(db_path)
    try:
        con.execute(SCHEMA)
    finally:
        con.close()
