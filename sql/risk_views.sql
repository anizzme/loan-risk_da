DROP VIEW IF EXISTS vw_risk_by_grade;
CREATE VIEW vw_risk_by_grade AS
SELECT grade, COUNT(*) AS loans, SUM(is_charged_off) AS charged_off,
       ROUND(100.0 * SUM(is_charged_off) / COUNT(*), 2) AS charge_off_pct,
       ROUND(AVG(int_rate), 2) AS avg_int_rate
FROM loans_clean WHERE outcome_known = 1 GROUP BY grade;

DROP VIEW IF EXISTS vw_risk_by_purpose;
CREATE VIEW vw_risk_by_purpose AS
SELECT purpose, COUNT(*) AS loans,
       ROUND(100.0 * SUM(is_charged_off) / COUNT(*), 2) AS charge_off_pct
FROM loans_clean WHERE outcome_known = 1 GROUP BY purpose;

DROP VIEW IF EXISTS vw_risk_by_income;
CREATE VIEW vw_risk_by_income AS
SELECT annual_inc_range, COUNT(*) AS loans,
       ROUND(100.0 * SUM(is_charged_off) / COUNT(*), 2) AS charge_off_pct
FROM loans_clean WHERE outcome_known = 1 AND income_outlier = 0 GROUP BY annual_inc_range;

DROP VIEW IF EXISTS vw_risk_by_state;
CREATE VIEW vw_risk_by_state AS
SELECT addr_state, COUNT(*) AS loans,
       ROUND(100.0 * SUM(is_charged_off) / COUNT(*), 2) AS charge_off_pct,
       RANK() OVER (ORDER BY 1.0 * SUM(is_charged_off) / COUNT(*) DESC) AS risk_rank
FROM loans_clean WHERE outcome_known = 1
GROUP BY addr_state HAVING COUNT(*) >= 15;

DROP VIEW IF EXISTS vw_risk_by_year;
CREATE VIEW vw_risk_by_year AS
SELECT issue_year, COUNT(*) AS loans,
       ROUND(100.0 * SUM(is_charged_off) / COUNT(*), 2) AS charge_off_pct
FROM loans_clean WHERE outcome_known = 1 GROUP BY issue_year;

DROP VIEW IF EXISTS vw_risk_tiers;
CREATE VIEW vw_risk_tiers AS
SELECT CASE WHEN grade IN ('E','F','G') OR int_rate >= 15 THEN 'High'
            WHEN grade IN ('C','D') THEN 'Medium' ELSE 'Low' END AS risk_tier,
       COUNT(*) AS loans,
       ROUND(100.0 * SUM(is_charged_off) / COUNT(*), 2) AS charge_off_pct
FROM loans_clean WHERE outcome_known = 1 GROUP BY risk_tier;