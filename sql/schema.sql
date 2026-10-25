-- Onboarding funnel schema (MySQL 8+). Star-style: 3 dimensions + 1 event fact table.
CREATE DATABASE IF NOT EXISTS broker_onboarding;
USE broker_onboarding;

DROP TABLE IF EXISTS fact_funnel_events;
DROP TABLE IF EXISTS dim_users;
DROP TABLE IF EXISTS dim_stage;
DROP TABLE IF EXISTS dim_reason;

CREATE TABLE dim_stage (
    stage_order INT          NOT NULL PRIMARY KEY,
    stage_name  VARCHAR(60)  NOT NULL,
    stage_short VARCHAR(20)  NOT NULL
);

CREATE TABLE dim_reason (
    drop_reason     VARCHAR(60) NOT NULL PRIMARY KEY,
    reason_category VARCHAR(40) NOT NULL
);

CREATE TABLE dim_users (
    user_id               VARCHAR(10) NOT NULL PRIMARY KEY,
    signup_ts             DATETIME    NOT NULL,
    signup_date           DATE        NOT NULL,
    signup_hour           TINYINT     NOT NULL,
    channel               VARCHAR(30) NOT NULL,
    device_os             VARCHAR(10) NOT NULL,
    device_tier           VARCHAR(15) NOT NULL,
    city_tier             VARCHAR(10) NOT NULL,
    age                   TINYINT     NOT NULL,
    age_group             VARCHAR(10) NOT NULL,
    bank                  VARCHAR(30) NOT NULL,
    aadhaar_mobile_linked TINYINT     NOT NULL,
    kyc_path              VARCHAR(25) NOT NULL,
    seeks_fno             TINYINT     NOT NULL,
    campaign_day_type     VARCHAR(30) NOT NULL,
    INDEX idx_signup_date (signup_date)
);

CREATE TABLE fact_funnel_events (
    event_id           INT         NOT NULL PRIMARY KEY,
    user_id            VARCHAR(10) NOT NULL,
    stage_order        INT         NOT NULL,
    entered_at         DATETIME    NOT NULL,
    completed_at       DATETIME    NULL,
    outcome            VARCHAR(15) NOT NULL,
    attempts           TINYINT     NOT NULL,
    system_latency_sec DECIMAL(10,1) NULL,
    time_spent_sec     INT         NOT NULL,
    drop_reason        VARCHAR(60) NULL,
    UNIQUE KEY uq_user_stage (user_id, stage_order),
    INDEX idx_stage_outcome (stage_order, outcome),
    CONSTRAINT fk_ev_user  FOREIGN KEY (user_id)     REFERENCES dim_users (user_id),
    CONSTRAINT fk_ev_stage FOREIGN KEY (stage_order) REFERENCES dim_stage (stage_order)
);
