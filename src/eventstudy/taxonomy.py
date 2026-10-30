"""Event taxonomy and normalization helpers."""
from __future__ import annotations

EVENT_TYPES = [
    "Geopolitical shock",
    "Corporate bankruptcy",
    "Natural disaster",
    "Monetary policy",
    "Earnings",
    "Regulatory",
    "Trade policy",
]

GEO_SCOPES = ("global", "regional", "national", "local")


def normalize_scope(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip().lower()
    return value if value in GEO_SCOPES else None


def normalize_severity(value) -> int | None:
    if value is None:
        return None
    try:
        v = int(value)
    except (TypeError, ValueError):
        return None
    return v if 1 <= v <= 10 else None
