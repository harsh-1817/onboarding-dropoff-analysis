# Power BI dashboard build guide

Build time: about 90 minutes. Save as `dashboard/onboarding_dropoff_dashboard.pbix` and export one screenshot per page into `dashboard/screenshots/`.

## 1. Load the data
**Home > Get data > Text/CSV**, one file at a time (not "Folder"), then **Close & Apply**:

| File | Table name | Used for |
|---|---|---|
| `data/users.csv` | `users` | one row per sign-up with segment attributes |
| `data/funnel_events.csv` | `funnel_events` | one row per user per stage entered |
| `data/processed/dim_stage.csv` | `dim_stage` | stage names and order |
| `data/processed/drop_reason_categories.csv` | `drop_reason_categories` | reason Pareto |
| `data/processed/drop_reasons_by_stage.csv` | `drop_reasons_by_stage` | top reasons per stage |
| `data/processed/latency_analysis.csv` | `latency_analysis` | response time vs completion |
| `data/processed/retry_analysis.csv` | `retry_analysis` | attempts vs completion |
| `data/processed/stage_timing.csv` | `stage_timing` | median time per stage |
| `data/processed/lever_sizing.csv` | `lever_sizing` | opportunity table |
| `data/processed/weekly_trend.csv` | `weekly_trend` | weekly cohorts |

In Power Query check types: `signup_ts`, `entered_at`, `completed_at` = Date/Time; `signup_date` = Date; counts = Whole number; rates = Decimal.

## 2. Model
1. Open **Model view**.
2. Relate `users[user_id]` (one) to `funnel_events[user_id]` (many), single direction.
3. Relate `dim_stage[stage_order]` (one) to `funnel_events[stage_order]` (many), single direction.
4. In `dim_stage`, select `stage_short` and set **Sort by column** to `stage_order` so stages never sort alphabetically.
5. Leave the processed tables unrelated; they are small standalone summaries.

In Data view, select `users` and add one calculated column (**New column**):
```DAX
Signup Time Band =
SWITCH (
    TRUE (),
    users[signup_hour] >= 22 || users[signup_hour] < 6, "Late night (22-05)",
    users[signup_hour] < 12, "Morning (06-11)",
    users[signup_hour] < 18, "Afternoon (12-17)",
    "Evening (18-21)"
)
```

## 3. Measures
Select `funnel_events`, **New measure**, add each:
```DAX
Sign-ups = CALCULATE ( COUNTROWS ( funnel_events ), funnel_events[stage_order] = 1, REMOVEFILTERS ( dim_stage ) )
Entered = COUNTROWS ( funnel_events )
Completed = CALCULATE ( COUNTROWS ( funnel_events ), funnel_events[outcome] = "COMPLETED" )
Dropped = [Entered] - [Completed]
Step Conversion % = DIVIDE ( [Completed], [Entered] )
Cumulative % of Sign-ups = DIVIDE ( [Completed], [Sign-ups] )
Lost % of Sign-ups = DIVIDE ( [Dropped], [Sign-ups] )

Activated =
CALCULATE ( COUNTROWS ( funnel_events ), funnel_events[stage_order] = 8,
            funnel_events[outcome] = "COMPLETED", REMOVEFILTERS ( dim_stage ) )
Funded =
CALCULATE ( COUNTROWS ( funnel_events ), funnel_events[stage_order] = 9,
            funnel_events[outcome] = "COMPLETED", REMOVEFILTERS ( dim_stage ) )
Activation Rate = DIVIDE ( [Activated], [Sign-ups] )
Funded Rate = DIVIDE ( [Funded], [Sign-ups] )

Unknown Reason Share =
DIVIDE (
    CALCULATE ( COUNTROWS ( funnel_events ), funnel_events[drop_reason] = "ABANDONED_NO_REASON" ),
    CALCULATE ( COUNTROWS ( funnel_events ), funnel_events[outcome] = "DROPPED" )
)
Median Minutes in Stage =
MEDIANX ( FILTER ( funnel_events, funnel_events[outcome] = "COMPLETED" ), funnel_events[time_spent_sec] ) / 60
```
Format the `%` measures as Percentage with 1 decimal.

## 4. Pages

**Page 1: Funnel overview** (title: *"Only 3 in 10 sign-ups get an account; KYC and funding lose the most"*)
- Cards: Sign-ups, Activation Rate, Funded Rate, Unknown Reason Share.
- **Funnel** visual: Category `dim_stage[stage_short]`, Values `[Entered]`.
- Clustered bar: `stage_short` vs `[Lost % of Sign-ups]`; colour the top two bars red.
- Slicers: `users[channel]`, `users[device_os]`, `users[city_tier]`, `users[kyc_path]`, `users[signup_date]` (between).

**Page 2: Segment explorer** (title: *"Who converts, and where do others fall away?"*)
- **Matrix:** Rows `users[channel]`; Columns `dim_stage[stage_short]`; Values `[Step Conversion %]`. Conditional formatting (Cell elements > Background color > Rules): below 65% red, 65-85% amber, above 85% green.
- Create a **field parameter** (Modeling > New parameter > Fields) with `channel`, `device_tier`, `city_tier`, `age_group`, `bank`, `kyc_path`, `Signup Time Band`; use it as the matrix rows so one visual explores every segment.
- Slicer: stage (to focus on KYC or bank).

**Page 3: Why users drop** (title: *"A third of drop-offs have no recorded reason"*)
- Bar: `drop_reason_categories[reason_category]` vs `users`, sorted descending; grey for the "Unknown" bar.
- Table: `drop_reasons_by_stage` (stage_short, drop_reason, users, pct_of_stage_drops) with a stage slicer.
- Stacked column: stage vs users by category.

**Page 4: Speed and friction** (title: *"Slow bank responses and repeated attempts predict abandonment"*)
- Column chart: `latency_analysis` filtered to stage_short = Bank; Axis `label`, Values `completion_rate`.
- Line chart: `retry_analysis` filtered to Selfie/IPV and KYC; Axis `attempts`, Values `completion_rate`, Legend `stage_short`.
- Bar: `stage_timing[stage_short]` vs `median_minutes`.
- Line: `weekly_trend[week]` vs `activation_rate` and `funded_rate`.

**Page 5: Opportunities** (title: *"Where fixing the funnel pays back most"*)
- Table from `lever_sizing`: `lever_id`, `segment_definition`, `stage_short`, `seg_conv`, `rest_conv`, `gap_pp`, `excess_lost_vs_rest`; data bars on `excess_lost_vs_rest`.
- Text box: summary from `excel/Onboarding_Impact_Model.xlsx` (base case: extra funded accounts per month and rank by priority score).
- Text box: *"Segment size is not priority: effort and downstream conversion change the order."*

## 5. Design tips
- Titles state the finding, not the metric name. Same colours for the same meaning on every page (red = leak, blue = normal, grey = unknown).
- Hide gridlines, align visuals to the grid, keep fonts to Segoe UI.
- Add a footer on every page: *"Synthetic data for a case study"*.
- Export: **File > Export > PDF**, and screenshot each page with Win + Shift + S into `dashboard/screenshots/` as `page1_funnel.png`, `page2_segments.png`, `page3_reasons.png`, `page4_speed.png`, `page5_opportunities.png`.
