import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.functions import col, desc, count, min
from snowflake.snowpark.window import Window
import pandas as pd
import datetime
from utils.utils import save_table, init_state, clear_submit_button
from utils.attempt_limiter import check_is_failed, init_attempt, process_exceeded_limit

MAX_ATTEMPTS_MAIN = 1

class ABCConverter:
    def __init__(self):
        self.abc_to_answer = {
            "A": "DATA FOUNDATION",
            "B": "AI",
            "C": "APP"
        }
        self.answer_to_abc = {v: k for k, v in self.abc_to_answer.items()}

    def to_answer(self, abc: str) -> str:
        return self.abc_to_answer[abc]

    def to_abc(self, answer: str) -> str:
        return self.answer_to_abc[answer]
    

def add_new_command(session, team_id, hand):
    converter = ABCConverter()
    hand = converter.to_abc(hand)
    insert_query = f"""
    INSERT INTO hand_data (team_id, hand)
    VALUES ('{team_id}', '{hand}')
    """
    session.sql(insert_query).collect()
    print(f"新しいコマンドが追加されました: Team ID: {team_id}, Hand: {hand}")


def present_quiz(tab_name: str, max_attempts: int) -> str:
    st.write("Question 少数決：現時点で最も投票が少ない選択肢を予測して投票してください")
    st.write(f"投票回数の上限は {max_attempts}回です。")
    st.markdown("### 選択肢")
    options = ["DATA FOUNDATION", "AI", "APP"]
    answer = st.radio("Your answer:", options, index=None, key=f"{tab_name}_answer")
    return answer


def process_answer(answer: str, state, session: Session) -> None:
    # 正解は最も少ない投票数の選択肢
    # hand_dataテーブルを読み込み
    print("process_answer")
    converter = ABCConverter()
    hand_data = session.table("hand_data")
    hand_counts = hand_data.groupBy("hand").agg(count("*").alias("frequency"))
    min_freq = hand_counts.select(min("frequency")).collect()[0][0]
    min_freq_hands = hand_counts.filter(col("frequency") == min_freq).select("hand").collect()
    min_freq_hands = [row['HAND'] for row in min_freq_hands]

    min_freq_hands = [converter.to_answer(hand) for hand in min_freq_hands]

    #投票結果の表示
    st.write("投票結果")
    # hands_countsを表示
    hand_counts_df = hand_counts.toPandas()
    hand_counts_df["HAND"] = hand_counts_df["HAND"].apply(converter.to_answer)
    st.table(hand_counts_df)


    # 投票が最も少ない選択肢が正解
    if answer in min_freq_hands:
        state["is_clear"] = True
        st.success("クイズに正解しました")
    else:
        state["is_clear"] = False
        st.error("不正解です")

    add_new_command(session, state["team_id"], answer)
    save_table(state, session)


def run(tab_name: str, session: Session):
    state = init_state(tab_name, session, MAX_ATTEMPTS_MAIN)
    main_attempt = init_attempt(
        max_attempts=MAX_ATTEMPTS_MAIN, tab_name=tab_name, session=session, key="main"
    )

    answer = present_quiz(tab_name, MAX_ATTEMPTS_MAIN)  # ★

    placeholder = st.empty()
    if check_is_failed(session, state):
        process_exceeded_limit(placeholder, state)
    elif placeholder.button("submit", key=f"{tab_name}_submit"):
        if main_attempt.check_attempt():
            if answer:
                process_answer(answer, state, session)  # ★
            else:
                st.warning("選択してください")

        else:
            process_exceeded_limit(placeholder, state)

    clear_submit_button(placeholder, state)