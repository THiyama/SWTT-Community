import streamlit as st
from snowflake.snowpark import Session

from utils.utils import save_table, init_state
from utils.attempt_limiter import check_is_failed, init_attempt

MAX_ATTEMPTS_MAIN = 3


def quiz(tab_name: str, max_attempts: int) -> str:
    st.write("Question 1: What is the capital of France?")
    st.write(f"回答回数の上限は {max_attempts}回です。")
    answer = st.text_input("Your answer:", key=f"{tab_name}_answer")

    return answer


def answer(answer: str, state, session: Session) -> None:
    correct_answer = "Paris"
    if answer.lower() == correct_answer.lower():
        state["is_clear"] = True
        st.success("クイズに正解しました")
    else:
        state["is_clear"] = False
        st.error("不正解です")

    save_table(state, session)


def run(tab_name: str, session: Session):
    state = init_state(tab_name, session)
    main_attempt = init_attempt(
        max_attempts=MAX_ATTEMPTS_MAIN, tab_name=tab_name, session=session, key="main"
    )

    answer = quiz(tab_name, MAX_ATTEMPTS_MAIN)

    if check_is_failed(session, state):
        st.error("回答回数の上限に達しています。")
    elif st.button("submit", key=f"{tab_name}_submit"):
        if main_attempt.add_attempt():
            if answer:
                answer(answer, state, session)
            else:
                st.warning("選択してください")
        else:
            st.error("回答回数の上限に達しています。")
