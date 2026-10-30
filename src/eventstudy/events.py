"""Event loading and normalization."""
from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from eventstudy.taxonomy import normalize_scope, normalize_severity


@dataclass
class Event:
    event_id: str
    event_date: str
    event_type: str | None = None
    event_description: str | None = None
    geographic_scope: str | None = None
    severity_rating: int | None = None
    sector_impact: str | None = None
    notes: str | None = None

    def to_row(self) -> tuple:
        return (
            self.event_id,
            self.event_date,
            self.event_type,
            self.event_description,
            normalize_scope(self.geographic_scope),
            normalize_severity(self.severity_rating),
            self.sector_impact,
            self.notes,
        )


def parse_date(value) -> str:
    if isinstance(value, (datetime, date)):
        return value.isoformat()[:10]
    return str(value)[:10]


def normalize_event(raw: dict) -> Event:
    return Event(
        event_id=str(raw.get("event_id") or raw.get("id")),
        event_date=parse_date(raw.get("date") or raw.get("event_date")),
        event_type=raw.get("event_type") or raw.get("type"),
        event_description=raw.get("event_description") or raw.get("description"),
        geographic_scope=raw.get("geographic_scope") or raw.get("scope"),
        severity_rating=raw.get("severity_rating") or raw.get("severity"),
        sector_impact=raw.get("sector_impact"),
        notes=raw.get("notes"),
    )


def load_legacy_events(path: Path | str) -> list[Event]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        data = data.get("events", [])
    return [normalize_event(r) for r in data]


def insert_events(con, events: Iterable[Event]) -> int:
    rows = [e.to_row() for e in events]
    if not rows:
        return 0
    con.executemany(
        "INSERT OR REPLACE INTO events VALUES (?,?,?,?,?,?,?,?)",
        rows,
    )
    return len(rows)
