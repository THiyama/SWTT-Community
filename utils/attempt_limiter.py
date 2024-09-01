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


def check_is_failed(session, state):
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
            return current_attempts >= max_attempts
        else:
            return False

    except IndexError as e:
        print(e)
        return False


def process_limit_success_error(placeholder, state):
    if (
        ":white_check_mark:"
        not in st.session_state[f"{state['problem_id']}_{state['team_id']}_title"]
    ):
        placeholder.error("そなたらはクリスタルのパワーを使い切ってしまったようだ。")

    else:
        placeholder.success("そなたらはすでにクリスタルのパワーを取り戻している！")


def process_exceeded_limit(placeholder, state):
    st.session_state[f"{state['problem_id']}_{state['team_id']}_disabled"] = True
    process_limit_success_error(placeholder, state)
