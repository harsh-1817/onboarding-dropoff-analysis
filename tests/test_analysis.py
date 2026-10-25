"""Tests for the analysis layer: funnel maths and lever sizing must be internally consistent."""
import pandas as pd
import pytest

from src_path import DATA_DIR  # noqa: F401  (puts src/ on sys.path)

pytestmark = pytest.mark.skipif(not (DATA_DIR / "funnel_events.csv").exists(), reason="dataset not generated yet")

import analysis  # noqa: E402


@pytest.fixture(scope="module")
def loaded():
    return analysis.load()


def test_funnel_starts_with_all_users_and_never_grows(loaded):
    users, ev = loaded
    f = analysis.overall_funnel(ev, len(users))
    assert f.loc[f.stage_order == 1, "entered"].iloc[0] == len(users)
    assert f["entered"].is_monotonic_decreasing
    assert (f["entered"] == f["completed"] + f["dropped"]).all()
    assert f["step_conversion"].between(0, 1).all()


def test_next_stage_entered_equals_previous_completed(loaded):
    users, ev = loaded
    f = analysis.overall_funnel(ev, len(users)).set_index("stage_order")
    for s in range(1, 10):
        assert f.loc[s + 1, "entered"] == f.loc[s, "completed"]


def test_segment_counts_add_up_to_the_overall_funnel(loaded):
    users, ev = loaded
    f = analysis.overall_funnel(ev, len(users)).set_index("stage_order")
    seg = analysis.segment_funnels(ev)
    for stype in ("Channel", "Bank", "City tier"):
        by_stage = seg[seg.segment_type == stype].groupby("stage_order")["entered"].sum()
        assert (by_stage == f["entered"]).all()


def test_lever_sizing_is_consistent(loaded):
    users, ev = loaded
    lv = analysis.lever_sizing(ev)
    assert (lv["excess_lost_vs_rest"] >= 0).all()
    assert (lv["seg_completed"] <= lv["seg_entered"]).all()
    f = analysis.overall_funnel(ev, len(users)).set_index("stage_order")
    for r in lv.itertuples():
        assert r.seg_entered + r.rest_entered <= f.loc[r.stage_order, "entered"]
    l1a = lv[lv.lever_id == "L1a"].iloc[0]          # unlinked vs linked users partition stage 2 exactly
    assert l1a.seg_entered + l1a.rest_entered == f.loc[2, "entered"]


def test_drop_reason_categories_cover_every_reason(loaded):
    _, ev = loaded
    _, overall, cat = analysis.reasons(ev)
    assert overall["reason_category"].notna().all()
    assert cat["users"].sum() == (ev["outcome"] == "DROPPED").sum()
