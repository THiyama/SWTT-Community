import streamlit as st
from snowflake.snowpark import Session

from utils.utils import save_table, init_state, clear_submit_button, string_to_hash_int
from utils.designs import header_animation, display_problem_statement
from utils.attempt_limiter import check_is_failed, init_attempt, process_exceeded_limit

import random

MAX_ATTEMPTS_MAIN = 2

# 問題用のデータセット
PROGRAM_LIST = ["Data Superheroes", "DATA Saber", "Snowflake Squad", "Data Polaris"]
PROGRAM_LOGOS = [
    "pages/normal_problems/resources/problem4/logo_data_superheroes.png",
    "pages/normal_problems/resources/problem4/logo_data_saber.png",
    "pages/normal_problems/resources/problem4/logo_snowflake_squad.png",
    "pages/normal_problems/resources/problem4/logo_data_polaris_fake.png",
]


# ランダムな並び順を取得する
@st.cache_data
def get_random_order(team_id: str) -> list:
    # チームIDからシード値を生成する
    seed = string_to_hash_int(team_id)
    random.seed(seed)
    # [1, 2, 3, 4]のリストをシャッフルする
    random.shuffle(order := [1, 2, 3, 4])
    return order


@st.cache_data
def display_squad_image():
    st.image(
        "pages/normal_problems/resources/problem4/squad.jpeg", use_column_width=True
    )


@st.cache_data
def display_logo_image(path: str):
    st.image(path, use_column_width=True)


def present_quiz(tab_name: str, max_attempts: int) -> str:
    header_animation()
    st.header("ヒーローを味方に", divider="rainbow")

    display_problem_statement("""
                              <i>“戦友とは魚のようなもの。釣り上げれば手に力を、心に勇気を得る。
                              それが大魚なら、なおさら。”———友の賢者、スズキ</i><br />
                              <br />
                              Snowflakeに関する活動を積極的に行った人を表彰するアンバサダープログラムが今年5月に新設されました。以下の写真の6人が表彰されている、そのプログラムはどれ？
                              """)
    display_squad_image()

    st.write(f"回答回数の上限は {max_attempts}回です。")

    # 選択肢をシャッフルする
    order = get_random_order(st.session_state.team_id)
    options = ["🐠" + PROGRAM_LIST[i - 1] for i in order]
    answer = st.radio("Your answer:", options, index=None)
    answer = answer[1:] if answer else None

    # 選択肢に応じた画像を表示する
    if answer:
        for i in range(4):
            if answer == PROGRAM_LIST[i]:
                display_logo_image(PROGRAM_LOGOS[i])

    return answer


def process_answer(answer: str, state, session: Session) -> None:
    correct_answer = "Snowflake Squad"
    if answer.lower() == correct_answer.lower():
        state["is_clear"] = True
        st.success("クイズに正解しました")
    else:
        state["is_clear"] = False
        st.error("不正解です")

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
