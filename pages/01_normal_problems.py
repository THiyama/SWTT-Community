import streamlit as st
import os
import importlib

from snowflake.snowpark import Session

from utils.utils import (
    check_is_clear,
    display_team_id_sidebar,
    display_team_id,
    get_session,
)
from utils.attempt_limiter import check_is_failed

st.title("通常問題")

session = get_session()
display_team_id_sidebar()
display_team_id()


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
