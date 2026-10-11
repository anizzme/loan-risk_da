import os, sqlite3
import numpy as np
import pandas as pd

RAW = 'data/raw/accepted_2007_to_2018Q4.csv.gz'
DB = 'db/lending.db'
OUT = 'data/processed/loans_clean.csv'

def extract():
    parts = []
    # read the big file in chunks and keep only loans issued 2007-2011
    for chunk in pd.read_csv(RAW, dtype=object, low_memory=False, chunksize=200000):
        year = pd.to_numeric(chunk['issue_d'].str[-4:], errors='coerce')
        parts.append(chunk[year.between(2007, 2011)])
    df = pd.concat(parts, ignore_index=True)
    print('Extracted rows/cols:', df.shape)
    return df

def transform(df):
    df = df.dropna(subset=['id', 'loan_amnt']).copy()      # blank/junk rows
    df = df.loc[:, df.isnull().mean() < 0.3]               # >=30% null columns
    df = df.loc[:, df.nunique() > 1]                       # constant columns
    df = df.drop(columns=['member_id', 'url', 'zip_code'], errors='ignore')

    num = ['loan_amnt', 'funded_amnt', 'funded_amnt_inv', 'installment', 'annual_inc', 'dti']
    df[num] = df[num].apply(pd.to_numeric, errors='coerce')
    df['int_rate'] = df['int_rate'].astype(str).str.rstrip('%').astype(float)
    df['term'] = df['term'].str.strip()
    df['emp_length'] = df['emp_length'].fillna('0')

    # drop 'other' and rare purposes (<0.75%), as in the notebook
    share = df['purpose'].value_counts(normalize=True) * 100
    drop = list(share[share < 0.75].index) + ['other']
    df = df[~df['purpose'].isin(drop)].copy()

    df['issue_month'] = df['issue_d'].str[:3]
    df['issue_year'] = df['issue_d'].str[-4:].astype(int)

    # NumPy-driven derived metrics
    df['loan_income_ratio'] = df['loan_amnt'] / df['annual_inc']
    df['log_annual_inc'] = np.log1p(df['annual_inc'])
    df['is_charged_off'] = np.where(df['loan_status'].str.contains('Charged Off'), 1, 0)
    df['outcome_known'] = np.where(df['loan_status'].str.contains('Fully Paid|Charged Off'), 1, 0)
    df['income_outlier'] = np.where(df['annual_inc'] > df['annual_inc'].quantile(0.99), 1, 0)

    df['loan_amnt_range'] = pd.cut(df['loan_amnt'], [0, 5000, 10000, 15000, 20000, 25000, 40000],
        labels=['0-5000', '5000-10000', '10000-15000', '15000-20000', '20000-25000', '25000+']).astype(str)
    df['annual_inc_range'] = pd.cut(df['annual_inc'], [0, 25000, 50000, 75000, 100000, 1e7],
        labels=['0-25k', '25k-50k', '50k-75k', '75k-100k', '100k+']).astype(str)
    df['int_rate_range'] = pd.cut(df['int_rate'], [0, 7.5, 10, 12.5, 15, 100],
        labels=['0-7.5', '7.5-10', '10-12.5', '12.5-15', '15+']).astype(str)
    df['emp_length'] = df['emp_length'].astype(str)
    print('Transformed rows/cols:', df.shape)
    return df

def load(df):
    os.makedirs('db', exist_ok=True)
    os.makedirs('data/processed', exist_ok=True)
    with sqlite3.connect(DB) as con:
        df.to_sql('loans_clean', con, if_exists='replace', index=False)
        for col in ['grade', 'purpose', 'addr_state', 'issue_year']:
            con.execute(f'CREATE INDEX IF NOT EXISTS idx_{col} ON loans_clean({col})')
    df.to_csv(OUT, index=False)
    print(f'Loaded {len(df):,} rows into {DB} and {OUT}')

if __name__ == '__main__':
    load(transform(extract()))