# Job Market Intelligence

An end-to-end data pipeline for analysing the Indian tech job market — from raw CSVs to a PostgreSQL database, EDA charts, and an Excel report.

## Project Structure

```
job-market-intelligence/
├── data/
│   ├── raw/                        # Source CSVs (not committed — see .gitignore)
│   └── processed/                  # Output of clean_data.py
├── scripts/
│   ├── clean_data.py               # Clean & merge raw datasets
│   ├── load_to_postgres.py         # Ingest into PostgreSQL
│   ├── eda_helpers.py              # Market overview charts
│   ├── hiring_analysis.py          # Fresher hiring analysis charts
│   └── generate_excel.py           # Build Excel report
├── sql/
│   ├── schema.sql                  # Table definitions
│   └── analysis_queries.sql        # 10 analytical SQL queries
├── notebooks/                      # Jupyter notebooks (optional)
├── excel/                          # Generated report output
├── powerbi/                        # Power BI dashboard file
├── requirements.txt
├── .env.example
└── .gitignore
```

## Quick Start

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables
copy .env.example .env
# Edit .env and fill in your PostgreSQL credentials

# 4. Create the database schema
psql -U postgres -d job_market_db -f sql/schema.sql

# 5. Run the pipeline
python scripts/clean_data.py
python scripts/load_to_postgres.py
python scripts/generate_excel.py
```

## Datasets

| Dataset | File | Description |
|---------|------|-------------|
| DS1 | `job_market_india.csv` | India job listings with salary data |
| DS2 | `fresher_hiring_india_dataset.csv` | Fresher hiring pipeline data |
| DS3 | `ai_job_market_insights.csv` | Global AI/ML role and skills insights |

All CSVs go in `data/raw/`. They are excluded from git by `.gitignore`.

## Environment Variables

Copy `.env.example` to `.env` and fill in your values.

| Variable | Description |
|----------|-------------|
| `DB_HOST` | PostgreSQL host |
| `DB_PORT` | PostgreSQL port (default `5432`) |
| `DB_NAME` | Database name |
| `DB_USER` | Database user |
| `DB_PASSWORD` | Database password |

> **Never commit `.env` to version control.**

## Requirements

See `requirements.txt`. Main dependencies: `pandas`, `sqlalchemy`, `psycopg2-binary`, `matplotlib`, `openpyxl`.
