# Why do 7 in 10 people who start opening a trading account never get one?

A business-analysis case study on **digital account-opening drop-off** at a stockbroker: data analysis (SQL, Python), a full set of BA documents (BRD, user stories, process flows, traceability, UAT, A/B test plan), an Excel impact model and a Power BI dashboard.

> **Synthetic data.** The dataset is simulated (`src/generate_dataset.py`) with documented assumptions about how Indian digital onboarding works (DigiLocker KYC, bank penny-drop, selfie / IPV, Aadhaar e-Sign). No company data is used. The point is the method: finding the leak, sizing it, specifying the fix and planning how to prove it.

![Onboarding funnel](dashboard/charts/01_onboarding_funnel.png)

## The business problem
Of **20,000** people who started opening an account between 1 April and 31 August 2026, only **5,964 (29.8%)** were activated, **3,462 (17.3%)** funded their account and **2,428 (12.1%)** placed a first trade. Every lost sign-up is wasted acquisition spend. Where exactly are they lost, why, and what should the product team build first?

## Key findings
1. **Three steps cause 59.2% of all drop-offs:** KYC (5,385 users lost), bank verification (2,515) and first funding (2,502).
2. **Aadhaar not linked to the mobile is the biggest single cause.** These users are 12.0% of sign-ups but convert at **33.3%** at KYC against **75.2%** for the rest, and only 12.4% of them are ever activated (vs 32.2%). They also take a median 71 hours to activate vs 39.
3. **Slow bank verification kills completion:** 56.7% when the bank takes over 5 minutes vs 86.3% under 30 seconds. Co-operative banks (63.6%) and PNB (68.5%) are the weakest.
4. **Late-night starters do not come back:** KYC conversion 61.9% vs 71.7% for morning sign-ups.
5. **Weaker devices struggle at the selfie step:** 79.6% on low-end Android and 83.9% on web vs 91.4% on iOS.
6. **F&O seekers drop at income proof** (83.1% vs 93.6% for cash-only users); **influencer-sourced users rarely fund** (50.1% vs 67.7% for referrals).
7. **The business is blind to 36.8% of its drop-offs**, because no reason is captured. Measurement is a requirement, not a nice-to-have.

![Where users are lost](dashboard/charts/02_users_lost_by_stage.png)
![Segment heatmap](dashboard/charts/03_segment_heatmap.png)

## Dashboard
A five-page Power BI report ([`dashboard/onboarding_dropoff_dashboard.pbix`](dashboard/onboarding_dropoff_dashboard.pbix)); design, data model and DAX are in [`dashboard/POWERBI_GUIDE.md`](dashboard/POWERBI_GUIDE.md).

**1. Funnel overview:** where sign-ups are lost, with slicers for channel, device, city tier, KYC path and date.
![Funnel overview](dashboard/screenshots/page1_funnel.png)

**2. Segment explorer:** step conversion for any segment, coloured by the gap against the stage average.
![Segment explorer](dashboard/screenshots/page2_segments.png)

**3. Why users drop:** reason categories and the top reasons at each stage.
![Why users drop](dashboard/screenshots/page3_reasons.png)

**4. Speed and friction:** bank response time, retries, time in stage and weekly cohorts.
![Speed and friction](dashboard/screenshots/page4_speed.png)

**5. Opportunities:** the seven improvement levers sized against a like-for-like benchmark.
![Opportunities](dashboard/screenshots/page5_opportunities.png)

*To open the `.pbix` on another machine, update the file paths in Power BI: Transform data > Data source settings > Change source, and point each CSV to this repo's `data/` folder.*

## What I recommend and what it is worth
Seven improvements were sized with a transparent Excel model (`excel/Onboarding_Impact_Model.xlsx`). Ranking uses *incremental funded accounts x confidence / effort*, so the biggest gap is not automatically first.

| Priority | Lever | Segment | Stage | Conversion gap | Extra funded accounts / month (base, before overlap haircut) |
|---|---|---|---|---|---|
| 1 | L2 | PNB, Bank of Baroda, Co-operative / other | Bank | 19 pp | 25.0 |
| 2 | L5 | Influencer / YouTube and Meta / social ads | Funding | 11 pp | 15.7 |
| 3 | L6 | Wants F&O | Segments | 10 pp | 11.8 |
| 4 | L1a | Aadhaar not linked to mobile | KYC | 42 pp | 25.2 |
| 5 | L4 | Low-end Android, web or age 55+ | Selfie/IPV | 7 pp | 11.1 |
| 6 | L3 | Signed up 22:00-05:59 (DigiLocker-eligible) | KYC | 9 pp | 4.1 |
| 7 | L1b | Aadhaar not linked to mobile | e-Sign | 14 pp | 3.3 |

The levers sum to about 96 extra funded accounts a month; because they reach overlapping users, the model applies a 20% haircut.

**Base case:** about **+77 funded accounts per month (+11.1%)** after the haircut; range **+5.6% to +16.7%**. First-year revenue in the base case is about **Rs 18.5 lakh** using a *placeholder* revenue-per-account (Rs 2,000); effort and confidence figures are also placeholders that must be replaced with finance and engineering estimates.

![Opportunity sizing](dashboard/charts/07_opportunity_sizing.png)

## Deliverables
| Area | File | What it shows |
|---|---|---|
| Requirements | [`docs/01_BRD.md`](docs/01_BRD.md) | Objectives, scope, RACI, evidence, 7 business / 21 functional / 8 non-functional requirements, KPIs, risks, release plan |
| Agile | [`docs/02_user_stories.md`](docs/02_user_stories.md) | 19 stories in 7 epics with Given / When / Then acceptance criteria |
| Process | [`docs/03_process_flows.md`](docs/03_process_flows.md) | As-is and to-be flows, status model, bank-fallback sequence (Mermaid) |
| Traceability | [`docs/04_traceability_matrix.md`](docs/04_traceability_matrix.md) | Finding to requirement to story to test to KPI |
| Testing | [`docs/05_uat_test_plan.md`](docs/05_uat_test_plan.md) | 30 UAT cases with entry / exit criteria |
| Experimentation | [`docs/06_ab_test_plan.md`](docs/06_ab_test_plan.md) | 4 experiments with hypotheses, guardrails and sample-size maths |
| Analysis | [`sql/`](sql/), [`src/analysis.py`](src/analysis.py) | Schema, 13 SQL queries (window functions, CTEs), Python funnel analysis |
| Business case | [`excel/Onboarding_Impact_Model.xlsx`](excel/Onboarding_Impact_Model.xlsx) | Live-formula model with 3 scenarios and a priority ranking |
| Dashboard | [`dashboard/onboarding_dropoff_dashboard.pbix`](dashboard/onboarding_dropoff_dashboard.pbix) | 5-page Power BI report (design and DAX in [`POWERBI_GUIDE.md`](dashboard/POWERBI_GUIDE.md)) |
| Findings | [`docs/key_findings.md`](docs/key_findings.md) | Auto-generated numbers |

## Supporting analysis
![Drop-off reasons](dashboard/charts/04_drop_reasons.png)
![Bank latency](dashboard/charts/08_bank_latency.png)
![Time to activation](dashboard/charts/06_time_to_activation.png)

## How the data was built (and why you can trust the analysis)
- 20,000 sign-ups, 101,619 funnel events across 10 stages, extracted 15 Oct 2026.
- Each stage's completion is a logistic function of channel, device, city tier, age, bank, Aadhaar-mobile linkage, signup hour and system response time, plus a per-user intent effect. Stage intercepts are calibrated so the overall funnel matches a target, so the **segment differences carry the insight**.
- 10 integrity tests (`tests/test_dataset_integrity.py`) check sequence, timestamps and outcomes. They caught a real bug during the build (timestamps in 1970 caused by a pandas 3 timestamp-unit change), which is why they exist.
- 5 analysis tests check that segment counts add up to the overall funnel and that lever sizing is consistent.

## How to run
```bash
git clone https://github.com/harsh-1817/onboarding-dropoff-analysis.git
cd onboarding-dropoff-analysis
pip install -r requirements.txt

python src/generate_dataset.py     # optional: the data is already in data/ (seeded, reproducible)
python src/analysis.py             # funnel analysis, charts, CSVs, docs/key_findings.md
python src/build_excel.py          # Excel impact model
pytest                             # 15 tests
```
Optional MySQL layer:
```powershell
$env:DB_URL="mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/broker_onboarding"   # encode @ in the password as %40
python src/load_to_mysql.py
# then run sql/analysis_queries.sql in MySQL Workbench
```

## Limitations
- **Synthetic data:** real behaviour is messier. Treat the numbers as a worked example, not a benchmark.
- **Placeholders:** revenue per account, effort and confidence are assumptions to be replaced; the ranking can change.
- **Correlation, not causation:** segment gaps suggest where to intervene; the A/B plan is how the effect is proven. The lower completion seen after repeated attempts is likewise an association (users who keep failing are the ones who give up).
- **Survivorship:** conversion at later stages is influenced by who survived earlier ones (e.g. 55+ users reaching the bank step convert unusually well), so each lever is sized at the stage where its problem arises, against a like-for-like benchmark.
- **Compliance:** alternative KYC and signature paths depend on what the regulator and the firm's Compliance team permit.

## Skills demonstrated
Business analysis (BRD, user stories, acceptance criteria, RACI, traceability, UAT planning, process modelling) - funnel and cohort analysis - SQL (CTEs, window functions) - Python (pandas, matplotlib, pytest) - Excel financial modelling with live formulas and scenarios - Power BI design and DAX - A/B test design and sample-size calculation - prioritisation (MoSCoW, effort-adjusted scoring).

## Author
**Harsh Trivedi**  
**MBA (Computer Management) | Data Analytics & Financial Markets**

**Certifications:** NISM Research Analyst (Series XV) · NISM Equity Derivatives (Series VIII)
