"""Migrate politician-trade anomaly findings into a separate DuckDB."""
from __future__ import annotations

import json
from datetime import datetime

from eventstudy.config import POLITICIAN_ANOMALIES_PATH
from eventstudy.db import get_connection, init_db
from eventstudy.events import Event, insert_events


def _first_date(finding) -> str:
    dates = []
    for t in finding.get("trades", []):
        if t.get("transaction_date"):
            dates.append(t["transaction_date"])
    if dates:
        return min(dates)[:10]
    return datetime.now().date().isoformat()


def load_events(path=None):
    path = path or POLITICIAN_ANOMALIES_PATH
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    events = []
    for i, fnd in enumerate(data.get("findings", [])):
        d = _first_date(fnd)
        events.append(Event(
            event_id=f"POL-{fnd.get('type')}-{fnd.get('ticker')}-{i}",
            event_date=d,
            event_type="Politician Trade",
            event_description=f"{fnd.get('type')} on {fnd.get('ticker')} by {fnd.get('trade_count',0)} trades",
            geographic_scope="national",
            severity_rating=5,
            sector_impact=fnd.get("ticker"),
            notes=fnd.get("type"),
        ))
    return events


def migrate(db_path=None, anomalies_path=None) -> int:
    from eventstudy.config import POLITICIAN_DB_PATH

    target = db_path or POLITICIAN_DB_PATH
    init_db(target)
    events = load_events(anomalies_path)
    con = get_connection(target)
    try:
        return insert_events(con, events)
    finally:
        con.close()
