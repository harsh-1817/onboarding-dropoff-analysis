-- ============================================================================
-- Investor onboarding drop-off analysis (MySQL 8+)
-- Run after: python src/load_to_mysql.py
-- ============================================================================
USE broker_onboarding;

-- ----------------------------------------------------------------------------
-- Q1. Overall funnel: users entering and completing each stage, step and cumulative conversion
-- ----------------------------------------------------------------------------
SELECT  s.stage_order,
        s.stage_name,
        COUNT(*)                                                             AS entered,
        SUM(e.outcome = 'COMPLETED')                                         AS completed,
        SUM(e.outcome = 'DROPPED')                                           AS dropped,
        ROUND(100 * SUM(e.outcome = 'COMPLETED') / COUNT(*), 1)              AS step_conversion_pct,
        ROUND(100 * SUM(e.outcome = 'COMPLETED') / (SELECT COUNT(*) FROM dim_users), 1) AS cumulative_pct_of_signups
FROM    fact_funnel_events e
JOIN    dim_stage s ON s.stage_order = e.stage_order
GROUP BY s.stage_order, s.stage_name
ORDER BY s.stage_order;

-- ----------------------------------------------------------------------------
-- Q2. Where is the biggest leak? Rank stages by users lost
-- ----------------------------------------------------------------------------
WITH f AS (
    SELECT stage_order, SUM(outcome = 'DROPPED') AS lost
    FROM   fact_funnel_events
    GROUP BY stage_order
)
SELECT  s.stage_name, f.lost,
        ROUND(100 * f.lost / (SELECT COUNT(*) FROM dim_users), 1)      AS lost_pct_of_signups,
        ROUND(100 * f.lost / SUM(f.lost) OVER (), 1)                   AS share_of_all_drop_offs,
        RANK() OVER (ORDER BY f.lost DESC)                             AS leak_rank
FROM    f JOIN dim_stage s ON s.stage_order = f.stage_order
ORDER BY leak_rank;

-- ----------------------------------------------------------------------------
-- Q3. KYC conversion by KYC path and signup time band (and gap vs overall KYC conversion)
-- ----------------------------------------------------------------------------
WITH kyc AS (
    SELECT  u.kyc_path,
            CASE WHEN u.signup_hour >= 22 OR u.signup_hour < 6 THEN 'Late night (22-05)'
                 WHEN u.signup_hour < 12 THEN 'Morning (06-11)'
                 WHEN u.signup_hour < 18 THEN 'Afternoon (12-17)'
                 ELSE 'Evening (18-21)' END                              AS time_band,
            e.outcome
    FROM    fact_funnel_events e
    JOIN    dim_users u ON u.user_id = e.user_id
    WHERE   e.stage_order = 2
)
SELECT  kyc_path, time_band,
        COUNT(*)                                                        AS entered_kyc,
        ROUND(100 * AVG(outcome = 'COMPLETED'), 1)                      AS kyc_conversion_pct,
        ROUND(100 * AVG(outcome = 'COMPLETED')
              - 100 * AVG(AVG(outcome = 'COMPLETED')) OVER (), 1)       AS gap_vs_avg_of_segments_pp
FROM    kyc
GROUP BY kyc_path, time_band
ORDER BY kyc_conversion_pct;

-- ----------------------------------------------------------------------------
-- Q4. Bank verification: conversion by bank with gap vs overall, and verification speed
-- ----------------------------------------------------------------------------
SELECT  u.bank,
        COUNT(*)                                                         AS entered_bank_step,
        ROUND(100 * AVG(e.outcome = 'COMPLETED'), 1)                     AS conversion_pct,
        ROUND(100 * AVG(e.outcome = 'COMPLETED')
              - 100 * (SELECT AVG(outcome = 'COMPLETED') FROM fact_funnel_events WHERE stage_order = 3), 1) AS gap_vs_overall_pp,
        ROUND(AVG(e.system_latency_sec), 0)                              AS avg_penny_drop_sec,
        ROUND(100 * AVG(e.system_latency_sec > 120), 1)                  AS pct_slower_than_2min
FROM    fact_funnel_events e
JOIN    dim_users u ON u.user_id = e.user_id
WHERE   e.stage_order = 3
GROUP BY u.bank
ORDER BY conversion_pct;

-- ----------------------------------------------------------------------------
-- Q5. Does slow bank verification cause abandonment? Completion by response-time bucket
-- ----------------------------------------------------------------------------
SELECT  CASE WHEN system_latency_sec < 30  THEN '1) under 30s'
             WHEN system_latency_sec < 120 THEN '2) 30-120s'
             WHEN system_latency_sec < 300 THEN '3) 2-5 min'
             ELSE '4) over 5 min' END                                    AS verification_time,
        COUNT(*)                                                          AS users,
        ROUND(100 * AVG(outcome = 'COMPLETED'), 1)                        AS completion_pct
FROM    fact_funnel_events
WHERE   stage_order = 3
GROUP BY verification_time
ORDER BY verification_time;

-- ----------------------------------------------------------------------------
-- Q6. Drop-off reason Pareto with running cumulative share
-- ----------------------------------------------------------------------------
WITH r AS (
    SELECT  e.drop_reason, d.reason_category, COUNT(*) AS users
    FROM    fact_funnel_events e
    JOIN    dim_reason d ON d.drop_reason = e.drop_reason
    WHERE   e.outcome = 'DROPPED'
    GROUP BY e.drop_reason, d.reason_category
)
SELECT  drop_reason, reason_category, users,
        ROUND(100 * users / SUM(users) OVER (), 1)                                         AS share_pct,
        ROUND(100 * SUM(users) OVER (ORDER BY users DESC, drop_reason) / SUM(users) OVER (), 1) AS cumulative_share_pct
FROM    r
ORDER BY users DESC, drop_reason;

-- ----------------------------------------------------------------------------
-- Q7. Top reason in each stage (ROW_NUMBER over reason counts)
-- ----------------------------------------------------------------------------
WITH r AS (
    SELECT  stage_order, drop_reason, COUNT(*) AS users,
            ROW_NUMBER() OVER (PARTITION BY stage_order ORDER BY COUNT(*) DESC) AS rn
    FROM    fact_funnel_events
    WHERE   outcome = 'DROPPED'
    GROUP BY stage_order, drop_reason
)
SELECT  s.stage_name, r.drop_reason, r.users,
        ROUND(100 * r.users / SUM(r.users) OVER (PARTITION BY r.stage_order), 1) AS pct_of_stage_drops
FROM    r JOIN dim_stage s ON s.stage_order = r.stage_order
WHERE   r.rn <= 2
ORDER BY r.stage_order, r.rn;

-- ----------------------------------------------------------------------------
-- Q8. Median time spent per stage (completed events), using window functions
-- ----------------------------------------------------------------------------
WITH t AS (
    SELECT  stage_order, time_spent_sec,
            ROW_NUMBER() OVER (PARTITION BY stage_order ORDER BY time_spent_sec) AS rn,
            COUNT(*)     OVER (PARTITION BY stage_order)                         AS cnt
    FROM    fact_funnel_events
    WHERE   outcome = 'COMPLETED'
)
SELECT  s.stage_name,
        ROUND(AVG(t.time_spent_sec) / 60, 1) AS median_minutes
FROM    t JOIN dim_stage s ON s.stage_order = t.stage_order
WHERE   t.rn IN (FLOOR((t.cnt + 1) / 2), CEIL((t.cnt + 1) / 2))
GROUP BY s.stage_order, s.stage_name
ORDER BY s.stage_order;

-- ----------------------------------------------------------------------------
-- Q9. Time from signup to activation, by KYC path (distribution buckets)
-- ----------------------------------------------------------------------------
WITH a AS (
    SELECT  u.kyc_path,
            TIMESTAMPDIFF(HOUR, u.signup_ts, e.completed_at) AS hours_to_activate
    FROM    fact_funnel_events e
    JOIN    dim_users u ON u.user_id = e.user_id
    WHERE   e.stage_order = 8 AND e.outcome = 'COMPLETED'
)
SELECT  kyc_path,
        COUNT(*)                                                 AS activated,
        ROUND(100 * AVG(hours_to_activate <= 24), 1)             AS pct_within_1_day,
        ROUND(100 * AVG(hours_to_activate > 24  AND hours_to_activate <= 72), 1) AS pct_1_to_3_days,
        ROUND(100 * AVG(hours_to_activate > 72), 1)              AS pct_over_3_days,
        ROUND(AVG(hours_to_activate), 0)                         AS avg_hours
FROM    a
GROUP BY kyc_path;

-- ----------------------------------------------------------------------------
-- Q10. How long do users wait before coming back? Gap between finishing a stage and starting the next
--      (LEAD over the user's stages) - long gaps signal users who need a reminder
-- ----------------------------------------------------------------------------
WITH g AS (
    SELECT  user_id, stage_order, completed_at,
            LEAD(entered_at) OVER (PARTITION BY user_id ORDER BY stage_order) AS next_entered
    FROM    fact_funnel_events
    WHERE   outcome = 'COMPLETED'
)
SELECT  stage_order,
        COUNT(next_entered)                                                    AS continued,
        ROUND(100 * AVG(TIMESTAMPDIFF(MINUTE, completed_at, next_entered) > 60), 1) AS pct_resumed_after_1h,
        ROUND(AVG(TIMESTAMPDIFF(MINUTE, completed_at, next_entered)) / 60, 1)  AS avg_gap_hours
FROM    g
WHERE   next_entered IS NOT NULL AND stage_order <= 7
GROUP BY stage_order
ORDER BY stage_order;

-- ----------------------------------------------------------------------------
-- Q11. Weekly sign-up cohorts: volume and conversion to activation and funding
-- ----------------------------------------------------------------------------
WITH c AS (
    SELECT  u.user_id,
            DATE_SUB(u.signup_date, INTERVAL WEEKDAY(u.signup_date) DAY) AS week_start,
            MAX(CASE WHEN e.stage_order = 8 AND e.outcome = 'COMPLETED' THEN 1 ELSE 0 END) AS activated,
            MAX(CASE WHEN e.stage_order = 9 AND e.outcome = 'COMPLETED' THEN 1 ELSE 0 END) AS funded
    FROM    dim_users u
    JOIN    fact_funnel_events e ON e.user_id = u.user_id
    GROUP BY u.user_id, week_start
)
SELECT  week_start, COUNT(*) AS signups,
        ROUND(100 * AVG(activated), 1) AS activation_pct,
        ROUND(100 * AVG(funded), 1)    AS funded_pct
FROM    c
GROUP BY week_start
ORDER BY week_start;

-- ----------------------------------------------------------------------------
-- Q12. Retries: does needing several attempts predict abandonment? (selfie / IPV and KYC)
-- ----------------------------------------------------------------------------
SELECT  s.stage_name, e.attempts,
        COUNT(*)                                       AS users,
        ROUND(100 * AVG(e.outcome = 'COMPLETED'), 1)   AS completion_pct
FROM    fact_funnel_events e
JOIN    dim_stage s ON s.stage_order = e.stage_order
WHERE   e.stage_order IN (2, 6)
GROUP BY s.stage_order, s.stage_name, e.attempts
ORDER BY s.stage_order, e.attempts;

-- ----------------------------------------------------------------------------
-- Q13. Channel quality: sign-ups, activation and funding rate per acquisition channel
-- ----------------------------------------------------------------------------
WITH u AS (
    SELECT  d.channel, d.user_id,
            MAX(CASE WHEN e.stage_order = 8 AND e.outcome = 'COMPLETED' THEN 1 ELSE 0 END) AS activated,
            MAX(CASE WHEN e.stage_order = 9 AND e.outcome = 'COMPLETED' THEN 1 ELSE 0 END) AS funded
    FROM    dim_users d JOIN fact_funnel_events e ON e.user_id = d.user_id
    GROUP BY d.channel, d.user_id
)
SELECT  channel, COUNT(*) AS signups,
        ROUND(100 * AVG(activated), 1) AS activation_pct,
        ROUND(100 * AVG(funded), 1)    AS funded_pct,
        RANK() OVER (ORDER BY AVG(funded) DESC) AS funded_rank
FROM    u
GROUP BY channel
ORDER BY funded_rank;
