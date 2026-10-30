"""Pattern detection from study results."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from eventstudy.config import REPORTS_DIR


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
        out.append({
            "event_type": et,
            "horizon": h,
            "n": len(vals),
            "mean_car": mean,
            "direction": "down" if mean < 0 else "up",
        })
    out.sort(key=lambda x: (x["event_type"], x["horizon"]))
    return out


def save_patterns(patterns, path=None) -> Path:
    path = path or (REPORTS_DIR / "patterns.json")
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(patterns, f, indent=2)
    return path
