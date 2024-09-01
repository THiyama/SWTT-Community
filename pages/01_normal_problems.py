import streamlit as st
import os
import importlib

from snowflake.snowpark import Session

from utils.utils import (
    check_is_clear,
    display_page_titles_sidebar,
    display_team_id_sidebar,
    display_team_id,
    get_session,
    get_team_id,
)
from utils.designs import apply_default_custom_css, display_applied_message
from utils.attempt_limiter import check_is_failed

display_page_titles_sidebar()
st.title("⚔️挑戦の場")


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
    if f"{state['problem_id']}_{state['team_id']}_title" not in st.session_state:
        if check_is_clear(session, state):
            checker = ":white_check_mark: "
        elif check_is_failed(session, state):
            checker = ":x: "
        else:
            checker = ""
        st.session_state[f"{state['problem_id']}_{state['team_id']}_title"] = (
            checker + problem_id
        )

    tab_titles.append(
        st.session_state[f"{state['problem_id']}_{state['team_id']}_title"]
    )
    problem_ids.append(problem_id)

st.session_state["problem_ids"] = problem_ids

selected_tab = st.tabs(tab_titles)

for i, tab_title in enumerate(problem_ids):
    with selected_tab[i]:
        try:
            tabs[tab_title].run(tab_title, session)

        except AttributeError as e:
            st.write("in develop...")
            print(e)
