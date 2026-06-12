import pandas as pd
df1 = pd.read_csv(r"data/raw/job_market_india.csv")
df2 = pd.read_csv(r"data/raw/fresher_hiring_india_dataset.csv")

print("DS1: job_market_india.csv ")
print(f"Total rows : {len(df1)}")
cities1 = sorted(df1["Location"].dropna().unique())
print(f"Total cities: {len(cities1)}")
print(f"Sample cities: {cities1[:40]}")

print()
print(" DS2: fresher_hiring_india_dataset.csv ")
print(f"Total rows : {len(df2)}")
cities2 = sorted(df2["job_location"].dropna().unique())
print(f"Total cities : {len(cities2)}")
print(f"All cities   : {cities2}")

print()
roles2 = sorted(df2["job_role"].dropna().unique())
print(f"Total job roles : {len(roles2)}")
print(f"All job roles   : {roles2}")

print()
sectors = sorted(df2["sector"].dropna().unique())
print(f"Total sectors : {len(sectors)}")
print(f"All sectors   : {sectors}")

print()
skills_flat = df2["top_skills"].dropna().str.split("|").explode().str.strip().str.lower()
print(f"Unique skills  : {skills_flat.nunique()}")
print(f"Top 30 skills  : {list(skills_flat.value_counts().head(30).index)}")
