import streamlit as st
import os
import importlib

from utils.utils import (
    check_is_clear,
    display_page_titles_sidebar,
    display_team_id_sidebar,
    get_session,
    get_team_id,
)
from utils.designs import (
    apply_default_custom_css,
    display_applied_message,
    background_image,
)
from utils.attempt_limiter import check_is_failed


TAB_TITLES = {
    "be_positive": "Sentiment のど自慢🎤　",
    "problem4": "Community 魚すくい🐠　",
    "chat_with_ai": "Cortex 占い🔮　",
    "rsp": "Unistore じゃんけん大会✋️　",
    "nw_role": "Governance わさびたこ焼き🐙　",
    "problem1": "Time Travel シューティング🔫　",
}

display_page_titles_sidebar()
st.title("⚔️挑戦の場")
background_image("pages/common/images/wars.png")

team_id = get_team_id()
css_name = apply_default_custom_css()
message = f"""
    ほう、そなたらがかの **{team_id}** チームか。

    さあ、8つの知恵の的屋に挑戦し、クリスタルの力を取り戻すのだ
    """
display_applied_message(message, css_name)

st.write("")

session = get_session()
display_team_id_sidebar()


problems_dir = "pages/normal_problems"
problem_files = [f for f in os.listdir(problems_dir) if f.endswith(".py")]

tabs = {}
for file in problem_files:
    module_name = file[:-3]
    module_path = f"pages.normal_problems.{module_name}"
    tabs[module_name] = importlib.import_module(module_path)


tab_titles = []
problem_ids = []
state = {}
state["team_id"] = session.get_current_user()[1:-1]
for problem_id in tabs.keys():
    state["problem_id"] = problem_id

    # タブ名、タブステートの初期化
    if f"{state['problem_id']}_{state['team_id']}_title" not in st.session_state:

        # クリアフラグを追加するIFステートメント
        if check_is_clear(session, state):
            checker = ":white_check_mark: "
            st.session_state[f"{state['problem_id']}_{state['team_id']}_is_clear"] = (
                True
            )
            st.session_state[f"{state['problem_id']}_{state['team_id']}_is_failed"] = (
                False
            )
        elif check_is_failed(session, state):
            checker = ":x: "
            st.session_state[f"{state['problem_id']}_{state['team_id']}_is_clear"] = (
                False
            )
            st.session_state[f"{state['problem_id']}_{state['team_id']}_is_failed"] = (
                True
            )
        else:
            checker = ""
            st.session_state[f"{state['problem_id']}_{state['team_id']}_is_clear"] = (
                False
            )
            st.session_state[f"{state['problem_id']}_{state['team_id']}_is_failed"] = (
                False
            )

        # タブタイトル（物理名）にフラグを追加する処理
        try:
            st.session_state[f"{state['problem_id']}_{state['team_id']}_title"] = (
                checker + TAB_TITLES[problem_id]
            )
        except KeyError as e:
            # TAB_TITLESにない問題はスキップする。
            continue

    # タブタイトル（物理名）の追加
    tab_titles.append(
        st.session_state[f"{state['problem_id']}_{state['team_id']}_title"]
    )
    problem_ids.append(problem_id)

st.session_state["problem_ids"] = problem_ids

selected_tab = st.tabs(tab_titles)

for i, tab_title in enumerate(problem_ids):
    with selected_tab[i]:
        tabs[tab_title].run(tab_title, session)
