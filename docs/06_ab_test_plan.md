# A/B Test Plan

The impact model assumes each fix closes half of its conversion gap. These experiments test that assumption before full rollout.

## Design rules (all experiments)
- Randomise by `user_id` hash, 50 / 50, with the assignment fixed for each user.
- Significance level 5% (two-sided), power 80%; sample size from the two-proportion formula.
- Check sample-ratio mismatch daily; fix the duration up front and do not stop early on a good-looking result.
- Primary metric decides; guardrails must not worsen beyond the agreed limit; Compliance reviews variants before launch.
- Run a full business cycle (at least 14 days) so weekday and weekend behaviour is covered.

## Experiments

| ID | Lever | Audience | Baseline | Minimum effect to detect | Sample per arm | Eligible users per day | Estimated duration |
|---|---|---|---|---|---|---|---|
| EXP-1 | L2 | Users with PNB, Bank of Baroda or co-operative / other banks reaching the bank step | 67.4% | +9.3 pp | 367 | 26 | 29 days |
| EXP-2 | L5 | All activated, unfunded users | 58.0% | +8.0 pp | 577 | 39 | 30 days |
| EXP-3 | L6 | Users who select F&O at the segment step | 83.1% | +7.0 pp | 371 | 18 | 42 days |
| EXP-4 | L1a | Users with Aadhaar not linked to mobile (limited pilot after Compliance approval) | 33.3% | +21.0 pp | 87 | 14 | 13 days |

### EXP-1: Bank-verification fallback (L2)
- **Hypothesis:** Offering UPI / cheque fallback after 60 s raises bank-step completion.
- **Variants:** A: current flow | B: fallback after 60 s.
- **Primary metric:** Bank-step completion.
- **Guardrails:** Account name-mismatch rate; manual-review backlog.
- **Sample size:** 367 users per arm at baseline 67.4% and a 9.3 point lift; about 29 days at 26 eligible users per day.

### EXP-2: Funding nudge journey (L5)
- **Hypothesis:** A one-tap UPI screen plus day 1, 3, 7 nudges raises first funding.
- **Variants:** A: no nudges | B: one-tap UPI + nudges.
- **Primary metric:** First funding within 14 days.
- **Guardrails:** Opt-out / complaint rate; unsubscribe rate.
- **Sample size:** 577 users per arm at baseline 58.0% and a 8.0 point lift; about 30 days at 39 eligible users per day.

### EXP-3: Defer income proof (L6)
- **Hypothesis:** Allowing cash segments first raises completion of the segment step without hurting later F&O proof submission.
- **Variants:** A: income proof required | B: cash first, proof later.
- **Primary metric:** Segment-step completion.
- **Guardrails:** Share who add F&O proof within 30 days; account rejection rate.
- **Sample size:** 371 users per arm at baseline 83.1% and a 7.0 point lift; about 42 days at 18 eligible users per day.

### EXP-4: Alternative KYC pilot (L1a)
- **Hypothesis:** An alternative path raises KYC completion for unlinked users.
- **Variants:** A: current offline flow | B: alternative path.
- **Primary metric:** KYC-step completion.
- **Guardrails:** Mismatch / fraud flags; manual-review time.
- **Sample size:** 87 users per arm at baseline 33.3% and a 21.0 point lift; about 13 days at 14 eligible users per day.

## Reading the durations
- Durations are driven by traffic. Stages that few users reach take longer, which is why EXP-2 uses all activated users and a larger lift, and why EXP-3 uses a lift of 7 points (the deferral removes the step for cash segments, so a large effect is plausible) and still needs weeks.
- If a duration is too long for the business, options are to widen the audience, test a bigger change, or accept a lower power; each trades certainty for speed and should be a stated decision.
- EXP-4 needs Compliance approval first and starts as a limited pilot.

## Decision rule
- **Ship** if the primary metric improves with p < 0.05 and no guardrail worsens beyond its limit.
- **Iterate** if the direction is positive but not significant; extend only if the power calculation allows it.
- **Stop** if a guardrail breaks or the effect is negative.
- After each ship decision, replace the assumption in `excel/Onboarding_Impact_Model.xlsx` (row 'Share of the conversion gap closed') with the measured value.