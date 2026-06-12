import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

df1 = pd.read_csv("data/raw/job_market_india.csv")
df2 = pd.read_csv("data/raw/fresher_hiring_india_dataset.csv")

print("=== DS1: job_market_india.csv ===")
print(f"Rows    : {len(df1)}")
cities1 = sorted(df1["Location"].dropna().unique())
print(f"Cities  : {len(cities1)}")
print(f"Sample  : {cities1[:40]}")

print()
print("=== DS2: fresher_hiring_india_dataset.csv ===")
print(f"Rows    : {len(df2)}")
cities2 = sorted(df2["job_location"].dropna().unique())
print(f"Cities  : {len(cities2)}")
print(f"All     : {cities2}")

print()
roles2 = sorted(df2["job_role"].dropna().unique())
print(f"Roles   : {len(roles2)}")
print(f"All     : {roles2}")

print()
sectors = sorted(df2["sector"].dropna().unique())
print(f"Sectors : {len(sectors)}")
print(f"All     : {sectors}")

print()
skills_flat = df2["top_skills"].dropna().str.split("|").explode().str.strip().str.lower()
print(f"Unique skills : {skills_flat.nunique()}")
print(f"Top 30        : {list(skills_flat.value_counts().head(30).index)}")
