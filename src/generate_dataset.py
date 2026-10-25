"""Generate a SYNTHETIC stockbroker onboarding funnel dataset.

IMPORTANT: this is simulated data, not data from any real company. The behavioural patterns below are
assumptions inspired by how digital account-opening flows in India typically work (DigiLocker KYC, bank
penny-drop verification, selfie/IPV, Aadhaar e-Sign). They exist so the analysis has realistic structure
to find. Every assumption is visible in this file.

Method
  * 20,000 users sign up between 1 Apr and 31 Aug 2026; data is extracted on 15 Oct 2026.
  * Users move through 10 stages. At each stage completion is a logistic function of user attributes
    (channel, device, city tier, age, bank, Aadhaar-mobile linkage, signup hour, system latency ...)
    plus a per-user "intent" random effect that correlates behaviour across stages.
  * The intercept of every stage is calibrated so the overall step conversion hits TARGET_CONV, so the
    aggregate funnel is controlled while the SEGMENT differences carry the insight.

Run:  python src/generate_dataset.py      (seeded, so the output is reproducible)
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from config import DATA_DIR, STAGE_NAME

SEED = 2026
N_USERS = 20_000
START, END = pd.Timestamp("2026-04-01"), pd.Timestamp("2026-08-31")
CUTOFF = pd.Timestamp("2026-10-15 23:59:59")          # data extraction time
SPIKE_DAYS = ["2026-04-20", "2026-05-12", "2026-06-03", "2026-07-08", "2026-07-29", "2026-08-18"]

# Overall step conversion targets (completed / entered) used to calibrate each stage
TARGET_CONV = {1: 0.90, 2: 0.70, 3: 0.80, 4: 0.92, 5: 0.90, 6: 0.86, 7: 0.90, 8: 0.93, 9: 0.58, 10: 0.72}

CHANNELS = ["Organic", "Google Ads", "Influencer / YouTube", "Referral", "Partner / sub-broker", "Meta / social ads"]
CHANNEL_P = [0.28, 0.22, 0.18, 0.14, 0.10, 0.08]
BANKS = ["SBI", "HDFC Bank", "ICICI Bank", "Axis Bank", "Kotak Mahindra Bank", "Punjab National Bank",
         "Bank of Baroda", "Canara Bank", "Union Bank", "Co-operative / other"]
BANK_P = [0.22, 0.17, 0.13, 0.09, 0.05, 0.07, 0.05, 0.04, 0.03, 0.15]
HOUR_W = np.array([1, .6, .4, .3, .3, .5, 1, 2, 4, 6, 7, 6, 5, 5, 5, 5, 5, 6, 7, 8, 9, 8, 5, 2.5])

CH_EARLY = {"Referral": .45, "Organic": .20, "Partner / sub-broker": .10, "Google Ads": 0.0,
            "Influencer / YouTube": -.35, "Meta / social ads": -.30}
CH_FUND = {"Referral": .50, "Organic": .15, "Partner / sub-broker": .20, "Google Ads": 0.0,
           "Influencer / YouTube": -.35, "Meta / social ads": -.30}
BANK_EFF = {"SBI": -.10, "HDFC Bank": .20, "ICICI Bank": .20, "Axis Bank": .10, "Kotak Mahindra Bank": .10,
            "Punjab National Bank": -.65, "Bank of Baroda": -.30, "Canara Bank": -.20, "Union Bank": -.25,
            "Co-operative / other": -.90}
BANK_LAT = {"SBI": 1.4, "HDFC Bank": 1.0, "ICICI Bank": 1.0, "Axis Bank": 1.0, "Kotak Mahindra Bank": 1.0,
            "Punjab National Bank": 3.0, "Bank of Baroda": 2.0, "Canara Bank": 1.5, "Union Bank": 1.6,
            "Co-operative / other": 3.5}

FLAKY = {1: .15, 2: .30, 3: .25, 4: .05, 5: .05, 6: .35, 7: .20, 8: .02, 9: .10, 10: .05}   # P(first attempt fails)
DUR_MED = {1: 75, 2: 300, 3: 150, 4: 240, 5: 200, 6: 110, 7: 140, 9: 180, 10: 120}          # seconds


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def calibrate(effects: np.ndarray, target: float) -> float:
    """Intercept b such that mean(sigmoid(b + effects)) == target (bisection)."""
    lo, hi = -10.0, 10.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if sigmoid(mid + effects).mean() < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def draw(rng, labels, probs, n):
    p = np.array(probs, dtype=float)
    return rng.choice(labels, size=n, p=p / p.sum())


def build_users(rng) -> pd.DataFrame:
    days = pd.date_range(START, END)
    trend = 1 + 0.25 * np.arange(len(days)) / len(days)
    weekend = np.where(days.dayofweek >= 5, 0.85, 1.0)
    spike = np.where(days.isin(pd.to_datetime(SPIKE_DAYS)), 2.5, 1.0)
    w = trend * weekend * spike
    day_idx = rng.choice(len(days), size=N_USERS, p=w / w.sum())
    hour = rng.choice(24, size=N_USERS, p=HOUR_W / HOUR_W.sum())
    ts = (days[day_idx] + pd.to_timedelta(hour, "h") + pd.to_timedelta(rng.integers(0, 3600, N_USERS), "s"))

    channel = draw(rng, CHANNELS, CHANNEL_P, N_USERS)
    city = draw(rng, ["Tier 1", "Tier 2", "Tier 3"], [.35, .38, .27], N_USERS)
    os_ = draw(rng, ["Android", "iOS", "Web"], [.72, .18, .10], N_USERS)
    tier3 = city == "Tier 3"
    tier_draw = np.where(tier3, rng.random(N_USERS) < .55, rng.random(N_USERS) < .35)   # low-end share of Android
    dev_tier = np.where(os_ == "Android", np.where(tier_draw, "Low-end",
                        np.where(rng.random(N_USERS) < .78, "Mid-range", "High-end")),
                        np.where(os_ == "iOS", "High-end", "Desktop"))
    age = np.clip(rng.normal(32, 9, N_USERS).round(), 18, 70).astype(int)
    age_group = pd.cut(age, [17, 24, 34, 44, 54, 100], labels=["18-24", "25-34", "35-44", "45-54", "55+"]).astype(str)

    bank = np.empty(N_USERS, dtype=object)
    base = np.array(BANK_P)
    for t in (True, False):
        p = base.copy()
        if t:
            for b, m in (("Co-operative / other", 2.0), ("Punjab National Bank", 1.5), ("HDFC Bank", .6), ("ICICI Bank", .6)):
                p[BANKS.index(b)] *= m
        idx = np.where(tier3 == t)[0]
        bank[idx] = draw(rng, BANKS, p, len(idx))

    linked = rng.random(N_USERS) < np.where(age >= 55, .80, .88)
    fno_p = pd.Series(channel).map({"Influencer / YouTube": .45, "Meta / social ads": .35, "Referral": .20}).fillna(.28).to_numpy()
    seeks_fno = rng.random(N_USERS) < fno_p

    df = pd.DataFrame({
        "signup_ts": ts, "channel": channel, "device_os": os_, "device_tier": dev_tier, "city_tier": city,
        "age": age, "age_group": age_group, "bank": bank, "aadhaar_mobile_linked": linked.astype(int),
        "kyc_path": np.where(linked, "DigiLocker (digital)", "Offline / manual"),
        "seeks_fno": seeks_fno.astype(int),
        "campaign_day_type": np.where(ts.normalize().isin(pd.to_datetime(SPIKE_DAYS)), "IPO / market-rally spike", "Normal day"),
    })
    df = df.sort_values("signup_ts").reset_index(drop=True)
    df.insert(0, "user_id", [f"U{i:06d}" for i in range(1, len(df) + 1)])
    df.insert(2, "signup_date", df["signup_ts"].dt.date.astype(str))
    df.insert(3, "signup_hour", df["signup_ts"].dt.hour)
    return df


def build_events(rng, u: pd.DataFrame) -> pd.DataFrame:
    n = len(u)
    ch, bank = u["channel"].to_numpy(), u["bank"].to_numpy()
    os_, tier, city = u["device_os"].to_numpy(), u["device_tier"].to_numpy(), u["city_tier"].to_numpy()
    age, linked, fno = u["age"].to_numpy(), u["aadhaar_mobile_linked"].to_numpy() == 1, u["seeks_fno"].to_numpy() == 1
    hour = u["signup_hour"].to_numpy()
    late = (hour >= 22) | (hour < 6)
    spike = (u["campaign_day_type"] != "Normal day").to_numpy()
    low, web, ios, old, young = tier == "Low-end", os_ == "Web", os_ == "iOS", age >= 55, age < 25
    t3 = city == "Tier 3"
    ch_e = pd.Series(ch).map(CH_EARLY).to_numpy()
    ch_f = pd.Series(ch).map(CH_FUND).to_numpy()
    bank_e = pd.Series(bank).map(BANK_EFF).to_numpy()
    bank_l = pd.Series(bank).map(BANK_LAT).to_numpy()
    intent = rng.normal(0, 0.6, n)

    # System latency (seconds) for stages with an external system call
    lat_med = {2: 10, 3: 40, 6: 6, 7: 8}
    lat = {}
    for s, med in lat_med.items():
        mult = np.where(low, 1.6, 1.0) * np.where(t3, 1.2, 1.0) * (bank_l if s == 3 else 1.0)
        lat[s] = np.round(rng.lognormal(np.log(med), 0.8, n) * mult, 1)

    def effects(s):
        e = np.zeros(n)
        if s == 1:
            e += ch_e + np.where(web, .2, 0) - np.where(spike, .3, 0)
        elif s == 2:
            e += .6 * ch_e + np.where(ios, .25, 0) - np.where(low, .35, 0) - np.where(web, .1, 0) - np.where(t3, .2, 0)
            e += -np.where(old, .5, 0) + np.where(young, .1, 0) - np.where(late, .55, 0) - np.where(~linked, 1.9, 0)
            e += -np.where(lat[2] > 30, .5, 0) - np.where(spike, .25, 0)
        elif s == 3:
            e += -np.where(t3, .3, 0) + bank_e - np.where(low, .1, 0) - np.where(old, .2, 0)
            e += -np.where(lat[3] > 300, .9, np.where(lat[3] > 120, .4, 0))
        elif s == 4:
            e += -np.where(old, .3, 0) + np.where(web, .1, 0) + .3 * np.minimum(ch_e, 0)
        elif s == 5:
            e += -np.where(fno, 1.2, 0)
        elif s == 6:
            e += -np.where(low, .55, np.where(tier == "Mid-range", .1, 0)) + np.where(ios, .3, 0) - np.where(web, .45, 0)
            e += -np.where(old, .45, 0) - np.where(lat[6] > 15, .4, 0) - np.where(late, .3, 0)
        elif s == 7:
            e += -np.where(old, .4, 0) - np.where(~linked, 1.2, 0) - np.where(lat[7] > 20, .4, 0)
        elif s == 8:
            e += -np.where(~linked, .6, 0)
        elif s == 9:
            e += ch_f + np.where(city == "Tier 1", .2, 0) - np.where(t3, .2, 0) + np.where((age >= 25) & (age < 45), .1, 0)
            e += -np.where(low, .1, 0) + np.where(fno, .3, 0)
        elif s == 10:
            e += np.where(fno, .3, 0) + np.where(ch == "Referral", .2, 0) - np.where(ch == "Influencer / YouTube", .2, 0) + np.where(ios, .15, 0)
        return e + intent * (1.0 if s <= 3 else 0.7)

    t0 = (u["signup_ts"] - pd.Timestamp("1970-01-01")).dt.total_seconds().to_numpy()   # epoch seconds (unit-safe)
    alive = np.ones(n, dtype=bool)
    t_enter = t0.copy()
    frames = []
    for s in range(1, 11):
        idx = np.where(alive)[0]
        e = effects(s)[idx]
        b = calibrate(e, TARGET_CONV[s])
        done = rng.random(len(idx)) < sigmoid(b + e)

        # --- timing --------------------------------------------------------------------------------
        slow = np.where(old[idx], 1.5, 1.0) * np.where(low[idx], 1.2, 1.0)
        if s == 8:
            med = 20 * 3600 * np.where(linked[idx], 1.0, 2.5)
            dur = rng.lognormal(np.log(med), 0.9)
        else:
            dur = rng.lognormal(np.log(DUR_MED[s]), 0.6, len(idx)) * slow
            if s in lat:
                dur = dur + lat[s][idx]
        dur = np.where(done, dur, dur * 1.3)
        entered = t_enter[idx]
        completed = np.where(done, entered + dur, np.nan)

        # --- attempts ------------------------------------------------------------------------------
        f = np.clip(FLAKY[s] * np.where(low[idx], 1.3, 1.0), 0, .6)
        r = rng.random(len(idx))
        att_done = np.where(r < 1 - f, 1, np.where(r < 1 - f + .7 * f, 2, 3))
        flaky = FLAKY[s] >= .2
        pr = [.5, .3, .2] if flaky else [.8, .15, .05]
        att_drop = rng.choice([1, 2, 3], size=len(idx), p=pr)
        attempts = np.where(done, att_done, att_drop)

        # --- drop reasons --------------------------------------------------------------------------
        reason = np.full(len(idx), None, dtype=object)
        dm = ~done
        reason[dm] = drop_reasons(rng, s, dm, idx, linked, late, bank, lat, fno, web)

        frames.append(pd.DataFrame({
            "user_idx": idx, "stage_order": s, "entered_s": entered, "completed_s": completed,
            "outcome": np.where(done, "COMPLETED", "DROPPED"), "attempts": attempts,
            "system_latency_sec": lat[s][idx] if s in lat else np.nan,
            "time_spent_sec": np.round(dur).astype(int) if s != 8 else np.round(dur).astype(int),
            "drop_reason": reason,
        }))

        # --- next stage entry time -----------------------------------------------------------------
        nxt = idx[done]
        if s <= 7:
            p_imm = np.clip(.78 + .07 * (ch[nxt] == "Referral") - .23 * late[nxt], .3, .95)
            immediate = rng.random(len(nxt)) < p_imm
            gap = np.where(immediate, rng.lognormal(np.log(15), .5, len(nxt)),
                           np.minimum(rng.lognormal(np.log(6 * 3600), 1.3, len(nxt)), 14 * 86400))
        elif s == 8:
            gap = np.minimum(rng.lognormal(np.log(30 * 3600), 1.2, len(nxt)), 21 * 86400)
        else:
            gap = np.minimum(rng.lognormal(np.log(20 * 3600), 1.4, len(nxt)), 21 * 86400)
        t_new = t_enter.copy()
        t_new[nxt] = completed[done] + gap
        t_enter = t_new
        alive = np.zeros(n, dtype=bool)
        alive[nxt] = True

    ev = pd.concat(frames, ignore_index=True)
    ev["entered_at"] = pd.to_datetime(ev["entered_s"], unit="s")
    ev["completed_at"] = pd.to_datetime(ev["completed_s"], unit="s")
    ev["user_id"] = u["user_id"].to_numpy()[ev["user_idx"].to_numpy()]
    ev["stage_name"] = ev["stage_order"].map(STAGE_NAME)

    # Right-censoring at the extraction time
    ev = ev[ev["entered_at"] <= CUTOFF].copy()
    pending = ev["completed_at"] > CUTOFF
    ev.loc[pending, ["completed_at", "outcome", "drop_reason"]] = [pd.NaT, "IN_PROGRESS", None]

    ev = ev.sort_values(["user_id", "stage_order"]).reset_index(drop=True)
    ev.insert(0, "event_id", np.arange(1, len(ev) + 1))
    cols = ["event_id", "user_id", "stage_order", "stage_name", "entered_at", "completed_at", "outcome",
            "attempts", "system_latency_sec", "time_spent_sec", "drop_reason"]
    for c in ("entered_at", "completed_at"):
        ev[c] = ev[c].dt.strftime("%Y-%m-%d %H:%M:%S")
    return ev[cols]


def drop_reasons(rng, s, dm, idx, linked, late, bank, lat, fno, web):
    m = int(dm.sum())
    ids = idx[dm]
    out = np.empty(m, dtype=object)

    def fill(mask, labels, probs):
        k = int(mask.sum())
        if k:
            out[mask] = draw(rng, labels, probs, k)

    if s == 1:
        fill(np.ones(m, bool), ["OTP_NOT_RECEIVED", "EMAIL_VERIFICATION_ISSUE", "ABANDONED_NO_REASON"], [.45, .15, .40])
    elif s == 2:
        nl, lt = ~linked[ids], late[ids] & linked[ids]
        fill(nl, ["AADHAAR_MOBILE_NOT_LINKED", "DIGILOCKER_ERROR", "ABANDONED_NO_REASON"], [.70, .10, .20])
        fill(lt, ["DEFERRED_NEVER_RETURNED", "DIGILOCKER_TIMEOUT", "PAN_AADHAAR_NAME_MISMATCH", "ABANDONED_NO_REASON"], [.35, .15, .10, .40])
        fill(~nl & ~lt, ["DIGILOCKER_TIMEOUT", "PAN_AADHAAR_NAME_MISMATCH", "PAN_NOT_AVAILABLE", "OTP_NOT_RECEIVED", "ABANDONED_NO_REASON"], [.25, .15, .10, .10, .40])
    elif s == 3:
        slow = lat[3][ids] > 300
        coop = (bank[ids] == "Co-operative / other") & ~slow
        fill(slow, ["VERIFICATION_TIMEOUT", "PENNY_DROP_FAILED", "ABANDONED_NO_REASON"], [.5, .2, .3])
        fill(coop, ["BANK_NOT_SUPPORTED", "PENNY_DROP_FAILED", "BANK_NAME_MISMATCH", "ABANDONED_NO_REASON"], [.35, .25, .10, .30])
        fill(~slow & ~coop, ["PENNY_DROP_FAILED", "BANK_NAME_MISMATCH", "VERIFICATION_TIMEOUT", "ABANDONED_NO_REASON"], [.35, .20, .10, .35])
    elif s == 4:
        fill(np.ones(m, bool), ["NOMINEE_DETAILS_UNAVAILABLE", "TOO_MANY_FIELDS", "ABANDONED_NO_REASON"], [.30, .20, .50])
    elif s == 5:
        f = fno[ids]
        fill(f, ["INCOME_PROOF_UNAVAILABLE", "SEGMENT_CONFUSION", "ABANDONED_NO_REASON"], [.60, .10, .30])
        fill(~f, ["SEGMENT_CONFUSION", "ABANDONED_NO_REASON"], [.30, .70])
    elif s == 6:
        fill(np.ones(m, bool), ["SELFIE_FAILED_LIGHTING", "LIVENESS_CHECK_FAILED", "CAMERA_PERMISSION_DENIED", "ABANDONED_NO_REASON"], [.35, .20, .15, .30])
    elif s == 7:
        nl = ~linked[ids]
        fill(nl, ["PHYSICAL_SIGNATURE_COURIER_PENDING", "ABANDONED_NO_REASON"], [.65, .35])
        fill(~nl, ["ESIGN_OTP_FAILED", "BROKERAGE_CHARGES_CONCERN", "ABANDONED_NO_REASON"], [.45, .10, .45])
    elif s == 8:
        fill(np.ones(m, bool), ["KYC_REJECTED_NAME_MISMATCH", "KYC_REJECTED_POOR_DOCUMENT", "REJECTED_OTHER"], [.40, .30, .30])
    elif s == 9:
        fill(np.ones(m, bool), ["NO_FUNDS_TO_ADD", "UPI_PAYMENT_FAILED", "WAITING_FOR_MARKET_DIP", "ABANDONED_NO_REASON"], [.30, .15, .15, .40])
    else:
        fill(np.ones(m, bool), ["NO_TRADING_IDEA", "PLATFORM_COMPLEXITY", "ABANDONED_NO_REASON"], [.30, .25, .45])
    return out


def main():
    rng = np.random.default_rng(SEED)
    users = build_users(rng)
    events = build_events(rng, users)
    DATA_DIR.mkdir(exist_ok=True)
    out_users = users.copy()
    out_users["signup_ts"] = out_users["signup_ts"].dt.strftime("%Y-%m-%d %H:%M:%S")
    out_users.to_csv(DATA_DIR / "users.csv", index=False)
    events.to_csv(DATA_DIR / "funnel_events.csv", index=False)
    print(f"users: {len(users):,} | events: {len(events):,}")
    print(events.groupby("stage_order")["outcome"].value_counts().unstack(fill_value=0))


if __name__ == "__main__":
    main()
