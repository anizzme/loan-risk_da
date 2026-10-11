# Loan Risk Pipeline (LendingClub 2007-2011)

Python ETL + SQL + automated report + Streamlit dashboard on 38,004 loans.

## What it does
1. etl.py extracts 2007-2011 loans, cleans them (Pandas, NumPy) and loads them into SQLite
2. sql/risk_views.sql calculates charge-off rates by grade, purpose, income and state
3. pipeline.py runs everything and report.py writes an Excel risk report
4. app.py is an interactive Streamlit dashboard

## Key findings
- Overall charge-off rate 14.87%
- Grade A 5.77% versus grade G 32.55%
- Lowest income band about 19% versus highest about 11%

## How to run
Download accepted_2007_to_2018Q4.csv.gz from Kaggle (wordsforthewise/lending-club) into data/raw, then:
pip install -r requirements.txt
python pipeline.py
streamlit run app.py
