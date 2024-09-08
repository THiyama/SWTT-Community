import streamlit as st
from snowflake.snowpark import Session
from streamlit_image_select import image_select
from st_clickable_images import clickable_images

from utils.utils import save_table, init_state, clear_submit_button, string_to_hash_int
from utils.designs import header_animation, display_problem_statement
from utils.attempt_limiter import check_is_failed, init_attempt, process_exceeded_limit

import base64
import random

MAX_ATTEMPTS_MAIN = 3

# Data Sharing: FY18 -> 1
# Snowpark: 2022/01/xx -> 2
# Streamlit in Snowflake: 2023/12/01 -> 3
# Dynamic Tables: 2024/04/29 -> 5
# Native Apps Framework: 2024/01/31 -> 4
# Universal Search: 2024/06/03 -> 6

# この問題のタグ。session_stateで使う領域を区別するために使う
PROBLEM_TAG = "sort_services"
PROGRESS_TAG = "progress"
TRY_TIMES_TAG = "try_times"


# session_stateを初期化する
def init_session_state():
    if PROBLEM_TAG not in st.session_state:
        st.session_state[PROBLEM_TAG] = {}
        data = get_data(st.session_state.team_id)
        for row in data:
            image_tag = row[0]
            st.session_state[PROBLEM_TAG][image_tag] = -1
        st.session_state[PROBLEM_TAG][PROGRESS_TAG] = []
        st.session_state[PROBLEM_TAG][TRY_TIMES_TAG] = 0


# 選択順をリセットする
def reset_session_state():
    if PROBLEM_TAG not in st.session_state:
        st.session_state[PROBLEM_TAG] = {}
    data = get_data(st.session_state.team_id)
    for row in data:
        image_tag = row[0]
        st.session_state[PROBLEM_TAG][image_tag] = -1
    st.session_state[PROBLEM_TAG][PROGRESS_TAG] = []
    st.session_state[PROBLEM_TAG][TRY_TIMES_TAG] += 1


# 画像ファイルを開いてbase64エンコードする
@st.cache_data
def open_image_by_base64(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return encoded_string


# 選択肢を画像で表示する
def display_image(data, index, caption):
    # プレースホルダーを作成して画像を切り替える
    placeholder1 = st.empty()

    # タグを取得する
    image_tag = data[index][0]

    if st.session_state[PROBLEM_TAG][image_tag] < 0:
        with placeholder1.container():
            img = open_image_by_base64(data[index][3])
            key = f"{st.session_state[PROBLEM_TAG][TRY_TIMES_TAG]}_{PROBLEM_TAG}_{image_tag}_active"
            # 画像を表示してクリックイベントを取得
            st.session_state[PROBLEM_TAG][image_tag] = clickable_images([f"data:image/png;base64,{img}"], titles=[caption], div_style={"padding": "0px", "margin": "0px", "display": "flex", "justify-content": "center"}, img_style={"padding": "0px", "margin": "0px", "width": "240px"}, key=key)
            # キャプションを表示
            st.html(f"<div style=\"text-align: center; position: relative; transform: translateY(-80%)\">{caption}</div>")
    if st.session_state[PROBLEM_TAG][image_tag] == 0:
        with placeholder1.container():
            img = open_image_by_base64(data[index][4])
            key = f"{PROBLEM_TAG}_{image_tag}_inactive"
            # 画像を表示
            clickable_images([f"data:image/png;base64,{img}"], titles=[caption], div_style={"padding": "0px", "margin": "0px", "display": "flex", "justify-content": "center"}, img_style={"padding": "0px", "margin": "0px", "width": "240px"}, key=key)
            # キャプションを表示
            st.html(f"<div style=\"text-align: center; position: relative; transform: translateY(-80%)\">{caption}</div>")


# 問題用のデータセットを定義する
@st.cache_data
def get_data(team_id):
    base_list = [
        ["button1", "Data Sharing",           "1", "pages/normal_problems/resources/problem1/button1.png", "pages/normal_problems/resources/problem1/button1.inactive.png"],
        ["button2", "Snowpark",               "2", "pages/normal_problems/resources/problem1/button2.png", "pages/normal_problems/resources/problem1/button2.inactive.png"],
        ["button3", "Streamlit in Snowflake", "3", "pages/normal_problems/resources/problem1/button3.png", "pages/normal_problems/resources/problem1/button3.inactive.png"],
        ["button4", "Dynamic Tables",         "4", "pages/normal_problems/resources/problem1/button4.png", "pages/normal_problems/resources/problem1/button4.inactive.png"],
        ["button5", "Native Apps Framework",  "5", "pages/normal_problems/resources/problem1/button5.png", "pages/normal_problems/resources/problem1/button5.inactive.png"],
        ["button6", "Universal Search",       "6", "pages/normal_problems/resources/problem1/button6.png", "pages/normal_problems/resources/problem1/button6.inactive.png"],
    ]

    # base_lstをシャッフルする。randomのシード値をチームIDから生成する
    seed = string_to_hash_int(team_id)
    random.seed(seed)
    random.shuffle(base_list)

    # インデックスを振り直す
    for i, _ in enumerate(base_list):
        base_list[i][2] = f"{i + 1}"
    return base_list


# キャプションを生成する
def make_captions(data, show_hint):
    if show_hint:
        result = []
        for row in data:
            result.append(f"{row[2]}: {row[1]}")
        return result
    else:
        return [row[2] for row in data]


# 機能名を取得する
def get_name(data, button_id, show_hint=True):
    for row in data:
        if row[0] == button_id:
            if show_hint:
                return row[1]
            else:
                return row[2]


def present_quiz(tab_name: str, max_attempts: int) -> str:
    header_animation()
    st.header("クリスタルの記憶を呼び起こせ", divider="rainbow")

    display_problem_statement("""
                              <i>“過去を知る者は未来を見通す英雄である。
                              記憶の海を探れ。そしてSnowflakeの歴史の影を射貫いて真実の姿を露わにせよ。”———時の賢者、ヒロキ</i><br />
                              <br />
                              6つのサービスを一般提供(GA)になった順番にクリックしろ！
                              """)
    st.write(f"回答回数の上限は {max_attempts}回です。")

    # データを取得する
    data = get_data(st.session_state.team_id)

    # ヒントを表示するかどうかを選択するトグルボタン
    show_hint = st.toggle("ヒント：機能名を表示する", False)

    # キャプションを生成する
    captions = make_captions(data, show_hint)

    # 選択順をリセットする
    if st.button("選択をリセットする"):
        reset_session_state()

    # 画像を表示する
    col1, col2 = st.columns(2)
    with col1:
        display_image(data, 0, captions[0])
        display_image(data, 1, captions[1])
        display_image(data, 2, captions[2])
    with col2:
        display_image(data, 3, captions[3])
        display_image(data, 4, captions[4])
        display_image(data, 5, captions[5])

    # session_stateに格納されたボタンの状態から選択順を生成する
    if not PROGRESS_TAG in st.session_state[PROBLEM_TAG]:
        st.session_state[PROBLEM_TAG][PROGRESS_TAG] = []
    data = get_data(st.session_state.team_id)
    for row in data:
        image_tag = row[0]
        if st.session_state[PROBLEM_TAG][image_tag] == 0:
            if image_tag not in st.session_state[PROBLEM_TAG][PROGRESS_TAG]:
                st.session_state[PROBLEM_TAG][PROGRESS_TAG].append(image_tag)

    # 選択順を表示する
    order_text = ""
    for _, button_id in enumerate(st.session_state[PROBLEM_TAG][PROGRESS_TAG]):
        if order_text != "":
            order_text += " → "
        name = get_name(data, button_id, show_hint)
        order_text += f"{name}"
    for _ in range(len(st.session_state[PROBLEM_TAG][PROGRESS_TAG]), len(data)):
        if order_text != "":
            order_text += " → "
        order_text += f"???"
    st.write(order_text)

    return st.session_state[PROBLEM_TAG][PROGRESS_TAG]


def process_answer(answer: str, state, session: Session) -> None:
    # 回答が正しいかどうかを確認する
    correct_answer = ["button1", "button2", "button3", "button5", "button4", "button6"]
    corrected = True
    for i, ans in enumerate(answer):
        if ans != correct_answer[i]:
            corrected = False
    if len(answer) != len(correct_answer):
        corrected = False

    if corrected:
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

    # session_stateを初期化する
    init_session_state()

    answer = present_quiz(tab_name, MAX_ATTEMPTS_MAIN)  # ★

    # 回答する前提が揃っているかどうかを確認
    button_disabled = len(answer) < 5

    placeholder = st.empty()
    if check_is_failed(session, state):
        process_exceeded_limit(placeholder, state)
    elif placeholder.button("submit", key=f"{tab_name}_submit", disabled=button_disabled):
        if main_attempt.check_attempt():
            if answer:
                process_answer(answer, state, session)  # ★
            else:
                st.warning("選択してください")

        else:
            process_exceeded_limit(placeholder, state)

    clear_submit_button(placeholder, state)
