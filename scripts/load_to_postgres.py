import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv, find_dotenv
import urllib.parse

load_dotenv(find_dotenv())

BASE_DIR      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMBINED_FILE = os.path.join(BASE_DIR, "data", "processed", "job_market_combined.csv")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "job_market")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", os.getenv("DB_PASSWORD", "password"))

DB_PASS_ESCAPED  = urllib.parse.quote_plus(DB_PASS)
CONNECTION_STRING = f"postgresql+psycopg2://{DB_USER}:{DB_PASS_ESCAPED}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

print("Connecting to PostgreSQL...")
engine = create_engine(CONNECTION_STRING)

try:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print("  Connected.")
except Exception as e:
    print(f"  Connection failed: {e}")
    raise


def clear_tables(db_engine):
    print("Clearing existing data...")
    try:
        with db_engine.begin() as conn:
            conn.execute(text("TRUNCATE TABLE job_listings, fresher_applications RESTART IDENTITY CASCADE;"))
        print("  Done.")
    except Exception as e:
        print(f"  Warning: {e}")


clear_tables(engine)


print(f"\nLoading {COMBINED_FILE}...")
df = pd.read_csv(COMBINED_FILE)
print(f"  Rows: {len(df)}")

df_salary  = df[df["source"].isin(["salary_ds", "ai_market_ds"])].copy()
df_fresher = df[df["source"] == "fresher_ds"].copy()

ds1_rows = (df["source"] == "salary_ds").sum()
ds2_rows = (df["source"] == "fresher_ds").sum()
ds3_rows = (df["source"] == "ai_market_ds").sum()
print(f"  salary_ds rows   : {ds1_rows}")
print(f"  fresher_ds rows  : {ds2_rows}")
print(f"  ai_market_ds rows: {ds3_rows}")
print(f"  → job_listings   : {len(df_salary)}")


# --- job_listings ---
print("\nLoading job_listings...")

listings_cols = ["job_role", "city", "state", "locality", "salary_inr", "source"]
listings_cols = [c for c in listings_cols if c in df_salary.columns]
df_listings = df_salary[listings_cols].copy()
df_listings["salary_inr"] = pd.to_numeric(df_listings["salary_inr"], errors="coerce")

df_listings.to_sql(
    name="job_listings",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=500,
    method="multi"
)
print(f"  Inserted {len(df_listings)} rows")


# --- fresher_applications ---
print("\nLoading fresher_applications...")

fresher_cols = [
    "gender", "age", "graduation_year", "college", "degree", "branch",
    "cgpa", "backlogs", "gap_year", "prior_internship",
    "projects_count", "certifications_count", "skills",
    "linkedin_connections", "profile_completion_pct",
    "linkedin_premium", "referral_applied",
    "platform", "company_applied", "sector", "job_role",
    "work_type", "city", "application_date",
    "hiring_stage", "interview_rounds", "response_time_days",
    "offered_salary_inr", "hired", "source"
]
fresher_cols = [c for c in fresher_cols if c in df_fresher.columns]
df_fresh = df_fresher[fresher_cols].copy()

numeric_cols = ["cgpa", "offered_salary_inr", "profile_completion_pct"]
int_cols     = [
    "age", "graduation_year", "backlogs", "projects_count",
    "certifications_count", "linkedin_connections",
    "interview_rounds", "response_time_days",
    "gap_year", "prior_internship", "linkedin_premium",
    "referral_applied", "hired"
]

for col in numeric_cols:
    if col in df_fresh.columns:
        df_fresh[col] = pd.to_numeric(df_fresh[col], errors="coerce")

for col in int_cols:
    if col in df_fresh.columns:
        df_fresh[col] = pd.to_numeric(df_fresh[col], errors="coerce").astype("Int64")

if "application_date" in df_fresh.columns:
    df_fresh["application_date"] = pd.to_datetime(
        df_fresh["application_date"], errors="coerce"
    ).dt.date

if "hiring_stage" in df_fresh.columns:
    df_fresh["hiring_stage"] = df_fresh["hiring_stage"].astype(str)

df_fresh.to_sql(
    name="fresher_applications",
    con=engine,
    if_exists="append",
    index=False,
    chunksize=500,
    method="multi"
)
print(f"  Inserted {len(df_fresh)} rows")


# --- dim_city ---
print("\nPopulating dim_city...")

cities_ds1 = df_salary[["city", "state", "locality"]].copy() if "locality" in df_salary.columns \
    else df_salary[["city", "state"]].assign(locality=None)
cities_ds2 = df_fresher[["city"]].assign(state=None, locality=None)

all_cities = (
    pd.concat([cities_ds1, cities_ds2], ignore_index=True)
    .drop_duplicates(subset=["city"])
    .dropna(subset=["city"])
    .reset_index(drop=True)
)

inserted_cities = 0
with engine.begin() as conn:
    for _, row in all_cities.iterrows():
        result = conn.execute(text("""
            INSERT INTO dim_city (city, state, locality)
            VALUES (:city, :state, :locality)
            ON CONFLICT (city) DO NOTHING
        """), {
            "city":     row["city"],
            "state":    row.get("state") if pd.notna(row.get("state")) else None,
            "locality": row.get("locality") if pd.notna(row.get("locality")) else None,
        })
        inserted_cities += result.rowcount

print(f"  {inserted_cities} new cities inserted ({len(all_cities)} unique total)")


# --- dim_role ---
print("\nPopulating dim_role...")

roles_ds1 = df_salary[["job_role"]].copy()
roles_ds1["sector"] = df_salary["sector"] if "sector" in df_salary.columns else None

roles_ds2 = df_fresher[["job_role"]].copy()
roles_ds2["sector"] = df_fresher["sector"] if "sector" in df_fresher.columns else None

all_roles = (
    pd.concat([roles_ds1, roles_ds2], ignore_index=True)
    .drop_duplicates(subset=["job_role"])
    .dropna(subset=["job_role"])
    .reset_index(drop=True)
)

inserted_roles = 0
with engine.begin() as conn:
    for _, row in all_roles.iterrows():
        result = conn.execute(text("""
            INSERT INTO dim_role (job_role, sector)
            VALUES (:job_role, :sector)
            ON CONFLICT (job_role) DO NOTHING
        """), {
            "job_role": row["job_role"],
            "sector":   row["sector"] if pd.notna(row.get("sector")) else None,
        })
        inserted_roles += result.rowcount

print(f"  {inserted_roles} new roles inserted ({len(all_roles)} unique total)")


# --- Verify ---
print("\nVerification:")
with engine.connect() as conn:
    r1 = conn.execute(text("SELECT COUNT(*) FROM job_listings")).scalar()
    r2 = conn.execute(text("SELECT COUNT(*) FROM fresher_applications")).scalar()
    r3 = conn.execute(text("SELECT COUNT(*) FROM dim_city")).scalar()
    r4 = conn.execute(text("SELECT COUNT(*) FROM dim_role")).scalar()
    r5 = conn.execute(text(
        "SELECT city, COUNT(*) as n FROM job_listings GROUP BY city ORDER BY n DESC LIMIT 5"
    )).fetchall()
    r6 = conn.execute(text(
        "SELECT hiring_stage, COUNT(*) as n FROM fresher_applications GROUP BY hiring_stage ORDER BY n DESC"
    )).fetchall()

print(f"  job_listings          : {r1}")
print(f"  fresher_applications  : {r2}")
print(f"  dim_city              : {r3}")
print(f"  dim_role              : {r4}")
print("\n  Top 5 cities:")
for row in r5:
    print(f"    {row[0]}: {row[1]}")
print("\n  Hiring stages:")
for row in r6:
    print(f"    {row[0]}: {row[1]}")

print("\nDone.")