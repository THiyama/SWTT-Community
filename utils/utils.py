from datetime import datetime

import pandas as pd
import streamlit as st
import snowflake.snowpark.functions as F
from snowflake.snowpark import Session

from utils.attempt_limiter import check_is_failed, update_failed_status

import hashlib


TAB_TITLES = {
    "be_positive": "Sentiment のど自慢🎤",
    "whats_squad": "Community 魚すくい🐠",
    "chat_with_ai": "Cortex 占い🔮",
    "real_ice": "Open かき氷🧊",
    "rsp": "Unistore じゃんけん大会✋️",
    "nw_role": "Governance わさびたこ焼き🐙",
    "sort_services": "Time Travel シューティング🔫",
    "real_wanage": "Query 輪投げ➰️",
}


# Key: 表示されるチーム名
# Value: secretsに記載されているチームID
TEAMS = {
    "": "",
    "Account Admin": "Account_Admin",
    "Business Critical": "BusinessCritical",
    "Cortex": "Cortex",
    "Data Clean Room": "DataCleanRoom",
    "Enterprise Edition": "Enterprise_Edtion",
    "Fail-Safe": "Fail_Safe",
    "Git": "Git",
    "Horizon": "Horizon",
    "Iceberg": "Iceberg",
    "JDBC": "JAROWINKLER_SIMILARITY",
    "Knowledge": "Kafka",
    "Lineage": "Lineage",
    "Marketplace": "Marketplace",
    "Notebooks": "Notebooks",
    "OrgAdmin": "Org_Admin",
    "POLARIS": "POLARIS",
    "Quality Monitoring": "QualityMonitoring",
    "Resource Monitor": "ResouceMonitor",
    "Snowpark": "Snowpark",
    "Trust Center": "TrustCenter",
    "Universal Search": "UniversalSearch",
    "Validate": "VARCHAR",
    "WAREHOUSE": "WAREHOUSE",
    "X-Small": "XS",
}


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
        columns=[
            "team_id",
            "problem_id",
            "timestamp",
            "is_clear",
            "key",
            "max_attempts",
        ],
    )

    with st.spinner("クリスタルと通信中..."):
        # session.write_pandas(df, "SUBMIT2", auto_create_table=False, overwrite=False)
        snow_df = session.create_dataframe(df)
        snow_df.write.mode("append").save_as_table("submit2")

        if state["is_clear"]:
            # はじめてのクリアの場合、if文内のロジックを実行する。
            if not st.session_state[
                f"{state['problem_id']}_{state['team_id']}_is_clear"
            ]:
                update_clear_status(session, state)
                st.session_state[f"{state['problem_id']}_{state['team_id']}_title"] = (
                    "✅️ "
                    + st.session_state[
                        f"{state['problem_id']}_{state['team_id']}_title"
                    ]
                )
                st.session_state[
                    f"{state['problem_id']}_{state['team_id']}_is_clear"
                ] = True

                st.rerun()

        else:
            update_failed_status(session, state)
            # 制限に到達している かつ クリアしていない 場合、if文内のロジックを実行する。
            if (
                check_is_failed(session, state)
                and not st.session_state[
                    f"{state['problem_id']}_{state['team_id']}_is_clear"
                ]
            ):
                st.session_state[f"{state['problem_id']}_{state['team_id']}_title"] = (
                    "❌️ "
                    + st.session_state[
                        f"{state['problem_id']}_{state['team_id']}_title"
                    ]
                )
                st.session_state[
                    f"{state['problem_id']}_{state['team_id']}_is_failed"
                ] = True

                st.rerun()


def update_clear_status(session: Session, state: dict) -> None:
    submit_table = session.table("submit2")

    try:
        result = submit_table.filter(
            (F.col("team_id") == state["team_id"])
            & (F.col("problem_id") == state["problem_id"])
            & (F.col("is_clear") == True)
        ).count()

        st.session_state[f"{state['problem_id']}_{state['team_id']}_is_clear"] = (
            result > 0
        )

    except IndexError as e:
        print(e)
        st.session_state[f"{state['problem_id']}_{state['team_id']}_is_clear"] = False


def check_is_clear(session: Session, state: dict):
    # 呼び出し側が session 引数を入力しているため、一旦この関数では使っていないが定義する。
    return st.session_state[f"{state['problem_id']}_{state['team_id']}_is_clear"]


def reset_problem_status() -> None:
    team_id = TEAMS[get_team_id()]

    for problem_id in st.session_state["problem_ids"]:
        # if f"{problem_id}_{team_id}_title" in st.session_state:
        del st.session_state[f"{problem_id}_{team_id}_title"]

    st.session_state[f"{team_id}_display_preparation_message"] = True


def clear_submit_button(placeholder, state):
    if st.session_state[f"{state['problem_id']}_{state['team_id']}_is_clear"]:
        placeholder.empty()
        placeholder.success("そなたらはすでにクリスタルのパワーを取り戻している！")
    elif st.session_state[f"{state['problem_id']}_{state['team_id']}_is_failed"]:
        placeholder.empty()
        placeholder.error("そなたらはクリスタルのパワーを使い切ってしまったようだ。")


def string_to_hash_int(base_string: str) -> int:
    # 文字列をUTF-8でエンコードし、SHA256ハッシュを計算
    hash_object = hashlib.sha256(base_string.encode("utf-8"))
    hash_hex = hash_object.hexdigest()

    # 16進数の文字列を整数に変換
    hash_int = int(hash_hex, 16)

    # 整数値をシードとして返す
    return hash_int
