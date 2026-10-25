"""Load the dataset into MySQL (schema in sql/schema.sql).

Run:  python src/load_to_mysql.py
Set DB_URL first, e.g. (PowerShell)  $env:DB_URL="mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/broker_onboarding"
Remember to URL-encode special characters in the password (@ becomes %40).
"""
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from config import DATA_DIR, DB_NAME, DB_URL, REASON_CATEGORY, SQL_DIR, STAGES


def main():
    url = make_url(DB_URL)
    with create_engine(url.set(database="mysql")).begin() as conn:      # built-in system DB
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"))
    engine = create_engine(url)

    script = "\n".join(l for l in (SQL_DIR / "schema.sql").read_text().splitlines() if not l.strip().startswith("--"))
    with engine.begin() as conn:
        for stmt in filter(None, (s.strip() for s in script.split(";"))):
            if not stmt.upper().startswith(("CREATE DATABASE", "USE ")):
                conn.execute(text(stmt))

    users = pd.read_csv(DATA_DIR / "users.csv")
    users["signup_ts"] = pd.to_datetime(users["signup_ts"])
    events = pd.read_csv(DATA_DIR / "funnel_events.csv", parse_dates=["entered_at", "completed_at"]).drop(columns=["stage_name"])
    stages = pd.DataFrame(STAGES, columns=["stage_order", "stage_name", "stage_short"])
    reasons = pd.DataFrame(list(REASON_CATEGORY.items()), columns=["drop_reason", "reason_category"])

    kw = dict(if_exists="append", index=False, chunksize=5000, method="multi")
    stages.to_sql("dim_stage", engine, **kw)
    reasons.to_sql("dim_reason", engine, **kw)
    users.to_sql("dim_users", engine, **kw)
    events.to_sql("fact_funnel_events", engine, **kw)
    print(f"Loaded {len(users):,} users and {len(events):,} funnel events into {DB_NAME}")


if __name__ == "__main__":
    main()
