"""Unit tests for the survival DV pipeline (no network)."""

from datetime import date

import pandas as pd
import pytest

from toolkit.survival_dv.classify import classify_page, fetch_page
from toolkit.survival_dv.crunchbase import (
    _classify_exit,
    _match_type,
    _precision_from_date,
    extract_domain,
    flag_website,
)
from toolkit.survival_dv.config import ANALYSIS_END_DATE, CB_DUMP_DATE
from toolkit.survival_dv.derive import build_panel, derive_duration
from toolkit.survival_dv.event_dates import lookup, parse_year
from toolkit.survival_dv.funding import _build_time_to_funding
from toolkit.survival_dv.io import normalize_name
from toolkit.survival_dv.wayback import find_death_transition


def test_parse_year():
    assert parse_year("Disrupt SF 2013") == 2013
    assert parse_year("TechCrunch50 -2008") == 2008
    assert parse_year("TechCrunch 40") is None


def test_event_dates_lookup():
    assert lookup("TechCrunch 40") == date(2007, 9, 1)
    assert lookup("Disrupt SF 2013") == date(2013, 9, 1)
    assert lookup("Disrupt NY 2013") == date(2013, 5, 1)
    assert lookup("Disrupt SF 2019") == date(2019, 10, 1)
    assert lookup("1st and Future") == date(2016, 2, 1)
    assert lookup("Startup Battlefield Latin America") == date(2018, 11, 1)


def test_normalize_name():
    assert normalize_name("3DLT") == "3dlt"
    assert normalize_name("Agrilyst (Artemis)") == "agrilystartemis"
    assert normalize_name("RedBeacon (Pro Referral)") == "redbeaconproreferral"


def test_extract_domain():
    assert extract_domain("https://www.example.com/path") == "example.com"
    assert extract_domain("http://example.com") == "example.com"
    assert extract_domain("www.example.com") == "example.com"
    assert extract_domain(None) is None


def test_flag_website_missing():
    row = pd.Series({"website": None, "status": "closed"})
    flags = flag_website(row)
    assert flags["website_valid"] is False
    assert flags["website_flag"] == "missing"


def test_flag_website_aggregator():
    row = pd.Series({"website": "https://crunchbase.com/organization/foo", "status": "closed"})
    flags = flag_website(row)
    assert flags["website_valid"] is False
    assert "crunchbase" in flags["website_flag"]


def test_flag_website_ok():
    row = pd.Series({"website": "https://example.com", "status": "closed"})
    flags = flag_website(row)
    assert flags["website_valid"] is True


def test_precision_from_date():
    assert _precision_from_date("2020-01-01") == "year"
    assert _precision_from_date("2020-05-18") == "day"
    assert _precision_from_date(pd.NaT) is None


def test_match_type():
    row = pd.Series({"cb_domain_match_count": 0})
    assert _match_type(row) == "none"
    row = pd.Series({"cb_domain_match_count": 1})
    assert _match_type(row) == "domain"
    row = pd.Series({"cb_domain_match_count": 3})
    assert _match_type(row) == "domain_multiple"


def test_classify_exit_failure_crunchbase():
    row = pd.Series({
        "status": "closed",
        "cb_closed_on": pd.Timestamp("2020-05-15"),
        "acquired_on": pd.NaT,
    })
    out = _classify_exit(row)
    assert out["exit_type"] == "failure"
    assert out["death_source"] == "crunchbase"
    assert out["exit_date_precision"] == "day"


def test_classify_exit_failure_year_stamp():
    row = pd.Series({
        "status": "closed",
        "cb_closed_on": pd.Timestamp("2020-01-01"),
        "acquired_on": pd.NaT,
    })
    out = _classify_exit(row)
    assert out["exit_type"] == "failure"
    assert out["death_source"] == "crunchbase"
    assert out["exit_date_precision"] == "year"


def test_classify_exit_acquired():
    row = pd.Series({
        "status": "acquired",
        "acquired_on": pd.Timestamp("2019-08-14"),
        "acquisition_type": "acquisition",
    })
    out = _classify_exit(row)
    assert out["exit_type"] == "acquired"
    assert out["acq_date_source"] == "cb_domain"
    assert out["exit_date_precision"] == "day"


def test_classify_exit_acquihire():
    row = pd.Series({
        "status": "acquired",
        "acquired_on": pd.Timestamp("2021-02-11"),
        "acquisition_type": "acquihire",
    })
    out = _classify_exit(row)
    assert out["acquihire"] == 1


def test_classify_exit_censored():
    row = pd.Series({"status": "open"})
    out = _classify_exit(row)
    assert out["exit_type"] == "censored"


def test_classify_page_alive():
    html = "<html><body><h1>Welcome to Example</h1><p>We are a startup.</p></body></html>"
    out = classify_page("https://example.com", html, "https://example.com", 200)
    assert out["alive"] is True
    assert out["reason"] == "content"


def test_classify_page_parking():
    html = "<html><body>This domain is for sale. Buy this domain now.</body></html>"
    out = classify_page("https://example.com", html, "https://example.com", 200)
    assert out["dead"] is True
    assert "parking" in out["reason"]


def test_classify_page_403():
    out = classify_page("https://example.com", "", "https://example.com", 403)
    assert out["inspect"] is True


def test_derive_duration_failure():
    df = pd.DataFrame({
        "name": ["A"],
        "status": ["closed"],
        "exit_type": ["failure"],
        "exit_date": [pd.Timestamp("2020-05-15")],
        "exit_date_precision": ["day"],
        "death_source": ["crunchbase"],
        "origin_date": [pd.Timestamp("2015-09-01")],
        "cb_founded_on": [pd.Timestamp("2014-01-01")],
    })
    out = derive_duration(df, analysis_end=pd.Timestamp("2024-03-31"))
    assert out["failed"].iloc[0] == 1
    assert out["time_years"].iloc[0] > 4
    assert out["age_at_pitch_years"].iloc[0] > 1


def test_build_panel_failure():
    df = pd.DataFrame({
        "name": ["A"],
        "event": ["Disrupt SF 2015"],
        "exit_type": ["failure"],
        "exit_date": [pd.Timestamp("2017-03-15")],
        "origin_date": [pd.Timestamp("2015-09-01")],
    })
    panel = build_panel(df, analysis_end=pd.Timestamp("2024-03-31"))
    # 2015-09 to 2017-03 is ~1.5 years -> year_index 0, 1
    assert len(panel) >= 2
    assert panel["failed"].sum() == 1
    assert panel["at_risk"].sum() >= 2


def test_build_panel_acquired_censored():
    df = pd.DataFrame({
        "name": ["B"],
        "event": ["Disrupt SF 2015"],
        "exit_type": ["acquired"],
        "exit_date": [pd.Timestamp("2017-03-15")],
        "origin_date": [pd.Timestamp("2015-09-01")],
    })
    panel = build_panel(df, analysis_end=pd.Timestamp("2024-03-31"))
    # Should leave risk set at year 2
    assert len(panel) <= 2
    assert panel["failed"].sum() == 0


def _wayback_failure_row(last_alive, first_dead, origin="2015-09-01"):
    return pd.DataFrame({
        "name": ["A"],
        "exit_type": ["failure"],
        "exit_date": [pd.Timestamp(f"{first_dead}-12-31") if first_dead else pd.NaT],
        "exit_date_precision": ["year" if first_dead else None],
        "death_source": ["wayback" if first_dead else None],
        "origin_date": [pd.Timestamp(origin)],
        "cb_founded_on": [pd.NaT],
        "last_alive_year_wb": [last_alive],
        "first_dead_year_wb": [first_dead],
    })


def test_wayback_death_date_never_precedes_pitch():
    """A late-year pitch must not end up with a death date before the pitch."""
    df = _wayback_failure_row(None, 2015, origin="2015-11-01")
    out = derive_duration(df, analysis_end=pd.Timestamp("2024-03-31"))
    assert out["exit_date"].iloc[0] >= out["origin_date"].iloc[0]
    assert out["date_conflict"].iloc[0] == False
    assert out["time_lower_years"].iloc[0] >= 0


def test_year_precision_failure_is_interval_censored():
    """A year-precision death must not be reported as an exact date."""
    df = _wayback_failure_row(2017, 2019)
    out = derive_duration(df, analysis_end=pd.Timestamp("2024-03-31"))
    assert out["interval_censored"].iloc[0] == 1
    width = out["time_upper_years"].iloc[0] - out["time_lower_years"].iloc[0]
    assert width > 1, f"expected a multi-year bound, got {width}"


def test_unknown_last_alive_bounds_back_to_pitch():
    """With no confirmed live snapshot, the death could have happened any time."""
    df = _wayback_failure_row(None, 2019)
    out = derive_duration(df, analysis_end=pd.Timestamp("2024-03-31"))
    assert out["time_lower_years"].iloc[0] == 0
    assert out["time_upper_years"].iloc[0] > 4


def test_undated_failure_is_bounded_not_dropped():
    """Known failures with unknown dates get bounds instead of being deleted."""
    df = _wayback_failure_row(None, None)
    out = derive_duration(df, analysis_end=pd.Timestamp("2024-03-31"))
    assert out["undated_exit"].iloc[0] == 1
    assert out["failed"].iloc[0] == 1
    assert pd.notna(out["time_upper_years"].iloc[0])
    assert out["time_upper_years"].iloc[0] > out["time_lower_years"].iloc[0]


def test_derive_duration_preserves_wayback_bounds():
    """derive_duration runs twice, so it must not wipe the scan's interval bounds."""
    df = _wayback_failure_row(2017, 2019)
    df["last_alive_date"] = [pd.Timestamp("2017-12-31")]
    df["first_dead_date"] = [pd.Timestamp("2019-12-31")]
    out = derive_duration(df, analysis_end=pd.Timestamp("2024-03-31"))
    assert out["last_alive_date"].iloc[0] == pd.Timestamp("2017-12-31")
    assert out["first_dead_date"].iloc[0] == pd.Timestamp("2019-12-31")


def _snap(year, alive=False, dead=False):
    return {"year": year, "alive": alive, "dead": dead, "inspect": not (alive or dead)}


def test_death_transition_ignores_dead_reading_before_later_life():
    """A dead reading followed by a live reading is a false positive."""
    out = find_death_transition([
        _snap(2011, dead=True),
        _snap(2014, alive=True),
        _snap(2016, dead=True),
    ])
    assert out["last_alive_year"] == 2014
    assert out["first_dead_year"] == 2016
    assert out["revived"] is True


def test_death_transition_no_death_after_last_life():
    """If the site is alive at the end of the window there is no death year."""
    out = find_death_transition([
        _snap(2011, dead=True),
        _snap(2016, alive=True),
    ])
    assert out["last_alive_year"] == 2016
    assert out["first_dead_year"] is None


def test_death_transition_clean_sequence():
    out = find_death_transition([
        _snap(2011, alive=True),
        _snap(2013, alive=True),
        _snap(2015, dead=True),
        _snap(2016, dead=True),
    ])
    assert out["last_alive_year"] == 2013
    assert out["first_dead_year"] == 2015
    assert out["revived"] is False


def test_death_transition_never_confirmed_alive():
    out = find_death_transition([_snap(2015, dead=True), _snap(2018, dead=True)])
    assert out["last_alive_year"] is None
    assert out["first_dead_year"] == 2015


def test_death_transition_all_unknown():
    out = find_death_transition([_snap(2015), _snap(2016)])
    assert out["last_alive_year"] is None
    assert out["first_dead_year"] is None


def test_time_to_funding_is_a_duration_not_a_date():
    """The column must hold years since the pitch, not a calendar date."""
    df = pd.DataFrame({
        "name": ["A"],
        "cb_matched": [1],
        "origin_date": [pd.Timestamp("2015-09-01")],
        "exit_date": [pd.NaT],
        "first_post_event_round_on": [pd.Timestamp("2017-03-01")],
    })
    out = _build_time_to_funding(df)
    assert out["post_event_round_observed"].iloc[0] == 1
    assert 1.4 < out["time_to_first_post_event_round"].iloc[0] < 1.6


def test_time_to_funding_censors_at_crunchbase_vintage():
    """A firm with no round is censored at the dump date, not left missing."""
    df = pd.DataFrame({
        "name": ["A"],
        "cb_matched": [1],
        "origin_date": [pd.Timestamp("2015-09-01")],
        "exit_date": [pd.NaT],
        "first_post_event_round_on": [pd.NaT],
    })
    out = _build_time_to_funding(df)
    assert out["post_event_round_observed"].iloc[0] == 0
    expected = (pd.Timestamp(CB_DUMP_DATE) - pd.Timestamp("2015-09-01")).days / 365.25
    assert out["time_to_first_post_event_round"].iloc[0] == pytest.approx(expected)


def test_time_to_funding_exposure_ends_at_exit():
    """A firm that already exited is no longer at risk of raising a round."""
    df = pd.DataFrame({
        "name": ["A"],
        "cb_matched": [1],
        "origin_date": [pd.Timestamp("2015-09-01")],
        "exit_date": [pd.Timestamp("2017-09-01")],
        "first_post_event_round_on": [pd.NaT],
    })
    out = _build_time_to_funding(df)
    assert out["post_event_round_observed"].iloc[0] == 0
    assert out["funding_exposure_years"].iloc[0] == pytest.approx(2.0, abs=0.01)


def test_funding_vintage_is_older_than_survival_vintage():
    """Funding exposure must not run past the Crunchbase dump."""
    assert pd.Timestamp(CB_DUMP_DATE) <= pd.Timestamp(ANALYSIS_END_DATE)
