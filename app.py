import streamlit as st
from snowflake.snowpark import Session

from utils.utils import create_session


st.title("top page")
team_id = st.text_input("チーム名を入力してください")
if team_id:
    st.session_state.team_id = team_id
    st.session_state.snow_session = create_session(team_id)
elif "team_id" in st.session_state:
    st.info(f"あなたのチームIDは、{st.session_state.team_id}です。")
