"""Price fetching and storage."""
from __future__ import annotations

import pandas as pd
import yfinance as yf

from eventstudy.config import BENCHMARK_TICKER, DB_PATH
from eventstudy.db import get_connection
from eventstudy.returns import compute_daily_returns


def fetch_prices(ticker: str, start: str, end: str) -> pd.DataFrame:
    df = yf.download(ticker, start=start, end=end, auto_adjust=False, progress=False)
    if df is None or df.empty:
        return pd.DataFrame()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] for c in df.columns]
    df = df.reset_index()
    df = df.rename(columns={"Date": "price_date"})
    if "Adj Close" in df.columns:
        df = df.rename(columns={"Adj Close": "adj_close"})
    for c in ("Open", "High", "Low", "Close", "Volume"):
        if c in df.columns:
            df = df.rename(columns={c: c.lower()})
    keep = ["price_date", "open", "high", "low", "close", "adj_close", "volume"]
    df = df[[c for c in keep if c in df.columns]]
    df["ticker"] = ticker
    df["price_date"] = pd.to_datetime(df["price_date"]).dt.date
    return df


def store_prices(con, ticker: str, df: pd.DataFrame) -> int:
    if df.empty:
        return 0
    rows = [
        (
            ticker,
            r["price_date"],
            float(r.get("open")) if pd.notna(r.get("open")) else None,
            float(r.get("high")) if pd.notna(r.get("high")) else None,
            float(r.get("low")) if pd.notna(r.get("low")) else None,
            float(r.get("close")) if pd.notna(r.get("close")) else None,
            float(r.get("adj_close")) if pd.notna(r.get("adj_close")) else None,
            float(r.get("volume")) if pd.notna(r.get("volume")) else None,
        )
        for _, r in df.iterrows()
    ]
    con.executemany(
        "INSERT OR REPLACE INTO prices VALUES (?,?,?,?,?,?,?,?)",
        rows,
    )
    return len(rows)


def store_daily_returns(con, ticker: str, df: pd.DataFrame) -> int:
    if df.empty:
        return 0
    daily = compute_daily_returns(df)
    rows = []
    for _, r in daily.iterrows():
        ret = r.get("ret")
        if pd.isna(ret):
            continue
        rows.append((ticker, r["price_date"], float(ret)))
    if not rows:
        return 0
    con.executemany(
        "INSERT OR REPLACE INTO daily_returns VALUES (?,?,?)",
        rows,
    )
    return len(rows)


def fetch_and_store(ticker=BENCHMARK_TICKER, start="2000-01-01", end=None, db_path=DB_PATH) -> int:
    import datetime as dt

    from eventstudy.config import ensure_dirs

    ensure_dirs()
    end = end or dt.date.today().isoformat()
    df = fetch_prices(ticker, start, end)
    con = get_connection(db_path)
    try:
        n = store_prices(con, ticker, df)
        store_daily_returns(con, ticker, df)
        return n
    finally:
        con.close()

