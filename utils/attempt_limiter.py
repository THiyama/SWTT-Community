from datetime import datetime

import streamlit as st
import pandas as pd
from snowflake.snowpark import Session
from snowflake.snowpark import functions as F


class AttemptLimiter:
    def __init__(
        self,
        max_attempts: int,
        problem_id: str,
        team_id: str,
        session: Session,
        key: str = "main",
    ):
        self.session = session
        self.max_attempts = max_attempts
        self.problem_id = problem_id
        self.team_id = team_id
        self.key = key

    def __check_attempt_table(self) -> bool:
        session = self.session
        attempt_table = session.table("submit2")

        try:
            current_attempts = attempt_table.filter(
                (F.col("team_id") == self.team_id)
                & (F.col("problem_id") == self.problem_id)
                & (F.col("key") == self.key)
            ).count()

            return current_attempts < self.max_attempts

        except IndexError as e:
            print(e)
            return False

    def __add_attempt_table(self) -> None:
        session = self.session

        df = pd.DataFrame(
            [
                {
                    "team_id": self.team_id,
                    "problem_id": self.problem_id,
                    "timestamp": datetime.now(),
                    "is_clear": None,
                    "key": self.key,
                    "max_attempts": self.max_attempts,
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
        snow_df.write.mode("append").save_as_table("submit2", block=False)

    def check_attempt(self) -> bool:
        return self.__check_attempt_table()

    def add_attempt(self):
        self.__add_attempt_table()


def init_attempt(
    max_attempts: int, tab_name: str, session: Session, key: str = "main"
) -> AttemptLimiter:
    problem_id = tab_name
    team_id = session.get_current_user()[1:-1]

    return AttemptLimiter(max_attempts, problem_id, team_id, session, key)


def update_failed_status(session: Session, state: dict) -> None:
    attempt_table = session.table("submit2")

    try:
        query_result = (
            attempt_table.filter(
                (F.col("team_id") == state["team_id"])
                & (F.col("problem_id") == state["problem_id"])
                & (F.col("key") == "main")
            )
            .select("max_attempts")
            .collect()
        )

        if query_result:
            max_attempts = query_result[0]["MAX_ATTEMPTS"]
            current_attempts = len(query_result)
            st.session_state[f"{state['problem_id']}_{state['team_id']}_is_failed"] = (
                current_attempts >= max_attempts
            )
        else:
            st.session_state[f"{state['problem_id']}_{state['team_id']}_is_failed"] = (
                False
            )

    except IndexError as e:
        print(e)
        st.session_state[f"{state['problem_id']}_{state['team_id']}_is_failed"] = False


def check_is_failed(session: Session, state: dict) -> None:
    # 呼び出し側が session 引数を入力しているため、一旦この関数では使っていないが定義する。
    return st.session_state[f"{state['problem_id']}_{state['team_id']}_is_failed"]


def process_exceeded_limit(placeholder, state):
    st.session_state[f"{state['problem_id']}_{state['team_id']}_is_failed"] = True

    # 回答制限に到達した際に、その回答がクリアだったかどうかで表示する内容を調整する。
    if st.session_state[f"{state['problem_id']}_{state['team_id']}_is_clear"]:
        placeholder.success("そなたらはクリスタルのパワーを取り戻すことができた！")

    else:
        placeholder.error("そなたらはクリスタルのパワーを使い切ってしまったようだ。")
