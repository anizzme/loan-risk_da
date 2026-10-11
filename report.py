import sqlite3, datetime
import pandas as pd

VIEWS = ['grade', 'purpose', 'income', 'state', 'year', 'tiers']

def run():
    with sqlite3.connect('db/lending.db') as con:
        con.executescript(open('sql/risk_views.sql').read())
        stamp = datetime.date.today().isoformat()
        path = 'reports/loan_risk_report.xlsx'
        with pd.ExcelWriter(path) as xw:
            for v in VIEWS:
                pd.read_sql(f'SELECT * FROM vw_risk_by_{v}' if v != 'tiers'
                            else 'SELECT * FROM vw_risk_tiers', con).to_excel(xw, sheet_name=v, index=False)
    print('Report saved:', path)

if __name__ == '__main__':
    run()