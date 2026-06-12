
-- ── Q1: Top 10 highest-paying cities (avg salary)
-- "Which Indian cities offer the best salaries?"
SELECT
    city,
    ROUND(AVG(salary_inr), 0)   AS avg_salary_inr,
    COUNT(*)                     AS job_count
FROM job_listings
WHERE salary_inr IS NOT NULL
GROUP BY city
ORDER BY avg_salary_inr DESC
LIMIT 10;


-- ── Q2: Top 10 highest-paying job roles
-- "Which roles command the highest salaries?"
SELECT
    job_role,
    ROUND(AVG(salary_inr), 0)   AS avg_salary_inr,
    ROUND(MIN(salary_inr), 0)   AS min_salary,
    ROUND(MAX(salary_inr), 0)   AS max_salary,
    COUNT(*)                     AS listings_count
FROM job_listings
WHERE salary_inr IS NOT NULL
GROUP BY job_role
HAVING COUNT(*) >= 5
ORDER BY avg_salary_inr DESC
LIMIT 10;


-- ── Q3: Fresher hire rate by platform
-- "Which job platform gives freshers the best chance of getting hired?"
SELECT
    platform,
    COUNT(*)                                            AS total_applications,
    SUM(hired)                                          AS hired_count,
    ROUND(100.0 * SUM(hired) / COUNT(*), 1)            AS hire_rate_pct
FROM fresher_applications
WHERE platform IS NOT NULL
GROUP BY platform
HAVING COUNT(*) >= 20
ORDER BY hire_rate_pct DESC;


-- ── Q4: Does CGPA actually matter for hiring?
-- "Is CGPA a significant factor in getting hired?"
SELECT
    CASE
        WHEN cgpa >= 8.5 THEN 'Distinction (8.5+)'
        WHEN cgpa >= 7.5 THEN 'First class (7.5–8.4)'
        WHEN cgpa >= 6.5 THEN 'Second class (6.5–7.4)'
        ELSE                   'Below 6.5'
    END                                                AS cgpa_band,
    COUNT(*)                                           AS total,
    SUM(hired)                                         AS hired,
    ROUND(100.0 * SUM(hired) / COUNT(*), 1)           AS hire_rate_pct,
    ROUND(AVG(offered_salary_inr), 0)                 AS avg_offered_salary
FROM fresher_applications
WHERE cgpa IS NOT NULL
GROUP BY cgpa_band
ORDER BY hire_rate_pct DESC;


-- ── Q5: Impact of prior internship on hire rate
-- "Do freshers with internship experience get hired more?"
SELECT
    CASE prior_internship WHEN 1 THEN 'Had internship' ELSE 'No internship' END AS internship_status,
    COUNT(*)                                               AS total,
    SUM(hired)                                             AS hired,
    ROUND(100.0 * SUM(hired) / COUNT(*), 1)               AS hire_rate_pct,
    ROUND(AVG(offered_salary_inr), 0)                     AS avg_salary_offered
FROM fresher_applications
GROUP BY prior_internship
ORDER BY hire_rate_pct DESC;


-- ── Q6: Top skills that appear in hired candidates
-- "What skills do hired freshers have that rejected ones don't?"
-- Splits the comma-separated skills column and counts frequencies
WITH skill_rows AS (
    SELECT
        TRIM(LOWER(skill_val))  AS skill,
        hired
    FROM fresher_applications,
         LATERAL UNNEST(STRING_TO_ARRAY(skills, ',')) AS skill_val
    WHERE skills IS NOT NULL
),
skill_stats AS (
    SELECT
        skill,
        COUNT(*)                                        AS total_mentions,
        SUM(hired)                                      AS hired_with_skill,
        ROUND(100.0 * SUM(hired) / COUNT(*), 1)        AS hire_rate_pct
    FROM skill_rows
    GROUP BY skill
    HAVING COUNT(*) >= 15
)
SELECT *
FROM skill_stats
ORDER BY hire_rate_pct DESC
LIMIT 20;


-- ── Q7: Salary comparison — fresher offer vs market salary
-- "Are freshers being paid fairly compared to market rates?"
SELECT
    fa.job_role,
    ROUND(AVG(fa.offered_salary_inr), 0)    AS avg_fresher_offer,
    ROUND(AVG(jl.salary_inr), 0)            AS avg_market_salary,
    ROUND(
        100.0 * (AVG(fa.offered_salary_inr) - AVG(jl.salary_inr))
        / NULLIF(AVG(jl.salary_inr), 0), 1
    )                                        AS pct_difference
FROM fresher_applications fa
JOIN job_listings jl ON LOWER(fa.job_role) = LOWER(jl.job_role)
WHERE fa.offered_salary_inr IS NOT NULL
  AND jl.salary_inr IS NOT NULL
  AND fa.hired = 1
GROUP BY fa.job_role
HAVING COUNT(*) >= 5
ORDER BY avg_market_salary DESC
LIMIT 15;


-- ── Q8: Hiring funnel — stage drop-off analysis
-- "Where in the process are most candidates rejected?"
SELECT
    hiring_stage,
    COUNT(*)                                            AS candidates,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct_of_total
FROM fresher_applications
WHERE hiring_stage IS NOT NULL
  AND hiring_stage != 'nan'
GROUP BY hiring_stage
ORDER BY candidates DESC;


-- ── Q9: Remote vs on-site — sector breakdown
-- "Which sectors offer the most remote-friendly jobs?"
SELECT
    sector,
    work_type,
    COUNT(*)                                           AS count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY sector), 1) AS pct_within_sector
FROM fresher_applications
WHERE sector IS NOT NULL
  AND work_type IS NOT NULL
GROUP BY sector, work_type
ORDER BY sector, count DESC;


-- ── Q10: Referral advantage — does it boost hire chance?
-- "Is applying with a referral significantly better?"
SELECT
    CASE referral_applied WHEN 1 THEN 'Referral used' ELSE 'No referral' END AS referral_status,
    COUNT(*)                                                AS total,
    SUM(hired)                                              AS hired,
    ROUND(100.0 * SUM(hired) / COUNT(*), 1)                AS hire_rate_pct,
    ROUND(AVG(response_time_days), 1)                      AS avg_response_days
FROM fresher_applications
GROUP BY referral_applied
ORDER BY hire_rate_pct DESC;
