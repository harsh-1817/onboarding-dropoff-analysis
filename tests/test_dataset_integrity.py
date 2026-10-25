"""Data-integrity tests: the dataset must be internally consistent before any analysis is trusted."""
import pandas as pd
import pytest

from src_path import DATA_DIR  # noqa: F401  (adds src/ to sys.path)

USERS = DATA_DIR / "users.csv"
EVENTS = DATA_DIR / "funnel_events.csv"

pytestmark = pytest.mark.skipif(not EVENTS.exists(), reason="dataset not generated yet")


@pytest.fixture(scope="module")
def users():
    return pd.read_csv(USERS, parse_dates=["signup_ts"])


@pytest.fixture(scope="module")
def events():
    return pd.read_csv(EVENTS, parse_dates=["entered_at", "completed_at"])


def test_user_ids_are_unique_and_events_reference_known_users(users, events):
    assert users["user_id"].is_unique
    assert set(events["user_id"]) <= set(users["user_id"])


def test_every_user_starts_at_stage_one(users, events):
    first = events[events["stage_order"] == 1]
    assert len(first) == len(users)


def test_stage_sequence_has_no_gaps(events):
    mx = events.groupby("user_id")["stage_order"].max()
    n = events.groupby("user_id")["stage_order"].nunique()
    assert (mx == n).all()


def test_user_only_reaches_next_stage_after_completing_previous(events):
    ev = events.sort_values(["user_id", "stage_order"])
    prev = ev.groupby("user_id")["outcome"].shift()
    has_prev = ev["stage_order"] > 1
    assert (prev[has_prev] == "COMPLETED").all()


def test_timestamps_are_ordered(events):
    done = events.dropna(subset=["completed_at"])
    assert (done["completed_at"] >= done["entered_at"]).all()
    ev = events.sort_values(["user_id", "stage_order"])
    prev_done = ev.groupby("user_id")["completed_at"].shift()
    ok = prev_done.isna() | (ev["entered_at"] >= prev_done)
    assert ok.all()


def test_first_stage_starts_at_signup_time(users, events):
    m = events[events["stage_order"] == 1].merge(users[["user_id", "signup_ts"]], on="user_id")
    assert (m["entered_at"] == m["signup_ts"]).all()


def test_outcome_fields_are_consistent(events):
    assert events.loc[events["outcome"] == "COMPLETED", "completed_at"].notna().all()
    assert events.loc[events["outcome"] != "COMPLETED", "completed_at"].isna().all()
    assert events.loc[events["outcome"] == "DROPPED", "drop_reason"].notna().all()
    assert events.loc[events["outcome"] != "DROPPED", "drop_reason"].isna().all()


def test_attempts_and_durations_are_sane(events):
    assert events["attempts"].between(1, 3).all()
    assert (events["time_spent_sec"] >= 0).all()


def test_no_event_after_extraction_cutoff(events):
    assert events["entered_at"].max() <= pd.Timestamp("2026-10-15 23:59:59")


def test_funnel_never_grows(events):
    entered = events.groupby("stage_order").size()
    assert entered.is_monotonic_decreasing
