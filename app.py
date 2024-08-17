import streamlit as st
from snowflake.snowpark import Session

from utils.utils import create_session


TEAMS = [
    "",
    "AccountAdmin",
    "BusinessCritical",
    "Cortex",
    "DCR_DynamicTables",
    "Enterprise_Edtion",
    "Fail_Safe",
    "Git",
    "Horizon",
    "Iceberg",
    "JAROWINKLER_SIMILARITY",
    "Kafka",
    "Lineage",
    "Marketplace",
    "Notebooks",
    "OrgAdmin",
    "POLARIS",
    "QualityMonitoring",
    "ResouceMonitor",
    "Snowpark",
    "TrustCenter",
    "UniversalSearch",
    "VARCHAR",
    "WAREHOUSE",
    "XS",
]

st.title("top page")
team_id = st.selectbox("チーム名を選択してください", options=TEAMS)
if team_id:
    st.session_state.team_id = team_id
    st.session_state.snow_session = create_session(team_id)
elif "team_id" in st.session_state:
    st.info(f"あなたのチームIDは、{st.session_state.team_id}です。")
