import streamlit as st
from snowflake.snowpark import Session

from utils.utils import create_session, display_team_id_sidebar

TEAMS = [
    "",
    "Account_Admin",
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
    "Org_Admin",
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

if "team_id" in st.session_state:
    index = TEAMS.index(st.session_state.team_id)
else:
    index = 0
team_id = st.selectbox("チーム名を選択してください", options=TEAMS, index=index)
if team_id:
    st.session_state.team_id = team_id
    st.session_state.snow_session = create_session(team_id)
    st.info(f"あなたのチームIDは、{st.session_state.team_id}です。")

if st.button("問題を解く"):
    st.switch_page("pages/01_normal_problems.py")

display_team_id_sidebar()
