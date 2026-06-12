import pandas as pd, sys
sys.stdout.reconfigure(encoding='utf-8')

INDIA_PATTERN = r'India$|,\s*India\b'
chunks = pd.read_csv(
    'data/raw/postings.csv',
    chunksize=100000,
    usecols=['title','location','max_salary','min_salary','currency','formatted_work_type','skills_desc']
)
total, india_total = 0, 0
india_frames = []
for chunk in chunks:
    total += len(chunk)
    india = chunk[chunk['location'].str.contains(INDIA_PATTERN, na=False, regex=True)]
    india_total += len(india)
    if len(india) > 0:
        india_frames.append(india)
    print(f"  Processed {total:,} rows | India rows found so far: {india_total}")

print(f"\nFinal: {total:,} total rows, {india_total} India rows")
if india_frames:
    df_india = pd.concat(india_frames, ignore_index=True)
    print(df_india[['title','location','max_salary','currency']].head(20).to_string())
    print(f"\nUnique titles: {df_india['title'].nunique()}")
    print(f"Unique locations: {df_india['location'].unique()}")
