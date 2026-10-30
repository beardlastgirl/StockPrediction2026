"""Simple pattern-based prediction."""
from __future__ import annotations

import json

from eventstudy.config import REPORTS_DIR


def load_patterns(path=None):
    path = path or (REPORTS_DIR / "patterns.json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def predict_event(event_type: str, horizon: int = 5, patterns=None) -> dict:
    patterns = patterns if patterns is not None else load_patterns()
    match = [p for p in patterns if p["event_type"] == event_type and p["horizon"] == horizon]
    if not match:
        return {"event_type": event_type, "horizon": horizon, "direction": "neutral", "expected_car": 0.0, "n": 0}
    p = match[0]
    return {
        "event_type": event_type,
        "horizon": horizon,
        "direction": p["direction"],
        "expected_car": p["mean_car"],
        "n": p["n"],
    }
