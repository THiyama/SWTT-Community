import streamlit as st
import os
import importlib

from snowflake.snowpark import Session

from utils.utils import check_is_clear


session = st.session_state.snow_session

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
    if check_is_clear(session, state):
        checker = ":white_check_mark: "
    else:
        checker = ""

    tab_titles.append(f"{checker}{problem_id}")
    problem_ids.append(problem_id)

st.session_state["problem_ids"] = problem_ids

selected_tab = st.tabs(tab_titles)

for i, tab_title in enumerate(problem_ids):
    with selected_tab[i]:
        tabs[tab_title].run(tab_title, session)
