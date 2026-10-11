import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title='Loan Risk Dashboard', layout='wide')

@st.cache_data
def q(sql, params=()):
    with sqlite3.connect('db/lending.db') as con:
        return pd.read_sql(sql, con, params=params)

st.title('LendingClub Loan Risk Dashboard')
grades = q('SELECT DISTINCT grade FROM loans_clean ORDER BY 1')['grade'].tolist()
years = q('SELECT DISTINCT issue_year FROM loans_clean ORDER BY 1')['issue_year'].tolist()
sel_g = st.sidebar.multiselect('Grade', grades, grades)
sel_y = st.sidebar.multiselect('Issue year', years, years)
if not sel_g or not sel_y:
    st.warning('Select at least one grade and year.')
    st.stop()

ph = lambda x: ','.join('?' * len(x))
where = f'outcome_known = 1 AND grade IN ({ph(sel_g)}) AND issue_year IN ({ph(sel_y)})'
params = tuple(sel_g) + tuple(sel_y)

k = q(f'SELECT COUNT(*) n, ROUND(100.0*SUM(is_charged_off)/COUNT(*),2) rate, ROUND(AVG(int_rate),2) ir FROM loans_clean WHERE {where}', params)
c1, c2, c3 = st.columns(3)
c1.metric('Loans', f"{int(k.n[0]):,}")
c2.metric('Charge-off rate %', k.rate[0])
c3.metric('Avg interest rate %', k.ir[0])

def by(col):
    return q(f'SELECT {col} AS k, COUNT(*) loans, ROUND(100.0*SUM(is_charged_off)/COUNT(*),2) charge_off_pct FROM loans_clean WHERE {where} GROUP BY {col} ORDER BY charge_off_pct DESC', params)

left, right = st.columns(2)
left.plotly_chart(px.bar(by('grade'), x='k', y='charge_off_pct', title='Charge-off % by grade'), use_container_width=True)
right.plotly_chart(px.bar(by('purpose'), x='k', y='charge_off_pct', title='Charge-off % by purpose'), use_container_width=True)
left.plotly_chart(px.bar(by('annual_inc_range'), x='k', y='charge_off_pct', title='Charge-off % by income band'), use_container_width=True)
right.plotly_chart(px.bar(by('addr_state').head(15), x='k', y='charge_off_pct', title='Top 15 riskiest states'), use_container_width=True)