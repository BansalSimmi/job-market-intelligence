import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

print("=" * 60)
print("DS3: ai_job_market_insights.csv")
print("=" * 60)
ds3 = pd.read_csv("data/raw/ai_job_market_insights.csv")
print(f"Shape   : {ds3.shape}")
print(f"Columns : {list(ds3.columns)}")
print()
print(ds3.head(3).to_string())
print()
for col in ds3.columns:
    n_unique = ds3[col].nunique()
    sample   = list(ds3[col].dropna().unique()[:6])
    print(f"  {col:<35} ({n_unique} unique) → {sample}")

print()
print("=" * 60)
print("DS4: postings.csv  [first 5 rows — file is ~500 MB]")
print("=" * 60)
ds4 = pd.read_csv("data/raw/postings.csv", nrows=5)
print(f"Columns ({len(ds4.columns)}): {list(ds4.columns)}")
print()
print(ds4.head(3).to_string())

ds4_sample = pd.read_csv("data/raw/postings.csv", nrows=5000)
print(f"\nSample (5000 rows):")
for col in ds4_sample.columns:
    n_unique = ds4_sample[col].nunique()
    sample   = list(ds4_sample[col].dropna().unique()[:5])
    print(f"  {col:<35} ({n_unique} unique) → {sample}")
