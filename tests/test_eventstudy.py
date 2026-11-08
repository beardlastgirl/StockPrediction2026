import datetime as dt

import pandas as pd
import pytest

from eventstudy import taxonomy
from eventstudy.events import normalize_event
from eventstudy.returns import find_event_index, window_return
from eventstudy.stats import cross_sectional_test, summarize


def prices():
    dates = [dt.date(2020, 1, 1) + dt.timedelta(days=i) for i in range(10)]
    close = [100 + i for i in range(10)]
    return pd.DataFrame({"price_date": dates, "close": close, "adj_close": close})


def test_find_event_index():
    df = prices()
    assert find_event_index(df["price_date"], "2020-01-03") == 2
    assert find_event_index(df["price_date"], "2019-12-01") == 0


def test_window_return():
    df = prices()
    cars = window_return(df, "2020-01-02", 1)
    assert cars == pytest.approx(0.01, rel=1e-9)


def test_taxonomy_normalize():
    assert taxonomy.normalize_event_type("Geopolitical shocks") == "Geopolitical shock"
    assert taxonomy.normalize_event_type("monetary_policy") == "Monetary policy"
    assert taxonomy.normalize_event_type("Corporate Bankruptcy") == "Corporate bankruptcy"
    assert taxonomy.normalize_severity(0) is None


def test_normalize_event_id_requires():
    with pytest.raises(ValueError):
        normalize_event({"event_date": "2020-01-01"})


def test_normalize_event():
    ev = normalize_event(
        {"event_id": "E1", "date": "2020-01-01", "type": "Geopolitical shocks", "severity": 0, "scope": "global"}
    )
    assert ev.event_id == "E1"
    assert ev.event_type == "Geopolitical shock"
    assert ev.severity_rating == 0
    assert ev.geographic_scope == "global"


def test_cross_sectional_and_summary():
    rows = [
        {"event_id": "a", "horizon": 1, "car": 0.01},
        {"event_id": "b", "horizon": 1, "car": -0.02},
    ]
    out = summarize(rows)
    assert out[0]["horizon"] == 1
    assert out[0]["n"] == 2
    t, _p = cross_sectional_test([0.01, -0.02])
    assert t == out[0]["t_stat"]