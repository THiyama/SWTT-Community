from datetime import datetime

import pandas as pd
import streamlit as st
import snowflake.snowpark.functions as F
from snowflake.snowpark import Session

from utils.attempt_limiter import check_is_failed, process_limit_success_error


@st.cache_resource
def create_session(team_id: str, _placeholder, is_info: bool = True) -> Session:
    try:
        session = st.connection(team_id, type="snowflake").session()
        if is_info:
            st.success("データクリスタルとのリンクに成功したぞ。次なる試練へ進むのだ！")
        return session
    except Exception as e:
        if is_info:
            _placeholder.empty()
            _placeholder.error("ふむ、、なにか問題が発生したようだな")
            print(e)


def get_session():
    if "snow_session" not in st.session_state:
        st.warning("そなたらは、まだチームとして誓いが結ばれていないようだの・・・。")
        if st.button("チーム結集に戻る"):
            st.switch_page("app.py")
        st.stop()
    else:
        session = st.session_state.snow_session
        return session


def display_page_titles_sidebar():
    with st.sidebar:
        st.page_link("app.py", label="Gather Teams", icon="👥")
        st.page_link("pages/01_normal_problems.py", label="Challenge Arena", icon="⚔️")
        st.page_link(
            "pages/03_aggregate_results.py", label="Overall Progress", icon="📊"
        )


def display_team_id_sidebar():
    with st.sidebar:
        try:
            st.divider()
            if "team_id" in st.session_state:
                st.write(f"チーム名: {st.session_state.team_id}")
            else:
                st.write(f"チーム名: 未結成")
        except AttributeError as e:
            print(e)


def display_team_id():
    st.write(f"そなたらのチームは 「**{st.session_state.team_id}**」 だ。")


def get_team_id():
    if "team_id" not in st.session_state:
        st.warning("そなたらは、まだチームとして誓いが結ばれていないようだの・・・。")
        if st.button("チーム結集に戻る"):
            st.switch_page("app.py")
        st.stop()
    else:
        return st.session_state.team_id


def init_state(tab_name: str, session: Session, max_attempts: int = 3):
    state_name = f"{tab_name}_state"
    if state_name not in st.session_state:
        st.session_state.state = {}

    state = st.session_state.state

    state["team_id"] = session.get_current_user()[1:-1]
    state["problem_id"] = tab_name

    state["is_clear"] = check_is_clear(session, state)
    state["max_attempts"] = max_attempts

    return state


def save_table(state: dict, session: Session):
    df = pd.DataFrame(
        [
            {
                "team_id": state["team_id"],
                "problem_id": state["problem_id"],
                "timestamp": datetime.now(),
                "is_clear": state["is_clear"],
                "key": "main",
                "max_attempts": state["max_attempts"],
            }
        ],
        index=[0],
    )
    new_column_order = [
        "team_id",
        "problem_id",
        "timestamp",
        "is_clear",
        "key",
        "max_attempts",
    ]
    df = df[new_column_order]

    snow_df = session.create_dataframe(df)

    if state["is_clear"]:
        snow_df.write.mode("append").save_as_table("submit2")
        if (
            ":white_check_mark:"
            not in st.session_state[f"{state['problem_id']}_{state['team_id']}_title"]
        ):
            st.session_state[f"{state['problem_id']}_{state['team_id']}_title"] = (
                ":white_check_mark: "
                + st.session_state[f"{state['problem_id']}_{state['team_id']}_title"]
            )

    else:
        snow_df.write.mode("append").save_as_table("submit2")

        if (
            check_is_failed(session, state)
            and ":white_check_mark:"
            not in st.session_state[f"{state['problem_id']}_{state['team_id']}_title"]
        ):
            st.session_state[f"{state['problem_id']}_{state['team_id']}_title"] = (
                ":x: "
                + st.session_state[f"{state['problem_id']}_{state['team_id']}_title"]
            )
            st.session_state[f"{state['problem_id']}_{state['team_id']}_disabled"] = (
                True
            )


def check_is_clear(session: Session, state: dict):
    submit_table = session.table("submit2")

    try:
        result = submit_table.filter(
            (F.col("team_id") == state["team_id"])
            & (F.col("problem_id") == state["problem_id"])
            & (F.col("is_clear") == True)
        ).count()
        return result > 0

    except IndexError as e:
        print(e)
        return False


def clear_submit_button(placeholder, state):
    if f"{state['problem_id']}_{state['team_id']}_disabled" not in st.session_state:
        st.session_state[f"{state['problem_id']}_{state['team_id']}_disabled"] = False
    elif st.session_state[f"{state['problem_id']}_{state['team_id']}_disabled"]:
        placeholder.empty()
        process_limit_success_error(placeholder, state)
