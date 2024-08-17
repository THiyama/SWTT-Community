import pandas as pd
import streamlit as st
import snowflake.snowpark.functions as F
from snowflake.snowpark import Session


@st.cache_resource
def create_session(team_id: str, is_info: bool = True) -> Session:
    try:
        session = st.connection(team_id, type="snowflake").session()
        if is_info:
            st.success("Snowflakeに接続できました。")
        return session
    except Exception as e:
        if is_info:
            st.error("Snowflakeに接続できませんでした。")
            st.write(e)


def check_is_clear(session: Session, state: dict):
    submit_table = session.table("submit")

    try:
        result = submit_table.filter(
            (F.col("team_id") == state["team_id"])
            & (F.col("problem_id") == state["problem_id"])
            & (F.col("is_clear") == True)
        ).count()
        return result > 0

    except Exception as e:
        st.write(e)
        return False


def save_table(state: dict, session: Session):
    df = pd.DataFrame([state], index=[0])
    new_column_order = ["team_id", "problem_id", "timestamp", "is_clear"]
    df = df[new_column_order]

    snow_df = session.create_dataframe(df)
    snow_df.write.mode("append").save_as_table("submit")
    st.success("結果をレコードに保存しました")
    st.rerun()


def init(tab_name: str, session: Session):
    state_name = f"{tab_name}_state"
    if state_name not in st.session_state:
        st.session_state.state = {}

    state = st.session_state.state

    state["team_id"] = session.get_current_user()[1:-1]
    state["problem_id"] = tab_name

    state["is_clear"] = check_is_clear(session, state)

    return state


def display_team_id_sidebar():
    with st.sidebar:
        try:
            st.write(f"チームID: {st.session_state.team_id}")
        except AttributeError as e:
            pass


def display_team_id():
    st.write(f"あなたが選択したチームIDは 「**{st.session_state.team_id}**」 です。")


def get_session():
    if "snow_session" not in st.session_state:
        st.warning("チームIDを選択してください。")
        st.stop()
    else:
        session = st.session_state.snow_session
        return session
