"""Return computation helpers."""
from __future__ import annotations

import pandas as pd


def compute_daily_returns(prices: pd.DataFrame) -> pd.DataFrame:
    df = prices.copy()
    price_col = "adj_close" if "adj_close" in df.columns else "close"
    df = df.sort_values("price_date").reset_index(drop=True)
    df["ret"] = df[price_col].pct_change()
    return df


def find_event_index(price_dates, event_date) -> int | None:
    import datetime as dt

    if isinstance(event_date, str):
        event_date = dt.date.fromisoformat(event_date[:10])
    if hasattr(event_date, "date"):
        event_date = event_date.date()
    idx = None
    for i, d in enumerate(price_dates):
        dd = d.date() if hasattr(d, "date") else d
        if dd >= event_date:
            idx = i
            break
    return idx


def window_return(price_df: pd.DataFrame, event_date, horizon: int) -> float | None:
    df = compute_daily_returns(price_df)
    dates = list(df["price_date"])
    i = find_event_index(dates, event_date)
    if i is None or i + horizon > len(df):
        return None
    # CAR over [0..horizon-1] inclusive using returns starting event day
    cum = 1.0
    for r in df["ret"].iloc[i : i + horizon]:
        if pd.isna(r):
            return None
        cum *= 1.0 + float(r)
    return cum - 1.0
