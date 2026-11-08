"""Study orchestration."""
from __future__ import annotations

import csv
import math

import pandas as pd

from eventstudy.config import BENCHMARK_TICKER, DB_PATH, REPORTS_DIR
from eventstudy.db import get_connection
from eventstudy.stats import event_cars, summarize


def _is_finite(value) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


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
        summary_by_horizon = {r["horizon"]: r for r in summary}
        # store
        con.execute("DELETE FROM study_results")
        for r in rows:
            if r["car"] is None:
                continue
            agg = summary_by_horizon.get(r["horizon"], {})
            t_stat = agg.get("t_stat")
            p_value = agg.get("p_value")
            if t_stat is not None and not _is_finite(t_stat):
                t_stat = None
            if p_value is not None and not _is_finite(p_value):
                p_value = None
            con.execute(
                "INSERT INTO study_results VALUES (?,?,?,?,?)",
                [r["event_id"], r["horizon"], float(r["car"]), t_stat, p_value],
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
