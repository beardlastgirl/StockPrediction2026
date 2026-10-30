"""Migrate legacy JSON events into DuckDB."""
from __future__ import annotations

from pathlib import Path

from eventstudy.config import LEGACY_EVENTS_PATH
from eventstudy.db import get_connection
from eventstudy.events import insert_events, load_legacy_events


def migrate(legacy_path: Path | str = LEGACY_EVENTS_PATH, db_path=None) -> int:
    events = load_legacy_events(legacy_path)
    con = get_connection(db_path) if db_path else get_connection()
    try:
        return insert_events(con, events)
    finally:
        con.close()
