"""Funnel analysis: conversion, segments, drop-off reasons, timing, retries, latency and lever sizing.

Reads  data/users.csv + data/funnel_events.csv
Writes data/processed/*.csv (Power BI / Excel inputs), dashboard/charts/*.png, docs/key_findings.md
Run:   python src/analysis.py
"""
from __future__ import annotations

import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from config import (ACTIVATION_STAGE, CHART_DIR, DATA_DIR, DOCS_DIR, PROCESSED_DIR, REASON_CATEGORY,
                    STAGE_NAME, STAGE_SHORT, STAGES)

plt.rcParams.update({"figure.dpi": 140, "axes.spines.top": False, "axes.spines.right": False,
                     "font.family": "DejaVu Sans"})
BLUE, RED, GREY, GREEN, AMBER = "#1f4e79", "#c0392b", "#9aa5b1", "#2e8b57", "#e08a00"


# ------------------------------------------------------------------------------------------------ load
def load():
    users = pd.read_csv(DATA_DIR / "users.csv", parse_dates=["signup_ts"])
    ev = pd.read_csv(DATA_DIR / "funnel_events.csv", parse_dates=["entered_at", "completed_at"])
    h = users["signup_hour"]
    users["time_band"] = np.select(
        [(h >= 22) | (h < 6), h < 12, h < 18], ["Late night (22-05)", "Morning (06-11)", "Afternoon (12-17)"],
        default="Evening (18-21)")
    users["fno_label"] = np.where(users["seeks_fno"] == 1, "Wants F&O", "Cash / delivery only")
    ev["completed"] = (ev["outcome"] == "COMPLETED").astype(int)
    ev = ev.merge(users, on="user_id", how="left")
    return users, ev


SEGMENTS = {"Channel": "channel", "Device OS": "device_os", "Device tier": "device_tier", "City tier": "city_tier",
            "Age group": "age_group", "Bank": "bank", "KYC path": "kyc_path", "Trading interest": "fno_label",
            "Signup time": "time_band", "Campaign day": "campaign_day_type"}


# ------------------------------------------------------------------------------------------------ funnel
def overall_funnel(ev, n_users):
    g = ev.groupby("stage_order").agg(entered=("user_id", "size"), completed=("completed", "sum")).reset_index()
    g["stage_name"] = g["stage_order"].map(STAGE_NAME)
    g["stage_short"] = g["stage_order"].map(STAGE_SHORT)
    g["dropped"] = g["entered"] - g["completed"]
    g["step_conversion"] = g["completed"] / g["entered"]
    g["cumulative_conversion"] = g["completed"] / n_users
    g["lost_pct_of_signups"] = g["dropped"] / n_users
    return g[["stage_order", "stage_name", "stage_short", "entered", "completed", "dropped", "step_conversion",
              "cumulative_conversion", "lost_pct_of_signups"]]


def segment_funnels(ev):
    rows = []
    for stype, col in SEGMENTS.items():
        g = ev.groupby([col, "stage_order"]).agg(entered=("user_id", "size"), completed=("completed", "sum")).reset_index()
        g = g.rename(columns={col: "segment_value"})
        g.insert(0, "segment_type", stype)
        rows.append(g)
    out = pd.concat(rows, ignore_index=True)
    out["stage_short"] = out["stage_order"].map(STAGE_SHORT)
    out["step_conversion"] = out["completed"] / out["entered"]
    return out


def activation_by_segment(users, ev):
    done = ev[ev["completed"] == 1].groupby("user_id")["stage_order"].max()
    users = users.assign(max_done=users["user_id"].map(done).fillna(0))
    rows = []
    for stype, col in SEGMENTS.items():
        g = users.groupby(col).agg(users=("user_id", "size"),
                                   kyc_done=("max_done", lambda s: (s >= 2).sum()),
                                   activated=("max_done", lambda s: (s >= ACTIVATION_STAGE).sum()),
                                   funded=("max_done", lambda s: (s >= 9).sum()),
                                   traded=("max_done", lambda s: (s >= 10).sum())).reset_index()
        g = g.rename(columns={col: "segment_value"})
        g.insert(0, "segment_type", stype)
        rows.append(g)
    out = pd.concat(rows, ignore_index=True)
    total = len(users)
    base = (users["max_done"] >= ACTIVATION_STAGE).mean()
    out["activation_rate"] = out["activated"] / out["users"]
    out["funded_rate"] = out["funded"] / out["users"]
    out["traded_rate"] = out["traded"] / out["users"]
    out["activation_gap_pp"] = (out["activation_rate"] - base) * 100
    out["share_of_signups"] = out["users"] / total
    return out, users


# ------------------------------------------------------------------------------------------------ reasons
def reasons(ev):
    d = ev[ev["outcome"] == "DROPPED"].copy()
    d["reason_category"] = d["drop_reason"].map(REASON_CATEGORY)
    by_stage = d.groupby(["stage_order", "drop_reason", "reason_category"]).size().reset_index(name="users")
    by_stage["stage_short"] = by_stage["stage_order"].map(STAGE_SHORT)
    tot = by_stage.groupby("stage_order")["users"].transform("sum")
    by_stage["pct_of_stage_drops"] = by_stage["users"] / tot
    overall = d.groupby(["drop_reason", "reason_category"]).size().reset_index(name="users").sort_values("users", ascending=False)
    overall["share"] = overall["users"] / overall["users"].sum()
    overall["cumulative_share"] = overall["share"].cumsum()
    cat = d.groupby("reason_category").size().reset_index(name="users").sort_values("users", ascending=False)
    cat["share"] = cat["users"] / cat["users"].sum()
    cat["cumulative_share"] = cat["share"].cumsum()
    return by_stage.sort_values(["stage_order", "users"], ascending=[True, False]), overall, cat


# ------------------------------------------------------------------------------------------------ timing etc.
def timing(ev):
    c = ev[(ev["completed"] == 1) & (ev["stage_order"] != 8)]
    t = c.groupby("stage_order")["time_spent_sec"].agg(median_sec="median", p90_sec=lambda s: s.quantile(.9)).reset_index()
    a8 = ev[(ev["stage_order"] == 8) & (ev["completed"] == 1)]
    t8 = pd.DataFrame({"stage_order": [8], "median_sec": [a8["time_spent_sec"].median()],
                       "p90_sec": [a8["time_spent_sec"].quantile(.9)]})
    t = pd.concat([t[t["stage_order"] != 8], t8]).sort_values("stage_order")
    t["stage_short"] = t["stage_order"].map(STAGE_SHORT)
    t["median_minutes"] = t["median_sec"] / 60
    t["p90_minutes"] = t["p90_sec"] / 60
    return t


def time_to_activation(users, ev):
    a = ev[(ev["stage_order"] == ACTIVATION_STAGE) & (ev["completed"] == 1)][["user_id", "completed_at"]]
    a = a.merge(users[["user_id", "signup_ts", "kyc_path"]], on="user_id")
    a["hours"] = (a["completed_at"] - a["signup_ts"]).dt.total_seconds() / 3600
    return a


def weekly(users, ev):
    u = users.copy()
    u["week"] = u["signup_ts"].dt.to_period("W-SUN").dt.start_time
    st = ev.pivot_table(index="user_id", columns="stage_order", values="completed", aggfunc="max").fillna(0)
    u = u.join(st, on="user_id")
    g = u.groupby("week").agg(signups=("user_id", "size"), kyc=(2, "mean"), bank=(3, "mean"),
                              activated=(ACTIVATION_STAGE, "mean"), funded=(9, "mean")).reset_index()
    return g.rename(columns={"kyc": "kyc_rate", "bank": "bank_rate", "activated": "activation_rate", "funded": "funded_rate"})


def retries(ev):
    g = ev.groupby(["stage_order", "attempts"]).agg(entered=("user_id", "size"), completed=("completed", "sum")).reset_index()
    g["completion_rate"] = g["completed"] / g["entered"]
    g["stage_short"] = g["stage_order"].map(STAGE_SHORT)
    return g


LAT_BINS = {2: [0, 10, 30, 1e9], 3: [0, 30, 120, 300, 1e9], 6: [0, 8, 15, 1e9], 7: [0, 10, 20, 1e9]}


def latency(ev):
    rows = []
    for s, bins in LAT_BINS.items():
        d = ev[ev["stage_order"] == s].copy()
        d["bucket"] = pd.cut(d["system_latency_sec"], bins, right=False)
        g = d.groupby("bucket", observed=True).agg(entered=("user_id", "size"), completed=("completed", "sum")).reset_index()
        g["label"] = [f"{int(iv.left)}-{int(iv.right)}s" if iv.right < 1e8 else f"{int(iv.left)}s+" for iv in g["bucket"]]
        g.insert(0, "stage_order", s)
        g["stage_short"] = STAGE_SHORT[s]
        g["completion_rate"] = g["completed"] / g["entered"]
        rows.append(g.drop(columns="bucket"))
    return pd.concat(rows, ignore_index=True)


# ------------------------------------------------------------------------------------------------ levers
def lever_sizing(ev):
    problem_banks = ["Punjab National Bank", "Bank of Baroda", "Co-operative / other"]
    low_or_web_or_old = (ev["device_tier"] == "Low-end") | (ev["device_os"] == "Web") | (ev["age"] >= 55)
    defs = [
        ("L1a", "Alternative KYC path for users whose Aadhaar is not linked to their mobile (KYC stage)", 2,
         "Aadhaar not linked to mobile", ev["aadhaar_mobile_linked"] == 0, None),
        ("L1b", "Offline-KYC users blocked at e-Sign (signature step)", 7,
         "Aadhaar not linked to mobile", ev["aadhaar_mobile_linked"] == 0, None),
        ("L2", "Bank-verification fallback (UPI / cancelled-cheque upload) for problem banks", 3,
         "PNB, Bank of Baroda, Co-operative / other", ev["bank"].isin(problem_banks), None),
        ("L3", "Save-and-resume with reminders for late-night KYC starters", 2,
         "Signed up 22:00-05:59 (DigiLocker-eligible)", (ev["time_band"] == "Late night (22-05)") & (ev["aadhaar_mobile_linked"] == 1),
         (ev["time_band"] != "Late night (22-05)") & (ev["aadhaar_mobile_linked"] == 1)),   # like-for-like benchmark
        ("L4", "Assisted selfie / IPV capture for low-end Android, web and 55+ users", 6,
         "Low-end Android, web or age 55+", low_or_web_or_old, None),
        ("L5", "First-funding nudges (one-tap UPI, starter offer) for paid-social/influencer users", 9,
         "Influencer / YouTube and Meta / social ads", ev["channel"].isin(["Influencer / YouTube", "Meta / social ads"]), None),
        ("L6", "Simplified income-proof upload for F&O seekers", 5,
         "Wants F&O", ev["seeks_fno"] == 1, None),
    ]
    rows = []
    for lid, name, stage, seg_def, mask, bench in defs:
        d = ev[ev["stage_order"] == stage]
        m = mask.loc[d.index]
        seg = d[m]
        rest = d[bench.loc[d.index]] if bench is not None else d[~m]
        rows.append({"lever_id": lid, "lever": name, "stage_order": stage, "stage_short": STAGE_SHORT[stage],
                     "segment_definition": seg_def,
                     "seg_entered": len(seg), "seg_completed": int(seg["completed"].sum()),
                     "rest_entered": len(rest), "rest_completed": int(rest["completed"].sum())})
    out = pd.DataFrame(rows)
    out["seg_conv"] = out["seg_completed"] / out["seg_entered"]
    out["rest_conv"] = out["rest_completed"] / out["rest_entered"]
    out["gap_pp"] = (out["rest_conv"] - out["seg_conv"]) * 100
    out["users_lost_in_segment"] = out["seg_entered"] - out["seg_completed"]
    out["excess_lost_vs_rest"] = (out["seg_entered"] * (out["rest_conv"] - out["seg_conv"])).clip(lower=0).round().astype(int)
    return out


# ------------------------------------------------------------------------------------------------ charts
def fmt_int(x):
    return f"{int(x):,}"


def chart_funnel(f, n):
    fig, ax = plt.subplots(figsize=(10, 5.6))
    y = np.arange(len(f))[::-1]
    ax.barh(y, f["entered"], color=BLUE, height=.62)
    for yi, (_, r) in zip(y, f.iterrows()):
        ax.text(r["entered"] + n * .01, yi + .08, fmt_int(r["entered"]), va="center", fontsize=8.5, fontweight="bold")
        col = RED if r["step_conversion"] < .75 else (AMBER if r["step_conversion"] < .88 else GREEN)
        ax.text(r["entered"] + n * .01, yi - .24, f"{r['step_conversion']:.0%} continue to next step", va="center", fontsize=7.5, color=col)
    ax.set_yticks(y)
    ax.set_yticklabels([f"{o}. {s}" for o, s in zip(f["stage_order"], f["stage_short"])], fontsize=9)
    ax.set_xlim(0, n * 1.32)
    ax.set_xticks([])
    ax.spines["bottom"].set_visible(False)
    ax.set_title(f"Of {n:,} sign-ups, only {f.loc[f.stage_order == ACTIVATION_STAGE, 'cumulative_conversion'].iloc[0]:.0%} get an activated account "
                 f"and {f.loc[f.stage_order == 10, 'cumulative_conversion'].iloc[0]:.0%} place a first trade",
                 loc="left", fontsize=10.5, fontweight="bold")
    fig.tight_layout(); fig.savefig(CHART_DIR / "01_onboarding_funnel.png"); plt.close(fig)


def chart_leaks(f):
    fig, ax = plt.subplots(figsize=(10, 4.8))
    colors = [RED if v >= f["lost_pct_of_signups"].max() * .6 else GREY for v in f["lost_pct_of_signups"]]
    ax.bar(f["stage_short"], f["lost_pct_of_signups"] * 100, color=colors)
    for i, (v, d) in enumerate(zip(f["lost_pct_of_signups"], f["dropped"])):
        ax.text(i, v * 100 + .3, f"{v:.1%}\n({d:,})", ha="center", fontsize=8)
    ax.set_ylabel("Users lost at stage (% of all sign-ups)")
    ax.set_title("Where the leaks are: KYC and first funding lose the most users", loc="left", fontweight="bold", fontsize=11)
    ax.set_ylim(0, f["lost_pct_of_signups"].max() * 100 * 1.25)
    plt.xticks(rotation=20)
    fig.tight_layout(); fig.savefig(CHART_DIR / "02_users_lost_by_stage.png"); plt.close(fig)


def chart_heatmap(seg, overall):
    pick = ["Channel", "Device tier", "City tier", "Age group", "KYC path", "Signup time"]
    d = seg[seg["segment_type"].isin(pick) & seg["stage_order"].between(2, 9)].copy()
    ov = overall.set_index("stage_order")["step_conversion"]
    d["gap"] = d["step_conversion"] - d["stage_order"].map(ov)
    d["row"] = d["segment_type"] + ": " + d["segment_value"].astype(str)
    order = [f"{t}: {v}" for t in pick for v in dict.fromkeys(d[d.segment_type == t]["segment_value"])]
    mat = d.pivot(index="row", columns="stage_order", values="gap").loc[order]
    val = d.pivot(index="row", columns="stage_order", values="step_conversion").loc[order]
    fig, ax = plt.subplots(figsize=(10, 9.5))
    im = ax.imshow(mat.values * 100, cmap="RdYlGn", vmin=-25, vmax=25, aspect="auto")
    ax.set_xticks(range(mat.shape[1])); ax.set_xticklabels([STAGE_SHORT[c] for c in mat.columns], fontsize=9)
    ax.set_yticks(range(mat.shape[0])); ax.set_yticklabels(mat.index, fontsize=8)
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            ax.text(j, i, f"{val.values[i, j]:.0%}", ha="center", va="center", fontsize=7)
    ax.set_title("Step conversion by segment (colour = percentage points vs overall)", loc="left", fontweight="bold", fontsize=11)
    fig.colorbar(im, shrink=.6, label="pp vs overall")
    fig.tight_layout(); fig.savefig(CHART_DIR / "03_segment_heatmap.png"); plt.close(fig)


def chart_pareto(cat, overall):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    ax = axes[0]
    ax.barh(cat["reason_category"][::-1], cat["users"][::-1], color=[GREY if "Unknown" in c else BLUE for c in cat["reason_category"][::-1]])
    for i, (u, s) in enumerate(zip(cat["users"][::-1], cat["share"][::-1])):
        ax.text(u + 40, i, f"{s:.0%}", va="center", fontsize=8)
    ax.set_title("Drop-offs by reason category", loc="left", fontweight="bold", fontsize=10)
    top = overall.head(10)
    ax = axes[1]
    ax.barh(top["drop_reason"][::-1], top["users"][::-1], color=[GREY if r == "ABANDONED_NO_REASON" else BLUE for r in top["drop_reason"][::-1]])
    ax.set_title("Top 10 reasons (grey = no reason captured)", loc="left", fontweight="bold", fontsize=10)
    ax.tick_params(axis="y", labelsize=7.5)
    fig.tight_layout(); fig.savefig(CHART_DIR / "04_drop_reasons.png"); plt.close(fig)


def chart_weekly(w):
    fig, ax = plt.subplots(figsize=(10, 4.6))
    ax.bar(w["week"], w["signups"], width=5, color="#cfd8e3", label="Weekly sign-ups")
    ax.set_ylabel("Sign-ups")
    ax2 = ax.twinx()
    ax2.plot(w["week"], w["activation_rate"] * 100, color=BLUE, marker="o", ms=3, label="Activation rate")
    ax2.plot(w["week"], w["funded_rate"] * 100, color=GREEN, marker="o", ms=3, label="Funded rate")
    ax2.set_ylabel("% of that week's sign-ups"); ax2.set_ylim(0, 45)
    ax2.spines["right"].set_visible(True)
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper left", fontsize=8, frameon=False)
    ax.set_title("Sign-up volume vs conversion by weekly cohort", loc="left", fontweight="bold", fontsize=11)
    fig.tight_layout(); fig.savefig(CHART_DIR / "05_weekly_trend.png"); plt.close(fig)


def chart_time(a):
    fig, ax = plt.subplots(figsize=(10, 4.6))
    for path, col in (("DigiLocker (digital)", BLUE), ("Offline / manual", RED)):
        h = a[a["kyc_path"] == path]["hours"].clip(upper=24 * 10)
        ax.hist(h, bins=60, alpha=.65, color=col, label=f"{path} (median {h.median():.0f}h)")
    ax.set_xlabel("Hours from sign-up to activation (capped at 10 days)"); ax.set_ylabel("Accounts")
    ax.legend(frameon=False, fontsize=9)
    ax.set_title("Offline-KYC users take far longer to activate", loc="left", fontweight="bold", fontsize=11)
    fig.tight_layout(); fig.savefig(CHART_DIR / "06_time_to_activation.png"); plt.close(fig)


def chart_levers(lv):
    d = lv.sort_values("excess_lost_vs_rest")
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.barh([f"{r.lever_id}  {r.segment_definition}" for r in d.itertuples()], d["excess_lost_vs_rest"], color=BLUE)
    for i, (v, g) in enumerate(zip(d["excess_lost_vs_rest"], d["gap_pp"])):
        ax.text(v + 15, i, f"{v:,} users ({g:.0f} pp gap)", va="center", fontsize=8)
    ax.set_xlim(0, d["excess_lost_vs_rest"].max() * 1.3)
    ax.set_title("Excess users lost vs the rest of the base, by improvement opportunity", loc="left", fontweight="bold", fontsize=11)
    ax.tick_params(axis="y", labelsize=8)
    fig.tight_layout(); fig.savefig(CHART_DIR / "07_opportunity_sizing.png"); plt.close(fig)


def chart_latency(lat):
    d = lat[lat["stage_order"] == 3]
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    ax.bar(d["label"], d["completion_rate"] * 100, color=[GREEN, GREEN, AMBER, RED][:len(d)])
    for i, (r, n) in enumerate(zip(d["completion_rate"], d["entered"])):
        ax.text(i, r * 100 + 1, f"{r:.0%}\n(n={n:,})", ha="center", fontsize=8)
    ax.set_ylim(0, 105); ax.set_ylabel("Bank-verification completion (%)"); ax.set_xlabel("Penny-drop response time")
    ax.set_title("Slow bank verification drives abandonment", loc="left", fontweight="bold", fontsize=11)
    fig.tight_layout(); fig.savefig(CHART_DIR / "08_bank_latency.png"); plt.close(fig)


# ------------------------------------------------------------------------------------------------ main
def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True); CHART_DIR.mkdir(parents=True, exist_ok=True)
    users, ev = load()
    n = len(users)
    f = overall_funnel(ev, n)
    seg = segment_funnels(ev)
    act, users_m = activation_by_segment(users, ev)
    r_stage, r_overall, r_cat = reasons(ev)
    tm = timing(ev)
    tta = time_to_activation(users, ev)
    wk = weekly(users, ev)
    rt = retries(ev)
    lat = latency(ev)
    lv = lever_sizing(ev)

    pd.DataFrame(STAGES, columns=["stage_order", "stage_name", "stage_short"]).to_csv(PROCESSED_DIR / "dim_stage.csv", index=False)
    f.round(5).to_csv(PROCESSED_DIR / "funnel_overall.csv", index=False)
    seg.round(5).to_csv(PROCESSED_DIR / "funnel_by_segment.csv", index=False)
    act.round(5).to_csv(PROCESSED_DIR / "activation_by_segment.csv", index=False)
    r_stage.round(5).to_csv(PROCESSED_DIR / "drop_reasons_by_stage.csv", index=False)
    r_overall.round(5).to_csv(PROCESSED_DIR / "drop_reasons_overall.csv", index=False)
    r_cat.round(5).to_csv(PROCESSED_DIR / "drop_reason_categories.csv", index=False)
    tm.round(3).to_csv(PROCESSED_DIR / "stage_timing.csv", index=False)
    wk.round({"kyc_rate": 5, "bank_rate": 5, "activation_rate": 5, "funded_rate": 5}).to_csv(PROCESSED_DIR / "weekly_trend.csv", index=False)
    rt.round(5).to_csv(PROCESSED_DIR / "retry_analysis.csv", index=False)
    lat.round(5).to_csv(PROCESSED_DIR / "latency_analysis.csv", index=False)
    lv.round(5).to_csv(PROCESSED_DIR / "lever_sizing.csv", index=False)

    chart_funnel(f, n); chart_leaks(f); chart_heatmap(seg, f); chart_pareto(r_cat, r_overall)
    chart_weekly(wk); chart_time(tta); chart_levers(lv); chart_latency(lat)

    # ---- headline numbers for the documents ---------------------------------------------------------
    def conv(stype, val, stage):
        r = seg[(seg.segment_type == stype) & (seg.segment_value.astype(str) == val) & (seg.stage_order == stage)]
        return float(r["step_conversion"].iloc[0])

    def actv(stype, val):
        r = act[(act.segment_type == stype) & (act.segment_value.astype(str) == val)].iloc[0]
        return float(r["activation_rate"]), int(r["users"])

    fo = f.set_index("stage_order")
    unk = float(r_cat[r_cat.reason_category.str.startswith("Unknown")]["share"].sum())
    k = {
        "signups": n, "period": f"{users.signup_ts.min():%d %b %Y} to {users.signup_ts.max():%d %b %Y}",
        "activated": int(fo.loc[8, "completed"]), "activation_rate": float(fo.loc[8, "cumulative_conversion"]),
        "funded": int(fo.loc[9, "completed"]), "funded_rate": float(fo.loc[9, "cumulative_conversion"]),
        "traded": int(fo.loc[10, "completed"]), "traded_rate": float(fo.loc[10, "cumulative_conversion"]),
        "step_conv": {int(o): float(v) for o, v in fo["step_conversion"].items()},
        "lost": {int(o): int(v) for o, v in fo["dropped"].items()},
        "kyc_aadhaar_unlinked": conv("KYC path", "Offline / manual", 2), "kyc_aadhaar_linked": conv("KYC path", "DigiLocker (digital)", 2),
        "kyc_late": conv("Signup time", "Late night (22-05)", 2), "kyc_morning": conv("Signup time", "Morning (06-11)", 2),
        "kyc_low": conv("Device tier", "Low-end", 2), "kyc_ios": conv("Device OS", "iOS", 2),
        "kyc_55": conv("Age group", "55+", 2), "kyc_25_34": conv("Age group", "25-34", 2),
        "bank_pnb": conv("Bank", "Punjab National Bank", 3), "bank_coop": conv("Bank", "Co-operative / other", 3),
        "bank_hdfc": conv("Bank", "HDFC Bank", 3), "bank_overall": float(fo.loc[3, "step_conversion"]),
        "selfie_low": conv("Device tier", "Low-end", 6), "selfie_ios": conv("Device OS", "iOS", 6), "selfie_web": conv("Device OS", "Web", 6),
        "esign_unlinked": conv("KYC path", "Offline / manual", 7), "esign_linked": conv("KYC path", "DigiLocker (digital)", 7),
        "fno_income": conv("Trading interest", "Wants F&O", 5), "cash_income": conv("Trading interest", "Cash / delivery only", 5),
        "fund_referral": conv("Channel", "Referral", 9), "fund_influencer": conv("Channel", "Influencer / YouTube", 9),
        "act_referral": actv("Channel", "Referral")[0], "act_influencer": actv("Channel", "Influencer / YouTube")[0],
        "act_offline": actv("KYC path", "Offline / manual")[0], "act_digital": actv("KYC path", "DigiLocker (digital)")[0],
        "offline_users": actv("KYC path", "Offline / manual")[1],
        "unknown_reason_share": unk,
        "top_reason_categories": [[r.reason_category, int(r.users), float(r.share)] for r in r_cat.head(6).itertuples()],
        "median_hours_to_activate": float(tta["hours"].median()),
        "median_hours_digital": float(tta[tta.kyc_path.str.startswith("Digi")]["hours"].median()),
        "median_hours_offline": float(tta[tta.kyc_path.str.startswith("Offline")]["hours"].median()),
        "pct_activated_within_24h": float((tta["hours"] <= 24).mean()),
        "lat3": {r.label: [int(r.entered), float(r.completion_rate)] for r in lat[lat.stage_order == 3].itertuples()},
        "levers": lv[["lever_id", "excess_lost_vs_rest", "gap_pp", "seg_entered", "seg_conv", "rest_conv"]].round(4).to_dict("records"),
        "months_in_period": round((users.signup_ts.max() - users.signup_ts.min()).days / 30.44, 2),
    }
    (PROCESSED_DIR / "key_numbers.json").write_text(json.dumps(k, indent=2))
    write_findings(k, f, lv, r_cat)
    print(json.dumps({x: k[x] for x in ("signups", "activation_rate", "funded_rate", "traded_rate", "unknown_reason_share",
                                       "median_hours_to_activate", "pct_activated_within_24h")}, indent=1))


def write_findings(k, f, lv, cat):
    L = ["# Key findings (auto-generated from the data)", "",
         "> Synthetic dataset: patterns reflect the assumptions in `src/generate_dataset.py`, not any real company.", "",
         f"Period: **{k['period']}** | Sign-ups: **{k['signups']:,}** | Activated: **{k['activated']:,} ({k['activation_rate']:.1%})** | "
         f"Funded: **{k['funded']:,} ({k['funded_rate']:.1%})** | First trade: **{k['traded']:,} ({k['traded_rate']:.1%})**", "",
         "## Funnel", "", f.assign(step_conversion=lambda d: (d.step_conversion * 100).round(1),
                                    cumulative_conversion=lambda d: (d.cumulative_conversion * 100).round(1),
                                    lost_pct_of_signups=lambda d: (d.lost_pct_of_signups * 100).round(1))
         [["stage_order", "stage_name", "entered", "completed", "dropped", "step_conversion", "cumulative_conversion", "lost_pct_of_signups"]]
         .to_markdown(index=False), "", "## Opportunity sizing (excess users lost vs the rest of the base)", "",
         lv[["lever_id", "segment_definition", "stage_short", "seg_entered", "seg_conv", "rest_conv", "gap_pp", "excess_lost_vs_rest"]]
         .round(3).to_markdown(index=False), "", "## Drop-off reason categories", "",
         cat.round(3).to_markdown(index=False), ""]
    (DOCS_DIR / "key_findings.md").write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    main()
