
-- Drop tables if re-running (safe order: child → parent)
DROP TABLE IF EXISTS fresher_applications CASCADE;
DROP TABLE IF EXISTS job_listings CASCADE;
DROP TABLE IF EXISTS dim_city CASCADE;
DROP TABLE IF EXISTS dim_role CASCADE;
DROP TABLE IF EXISTS dim_skill CASCADE;

-- ────────────────────────────────────────────────────────────
-- DIMENSION: cities
-- ────────────────────────────────────────────────────────────
CREATE TABLE dim_city (
    city_id     SERIAL PRIMARY KEY,
    city        VARCHAR(100) NOT NULL UNIQUE,
    state       VARCHAR(100),
    locality    VARCHAR(100)
);

-- ────────────────────────────────────────────────────────────
-- DIMENSION: job roles
-- ────────────────────────────────────────────────────────────
CREATE TABLE dim_role (
    role_id     SERIAL PRIMARY KEY,
    job_role    VARCHAR(200) NOT NULL UNIQUE,
    sector      VARCHAR(100)
);

-- ────────────────────────────────────────────────────────────
-- FACT: job listings (DS1 — salary dataset)
-- One row per job posting from job_market_india.csv
-- ────────────────────────────────────────────────────────────
CREATE TABLE job_listings (
    listing_id      SERIAL PRIMARY KEY,
    job_role        VARCHAR(200),
    city            VARCHAR(100),
    state           VARCHAR(100),
    locality        VARCHAR(100),
    salary_inr      NUMERIC(12, 2),
    source          VARCHAR(50)  DEFAULT 'salary_ds',
    created_at      TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

-- ────────────────────────────────────────────────────────────
-- FACT: fresher applications (DS2 — hiring dataset)
-- One row per fresher job application
-- ────────────────────────────────────────────────────────────
CREATE TABLE fresher_applications (
    app_id                  SERIAL PRIMARY KEY,

    -- Candidate profile
    gender                  VARCHAR(20),
    age                     INT,
    graduation_year         INT,
    college                 VARCHAR(200),
    degree                  VARCHAR(100),
    branch                  VARCHAR(100),
    cgpa                    NUMERIC(4, 2),
    backlogs                INT          DEFAULT 0,
    gap_year                SMALLINT     DEFAULT 0,   -- 0/1
    prior_internship        SMALLINT     DEFAULT 0,   -- 0/1
    projects_count          INT,
    certifications_count    INT,
    skills                  TEXT,                     -- comma-separated
    linkedin_connections    INT,
    profile_completion_pct  NUMERIC(5, 2),
    linkedin_premium        SMALLINT     DEFAULT 0,   -- 0/1
    referral_applied        SMALLINT     DEFAULT 0,   -- 0/1

    -- Application details
    platform                VARCHAR(100),
    company_applied         VARCHAR(200),
    sector                  VARCHAR(100),
    job_role                VARCHAR(200),
    work_type               VARCHAR(50),
    city                    VARCHAR(100),
    application_date        DATE,

    -- Outcome
    hiring_stage            VARCHAR(50),
    interview_rounds        INT,
    response_time_days      INT,
    offered_salary_inr      NUMERIC(12, 2),
    hired                   SMALLINT     DEFAULT 0,   -- 0/1 (derived)

    source                  VARCHAR(50)  DEFAULT 'fresher_ds',
    created_at              TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

-- ────────────────────────────────────────────────────────────
-- INDEXES (speeds up all GROUP BY / WHERE queries)
-- ────────────────────────────────────────────────────────────
CREATE INDEX idx_listings_city      ON job_listings(city);
CREATE INDEX idx_listings_role      ON job_listings(job_role);
CREATE INDEX idx_listings_salary    ON job_listings(salary_inr);

CREATE INDEX idx_apps_city          ON fresher_applications(city);
CREATE INDEX idx_apps_role          ON fresher_applications(job_role);
CREATE INDEX idx_apps_platform      ON fresher_applications(platform);
CREATE INDEX idx_apps_hired         ON fresher_applications(hired);
CREATE INDEX idx_apps_sector        ON fresher_applications(sector);
CREATE INDEX idx_apps_grad_year     ON fresher_applications(graduation_year);
CREATE INDEX idx_apps_hiring_stage  ON fresher_applications(hiring_stage);

-- ────────────────────────────────────────────────────────────
-- VERIFICATION QUERIES (run after loading data)
-- ────────────────────────────────────────────────────────────
SELECT COUNT(*) FROM job_listings;
SELECT COUNT(*) FROM fresher_applications;
-- SELECT city, COUNT(*) FROM job_listings GROUP BY city ORDER BY 2 DESC LIMIT 10;
