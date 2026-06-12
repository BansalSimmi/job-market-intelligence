
# Step 1: Clean all source datasets and merge into one unified DataFrame

# Datasets:
#     DS1 — job_market_india.csv          (India job listings, salary data)
#     DS2 — fresher_hiring_india_dataset.csv  (India fresher hiring pipeline)
#     DS3 — ai_job_market_insights.csv    (Global AI/ML role & skills insights)
#     DS4 — postings.csv                  (LinkedIn US-only — SKIPPED, no India rows)

# Usage:  python scripts/clean_data.py

# Output:    data/processed/job_market_combined.csv


import pandas as pd
import numpy as np
import os

# PATHS
RAW_DIR       = r"C:\Users\simmi\OneDrive\Desktop\job-market-intelligence\data\raw"
PROCESSED_DIR = r"C:\Users\simmi\OneDrive\Desktop\job-market-intelligence\data\processed"
DS1_FILE      = os.path.join(RAW_DIR, "job_market_india.csv")
DS2_FILE      = os.path.join(RAW_DIR, "fresher_hiring_india_dataset.csv")
DS3_FILE      = os.path.join(RAW_DIR, "ai_job_market_insights.csv")
OUTPUT_FILE   = os.path.join(PROCESSED_DIR, "job_market_combined.csv")

# USD → INR conversion rate (approximate)
USD_TO_INR = 83.5

os.makedirs(PROCESSED_DIR, exist_ok=True)

# SHARED HELPERS
def parse_salary(s):
    """Strip currency symbols/commas and return float, or NaN."""
    if pd.isna(s):
        return np.nan
    s = str(s).replace(",", "").replace("₹", "").replace("INR", "").strip()
    try:
        return float(s)
    except ValueError:
        return np.nan


def normalize_role(role_str):
    """Map a messy job title to a canonical role name via substring lookup."""
    lower = str(role_str).lower()
    for keyword, canonical in ROLE_NORMALIZE_MAP.items():
        if keyword in lower:
            return canonical
    return str(role_str).strip()


# Canonical role names — maps common title variations → clean name
ROLE_NORMALIZE_MAP = {
    # Data & Analytics
    "data analyst":           "Data Analyst",
    "data analysis":          "Data Analyst",
    "business analyst":       "Business Analyst",
    "business analysis":      "Business Analyst",
    "operations analyst":     "Operations Analyst",
    "marketing analyst":      "Marketing Analyst",
    "finance analyst":        "Finance Analyst",
    "financial analyst":      "Finance Analyst",
    "seo analyst":            "SEO Analyst",
    "data entry":             "Data Entry Operator",
    # Data Engineering & DB
    "data engineer":          "Data Engineer",
    "database admin":         "Database Administrator",
    "database administrator": "Database Administrator",
    "dba":                    "Database Administrator",
    # Data Science
    "data scientist":         "Data Scientist",
    "junior data scientist":  "Data Scientist",
    # ML / AI
    "ml engineer":            "ML Engineer",
    "machine learning":       "ML Engineer",
    "ai engineer":            "AI Engineer",
    "ai/ml":                  "AI/ML Engineer",
    "deep learning":          "ML Engineer",
    "nlp engineer":           "NLP Engineer",
    "computer vision":        "Computer Vision Engineer",
    "ai researcher":          "AI Researcher",
    "research scientist":     "AI Researcher",
    # Agentic / Generative AI
    "generative ai":          "Generative AI Engineer",
    "gen ai":                 "Generative AI Engineer",
    "llm":                    "Generative AI Engineer",
    "agentic":                "Agentic AI Engineer",
    "prompt engineer":        "Prompt Engineer",
    # Software / Web / Mobile
    "software engineer":      "Software Engineer",
    "software developer":     "Software Engineer",
    "backend developer":      "Backend Developer",
    "backend engineer":       "Backend Developer",
    "frontend developer":     "Frontend Developer",
    "front end developer":    "Frontend Developer",
    "full stack":             "Full Stack Developer",
    "fullstack":              "Full Stack Developer",
    "android developer":      "Android Developer",
    "ios developer":          "iOS Developer",
    "mobile app developer":   "Mobile Developer",
    "mobile developer":       "Mobile Developer",
    # Web / UI
    "web developer":          "Web Developer",
    "web designer":           "Web Developer",
    "ui developer":           "Frontend Developer",
    "ux designer":            "UX Designer",
    "ux/ui":                  "UX Designer",
    # Cloud / DevOps / Infra
    "cloud engineer":         "Cloud Engineer",
    "devops":                 "DevOps Engineer",
    "site reliability":       "DevOps Engineer",
    "network engineer":       "Network Engineer",
    "systems engineer":       "Systems Engineer",
    "embedded":               "Embedded Engineer",
    "cybersecurity":          "Cybersecurity Analyst",
    "security analyst":       "Cybersecurity Analyst",
    "security engineer":      "Cybersecurity Analyst",
    # QA / Testing
    "qa engineer":            "QA Engineer",
    "quality assurance":      "QA Engineer",
    "software tester":        "QA Engineer",
    "test engineer":          "QA Engineer",
    # Product / Project
    "product manager":        "Product Manager",
    "project manager":        "Project Manager",
    "scrum master":           "Project Manager",
    # Support / Operations
    "technical support":      "Technical Support Engineer",
    "tech support":           "Technical Support Engineer",
    "customer support":       "Customer Support Executive",
    "customer service":       "Customer Support Executive",
    "customer care":          "Customer Support Executive",
    # Programming Language trainees
    "python developer":       "Software Engineer",
    "python intern":          "Software Engineer",
    "java developer":         "Software Engineer",
    "html developer":         "Frontend Developer",
    # Sales / Marketing / HR
    "digital marketing":      "Digital Marketing Executive",
    "marketing specialist":   "Marketing Analyst",
    "sales executive":        "Sales Executive",
    "sales manager":          "Sales Executive",
    "sales officer":          "Sales Executive",
    "recruiter":              "Recruiter",
    "hr executive":           "HR Executive",
    "hr manager":             "HR Executive",
    "content writer":         "Content Writer",
}

# Sector lookup for DS1 (which has no sector column)
DATA_AI_ROLES = {
    "Data Analyst", "Data Scientist", "Data Engineer", "Business Analyst",
    "ML Engineer", "AI Engineer", "AI/ML Engineer", "NLP Engineer",
    "Computer Vision Engineer", "Generative AI Engineer", "Agentic AI Engineer",
    "Prompt Engineer", "AI Researcher", "Operations Analyst", "Database Administrator",
}

def infer_sector(role):
    if role in DATA_AI_ROLES:
        return "Data/AI/ML"
    if any(k in role.lower() for k in ["cloud", "devops", "network", "systems", "embedded", "cybersecurity"]):
        return "IT/Software"
    return "IT/Software"


# LOAD ALL DATASETS
print("Loading datasets...")
df1 = pd.read_csv(DS1_FILE)
df2 = pd.read_csv(DS2_FILE)
df3 = pd.read_csv(DS3_FILE) if os.path.exists(DS3_FILE) else None

print(f"  DS1 (job_market_india):           {df1.shape}")
print(f"  DS2 (fresher_hiring_india):        {df2.shape}")
if df3 is not None:
    print(f"  DS3 (ai_job_market_insights):     {df3.shape}")
print("  DS4 (postings.csv): SKIPPED — US-only dataset, 0 India rows")


# CLEAN DS1  (job_market_india.csv)
print("\nCleaning DS1...")

df1.columns = df1.columns.str.strip().str.lower().str.replace(" ", "_")

# Resolve job role column name
if "job" in df1.columns and "title" in df1.columns:
    df1["job_role"] = df1["title"].combine_first(df1["job"])
    df1.drop(columns=["job", "title"], inplace=True)
elif "job_title" in df1.columns:
    df1.rename(columns={"job_title": "job_role"}, inplace=True)
elif "title" in df1.columns:
    df1.rename(columns={"title": "job_role"}, inplace=True)
elif "job" in df1.columns:
    df1.rename(columns={"job": "job_role"}, inplace=True)

df1.rename(columns={"location": "city", "monthly_salary": "salary_inr"}, inplace=True)

df1["salary_inr"] = df1["salary_inr"].apply(parse_salary)

for col in ["city", "locality", "state"]:
    if col in df1.columns:
        df1[col] = df1[col].astype(str).str.strip().str.title()

df1["job_role"] = df1["job_role"].astype(str).str.strip().str.title()
df1["job_role"] = df1["job_role"].apply(normalize_role)
df1["sector"]   = df1["job_role"].apply(infer_sector)
df1["source"]   = "salary_ds"
df1["is_fresher"] = 0

ds1_keep = ["job_role", "city", "locality", "state", "salary_inr", "sector", "source", "is_fresher"]
df1 = df1[[c for c in ds1_keep if c in df1.columns]]
print(f"  DS1 cleaned: {df1.shape} | unique roles: {df1['job_role'].nunique()} | unique cities: {df1['city'].nunique()}")


# CLEAN DS2  (fresher_hiring_india_dataset.csv)
print("\nCleaning DS2...")

df2.columns = df2.columns.str.strip().str.lower().str.replace(" ", "_")
df2.drop(columns=[c for c in ["candidate_id", "full_name"] if c in df2.columns], inplace=True)

df2.rename(columns={
    "job_location":       "city",
    "top_skills":         "skills",
    "offered_salary_inr": "salary_inr",
}, inplace=True)

for col in ["city", "job_role"]:
    if col in df2.columns:
        df2[col] = df2[col].astype(str).str.strip().str.title()

# Skills: DS2 uses pipe (|) as native separator → normalise to comma-separated lowercase
if "skills" in df2.columns:
    df2["skills"] = (
        df2["skills"]
        .astype(str).str.strip().str.lower()
        .str.replace(r"\s*\|\s*", ", ", regex=True)
        .str.replace(r"\s*,\s*", ", ", regex=True)
    )

df2["salary_inr"] = df2["salary_inr"].apply(parse_salary)

bool_cols = ["gap_year", "prior_internship", "linkedin_premium", "referral_applied", "backlogs"]
for col in bool_cols:
    if col in df2.columns:
        df2[col] = df2[col].map(
            {"Yes": 1, "No": 0, "TRUE": 1, "FALSE": 0, True: 1, False: 0, 1: 1, 0: 0}
        ).fillna(df2[col]).infer_objects(copy=False)

stage_mapping = {
    "Applied": "Applied", "Shortlisted": "Shortlisted",
    "Online Assessment": "Assessment", "Technical Interview": "Interview",
    "HR Interview": "Interview", "Offer": "Hired",
    "Rejected": "Rejected", "Withdrawn": "Withdrawn",
}
if "hiring_stage" in df2.columns:
    df2["hiring_stage"] = df2["hiring_stage"].map(stage_mapping).fillna(df2["hiring_stage"])

stage_order = ["Applied", "Assessment", "Shortlisted", "Interview", "Hired", "Rejected", "Withdrawn"]
if "hiring_stage" in df2.columns:
    df2["hiring_stage"] = pd.Categorical(df2["hiring_stage"], categories=stage_order, ordered=True)

df2["hired"]      = (df2["hiring_stage"] == "Hired").astype(int)
df2["source"]     = "fresher_ds"
df2["is_fresher"] = 1

print(f"  DS2 cleaned: {df2.shape} | unique roles: {df2['job_role'].nunique()} | unique cities: {df2['city'].nunique()}")


# CLEAN DS3  (ai_job_market_insights.csv)
if df3 is not None:
    print("\nCleaning DS3...")

    df3.columns = df3.columns.str.strip().str.lower().str.replace(" ", "_")

    # Rename to unified schema
    df3.rename(columns={
        "job_title":        "job_role",
        "industry":         "sector",
        "required_skills":  "skills",
        "salary_usd":       "salary_usd_raw",
        "remote_friendly":  "work_type_flag",
        "location":         "original_location",
    }, inplace=True)

    # Normalise job role
    df3["job_role"] = df3["job_role"].astype(str).str.strip().str.title()
    df3["job_role"] = df3["job_role"].apply(normalize_role)

    # Convert USD salary → INR
    df3["salary_inr"] = pd.to_numeric(df3["salary_usd_raw"], errors="coerce") * USD_TO_INR

    # Skills: single string → keep as-is, just lowercase
    if "skills" in df3.columns:
        df3["skills"] = df3["skills"].astype(str).str.strip().str.lower()

    # work_type from Remote_Friendly flag
    if "work_type_flag" in df3.columns:
        df3["work_type"] = df3["work_type_flag"].map(
            {"Yes": "Remote", "No": "On-site", True: "Remote", False: "On-site"}
        ).fillna("On-site")

    # DS3 is global — assign to major Indian tech hubs proportionally
    INDIA_TECH_CITIES = [
        "Bengaluru", "Hyderabad", "Pune", "Chennai", "Mumbai",
        "Noida", "Gurugram", "Delhi NCR", "Kolkata", "Ahmedabad",
        "Jaipur", "Coimbatore", "Kochi", "Indore", "Chandigarh",
    ]
    np.random.seed(42)
    df3["city"]  = np.random.choice(INDIA_TECH_CITIES, size=len(df3))
    df3["state"] = None

    # Keep additional insight columns as-is (no fresher-specific fields)
    df3["source"]     = "ai_market_ds"
    df3["is_fresher"] = 0

    ds3_keep = [
        "job_role", "city", "state", "salary_inr", "sector",
        "skills", "work_type", "source", "is_fresher",
        "ai_adoption_level", "automation_risk", "job_growth_projection",
    ]
    df3 = df3[[c for c in ds3_keep if c in df3.columns]]
    print(f"  DS3 cleaned: {df3.shape} | unique roles: {df3['job_role'].nunique()} | cities assigned: {df3['city'].nunique()}")
    print(f"  DS3 roles added: {sorted(df3['job_role'].unique())}")
else:
    print("\nDS3 not found — skipping.")
    df3 = pd.DataFrame()


# MERGE ALL — pd.concat (vertical stack)
print("\nMerging all datasets...")

frames = [df1, df2]
if not df3.empty:
    frames.append(df3)

combined = pd.concat(frames, ignore_index=True, sort=False)

print(f"  Combined shape: {combined.shape}")
print(f"  Source breakdown:\n{combined['source'].value_counts().to_string()}")
print(f"  Null counts per column:\n{combined.isnull().sum().to_string()}")


# FINAL QUALITY CHECKS
print("\nRunning quality checks...")

before = len(combined)
combined.dropna(subset=["job_role", "city"], inplace=True)
print(f"  Dropped {before - len(combined)} rows with missing job_role or city")

p99 = combined["salary_inr"].quantile(0.99)
outliers = combined["salary_inr"] > p99 * 10
print(f"  Salary outliers flagged: {outliers.sum()}")
combined.loc[outliers, "salary_inr"] = np.nan

before = len(combined)
combined.drop_duplicates(inplace=True)
print(f"  Duplicates removed: {before - len(combined)}")


# SAVE
combined.to_csv(OUTPUT_FILE, index=False)
print(f"\n[Done] Saved to {OUTPUT_FILE}")
print(f"  Final shape          : {combined.shape}")
print(f"  Source breakdown:\n{combined['source'].value_counts().to_string()}")
print(f"  Unique cities        : {combined['city'].nunique()}")
print(f"  Unique job roles     : {combined['job_role'].nunique()}")
print(f"  Salary range (INR)   : {combined['salary_inr'].min():,.0f} – {combined['salary_inr'].max():,.0f}")
print(f"  Fresher records      : {int(combined['is_fresher'].sum())}")