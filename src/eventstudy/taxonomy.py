"""Event taxonomy and normalization helpers."""
from __future__ import annotations

import re

EVENT_TYPES = [
    "Geopolitical shock",
    "Corporate bankruptcy",
    "Natural disaster",
    "Monetary policy",
    "Earnings",
    "Regulatory",
    "Trade policy",
    "Politician trade",
]

GEO_SCOPES = ("global", "regional", "national", "local")

_ALIASES = {
    "geopolitical shocks": "Geopolitical shock",
    "geopolitical/war": "Geopolitical shock",
    "corporate bankruptcy": "Corporate bankruptcy",
    "corporate bankrupcy": "Corporate bankruptcy",
    "corporate financial distress": "Corporate bankruptcy",
    "natural disasters": "Natural disaster",
    "natural disaster": "Natural disaster",
    "monetary policy": "Monetary policy",
    "monetary_policy": "Monetary policy",
    "regulatory change": "Regulatory",
    "regulatory changes": "Regulatory",
    "major earnings surprise": "Earnings",
    "stock market crash": "Geopolitical shock",
}


def _clean(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip())


def normalize_event_type(value) -> str | None:
    if value is None:
        return None
    raw = _clean(str(value))
    if not raw:
        return None
    key = raw.lower().replace("-", " ").replace("_", " ")
    key = re.sub(r"\s+", " ", key).strip()
    if key in _ALIASES:
        return _ALIASES[key]
    for candidate in EVENT_TYPES:
        if candidate.lower() == key:
            return candidate
    # Keyword-based canonicalization for free-form labels.
    if any(k in key for k in ("bankruptcy", "financial distress", "default")):
        return "Corporate bankruptcy"
    if any(k in key for k in ("disaster",)):
        return "Natural disaster"
    if any(k in key for k in ("monetary", "interest rate", "fed ")):
        return "Monetary policy"
    if any(k in key for k in ("earnings", "profit", "revenue")):
        return "Earnings"
    if any(k in key for k in ("regulat", "compliance", "antitrust")):
        return "Regulatory"
    if any(k in key for k in ("trade", "tariff", "sanction", "blockade")):
        return "Trade policy"
    if any(k in key for k in ("geopol", "war", "military", "conflict", "crisis", "civil", "blockade")):
        return "Geopolitical shock"
    if "politician" in key:
        return "Politician trade"
    return raw.title()


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


def normalize_event_id(raw: dict) -> str:
    value = raw.get("event_id", raw.get("id"))
    if value is None or str(value).strip() == "" or str(value).strip().lower() == "none":
        raise ValueError("event_id is required")
    return str(value).strip()
