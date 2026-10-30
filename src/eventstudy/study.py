"""Study orchestration."""
from __future__ import annotations

import csv

import pandas as pd

from eventstudy.config import BENCHMARK_TICKER, DB_PATH, REPORTS_DIR
from eventstudy.db import get_connection
from eventstudy.stats import event_cars, summarize


def load_events(con) -> list[dict]:
    rows = con.execute(
        "SELECT event_id, event_date, event_type, geographic_scope, severity_rating FROM events"
    ).fetchall()
    cols = ["event_id", "event_date", "event_type", "geographic_scope", "severity_rating"]
    return [dict(zip(cols, r)) for r in rows]


def load_prices(con, ticker=BENCHMARK_TICKER) -> pd.DataFrame:

    df = con.execute(
        "SELECT price_date, close, adj_close FROM prices WHERE ticker=? ORDER BY price_date",
        [ticker],
    ).fetchdf()
    df = df.rename(columns={"price_date": "price_date"})
    if "price_date" in df.columns:
        df["price_date"] = pd.to_datetime(df["price_date"]).dt.date
    return df


def run_study(db_path=DB_PATH, ticker=BENCHMARK_TICKER, report_path=None) -> list[dict]:
    con = get_connection(db_path)
    try:
        events = load_events(con)
        prices = load_prices(con, ticker)
        rows = event_cars(prices, events)
        summary = summarize(rows)
        # store
        con.execute("DELETE FROM study_results")
        for r in rows:
            if r["car"] is None:
                continue
            con.execute(
                "INSERT INTO study_results VALUES (?,?,?,NULL,NULL)",
                [r["event_id"], r["horizon"], float(r["car"])],
            )
        report_path = report_path or (REPORTS_DIR / "study_results.csv")
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        with open(report_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["horizon", "n", "mean_car", "t_stat", "p_value"])
            w.writeheader()
            w.writerows(summary)
        return summary
    finally:
        con.close()
