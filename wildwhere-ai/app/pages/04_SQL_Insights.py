import sys
from pathlib import Path

import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[2]))
from analysis.sql_analysis import load_sql_queries, run_query
from app.components.layout import caveat, configure_page, page_header


configure_page("WildWhere AI | SQL Insights")
page_header(
    "SQL Insights",
    "Portfolio SQL queries run directly against the SQLite warehouse created by the ETL pipeline.",
)

queries = load_sql_queries()
selected = st.selectbox("Choose a query", list(queries.keys()))
st.code(queries[selected], language="sql")
st.dataframe(run_query(queries[selected]), use_container_width=True)
st.caption("These queries demonstrate SQL analytics over cleaned tables, not raw API responses.")
caveat()
