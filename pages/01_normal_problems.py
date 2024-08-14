import streamlit as st
import os
import importlib

problems_dir = 'pages/normal_problems'

problem_files = [f for f in os.listdir(problems_dir) if f.endswith('.py')]

tabs = {}
for file in problem_files:
    module_name = file[:-3] 
    module_path = f'pages.normal_problems.{module_name}' 
    tabs[module_name] = importlib.import_module(module_path)

tab_titles = list(tabs.keys())
selected_tab = st.tabs(tab_titles)

for i, tab_title in enumerate(tab_titles):
    with selected_tab[i]:
        tabs[tab_title].run(tab_title) 
