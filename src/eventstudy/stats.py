"""Event-study statistics."""
from __future__ import annotations

import numpy as np
from scipy import stats as sp_stats

from eventstudy.config import HORIZONS
from eventstudy.returns import window_return


def event_cars(price_df, events, horizons=HORIZONS) -> list[dict]:
    out = []
    for ev in events:
        ed = ev["event_date"] if isinstance(ev, dict) else ev.event_date
        eid = ev["event_id"] if isinstance(ev, dict) else ev.event_id
        for h in horizons:
            car = window_return(price_df, ed, h)
            out.append({"event_id": eid, "horizon": h, "car": car})
    return out


def cross_sectional_test(cars: list[float]) -> tuple[float, float]:
    arr = np.array([x for x in cars if x is not None], dtype=float)
    if len(arr) < 2:
        return float("nan"), float("nan")
    t, p = sp_stats.ttest_1samp(arr, 0.0)
    return float(t), float(p)


def summarize(car_rows: list[dict]) -> list[dict]:
    by_h = {}
    for r in car_rows:
        by_h.setdefault(r["horizon"], []).append(r["car"])
    result = []
    for h in sorted(by_h):
        t, p = cross_sectional_test(by_h[h])
        vals = [x for x in by_h[h] if x is not None]
        result.append({
            "horizon": h,
            "n": len(vals),
            "mean_car": float(np.mean(vals)) if vals else float("nan"),
            "t_stat": t,
            "p_value": p,
        })
    return result
