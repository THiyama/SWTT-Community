from datetime import datetime

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
        attempt_table = session.table("attempt")

        try:
            result = attempt_table.filter(
                (F.col("team_id") == self.team_id)
                & (F.col("problem_id") == self.problem_id)
                & (F.col("key") == self.key)
            ).count()

            if result < self.max_attempts:
                return True
            else:
                return False

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
                    "key": self.key,
                    "timestamp": datetime.now(),
                    "max_attempts": self.max_attempts,
                }
            ],
            index=[0],
        )
        new_column_order = ["team_id", "problem_id", "key", "timestamp", "max_attempts"]
        df = df[new_column_order]

        snow_df = session.create_dataframe(df)
        snow_df.write.mode("append").save_as_table("attempt", block=False)

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
    attempt_table = session.table("attempt")

    try:
        result = attempt_table.filter(
            (F.col("team_id") == state["team_id"])
            & (F.col("problem_id") == state["problem_id"])
            & (F.col("key") == "main")
        ).count()

        max_attempts = (
            attempt_table.filter(
                (F.col("team_id") == state["team_id"])
                & (F.col("problem_id") == state["problem_id"])
                & (F.col("key") == "main")
            )
            .select("max_attempts")
            .to_pandas()
        )

        if not max_attempts.empty:
            max_attempts = max_attempts.iloc[0, 0]
        else:
            return False

        if result < max_attempts:
            return False
        else:
            return True

    except IndexError as e:
        print(e)
        return False
