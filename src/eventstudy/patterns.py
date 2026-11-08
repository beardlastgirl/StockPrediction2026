"""Pattern detection from study results."""
from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

from eventstudy.config import REPORTS_DIR


def _finite(value) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _safe_std(vals: list[float]) -> float:
    if len(vals) < 2:
        return 0.0
    mean = sum(vals) / len(vals)
    return (sum((x - mean) ** 2 for x in vals) / (len(vals) - 1)) ** 0.5


def compute_patterns(con) -> list[dict]:
    rows = con.execute(
        """SELECT e.event_type, s.horizon, s.car
           FROM study_results s JOIN events e ON e.event_id=s.event_id
           WHERE s.car IS NOT NULL"""
    ).fetchall()
    groups = defaultdict(list)
    for et, h, car in rows:
        groups[(et, h)].append(float(car))
    out = []
    for (et, h), vals in groups.items():
        mean = sum(vals) / len(vals) if vals else 0.0
        std = _safe_std(vals)
        # Approximate significance versus zero with a one-sample t-test.
        import scipy.stats as st
        t, p = st.ttest_1samp(vals, 0.0) if len(vals) >= 2 else (float("nan"), float("nan"))
        out.append({
            "event_type": et,
            "horizon": h,
            "n": len(vals),
            "mean_car": mean,
            "std_car": std,
            "t_stat": float(t) if _finite(t) else None,
            "p_value": float(p) if _finite(p) else None,
            "direction": "down" if mean < 0 else "up",
        })
    out.sort(key=lambda x: (x["event_type"], x["horizon"]))
    return out


def save_patterns(patterns, path=None) -> Path:
    path = path or (REPORTS_DIR / "patterns.json")
    from eventstudy.config import ensure_dirs

    ensure_dirs()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(patterns, f, indent=2)
    return path
