import streamlit as st
from snowflake.snowpark import Session
from snowflake.cortex import Sentiment, Translate

from utils.utils import save_table, init_state, clear_submit_button
from utils.attempt_limiter import check_is_failed, init_attempt, process_exceeded_limit
from utils.designs import header_animation, display_problem_statement

MAX_ATTEMPTS_MAIN = 3


def present_quiz(tab_name: str, max_attempts: int) -> str:
    header_animation()
    st.header("Be Positive!", divider="rainbow")

    display_problem_statement("ポジティブな気分で、邪気を取り払うのだ！")
    st.write(f"回答回数の上限は {max_attempts}回です。")
    answer = st.text_input(
        "ポジティブメッセージを入力してください:", key=f"{tab_name}_answer"
    )

    return answer


def process_answer(answer: str, state, session: Session) -> None:
    correct_value = 0.8
    answer_sentiment = Sentiment(
        Translate(answer, "ja", "en", session=session), session=session
    )
    if answer_sentiment > correct_value:
        state["is_clear"] = True
        st.success(f"ポジティブ！あなたのポジティブは{answer_sentiment}でした。")
    else:
        state["is_clear"] = False
        st.error(
            f"ポジティブが足りません！あなたのポジティブは{answer_sentiment}でした。0.8 を超えるように頑張りましょう！"
        )

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
