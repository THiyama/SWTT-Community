from datetime import datetime

import streamlit as st
import snowflake.snowpark.functions as F
from snowflake.snowpark import Session

from utils.utils import save_table, init


@st.cache_data
def show_img():
    col1, col2, col3, col4 = st.columns(4)
    col1.image("pages/normal_problems/resources/problem3/img1.png")
    col2.image("pages/normal_problems/resources/problem3/img2.png")
    col3.image("pages/normal_problems/resources/problem3/img3.png")
    col4.image("pages/normal_problems/resources/problem3/img4.png")


def run(tab_name: str, session: Session):
    state = init(tab_name, session)

    st.write("Question 3: CEOは誰！？")
    show_img()

    options = ["img1", "img2", "img3", "img4"]
    answer = st.selectbox("Your answer:", options=options, key=f"{tab_name}_answer")

    if st.button("submit", key=f"{tab_name}_submit"):
        if not answer:
            st.warn("選択してください")

        state["timestamp"] = datetime.now()
        st.write(f"You answered: {answer}")

        if answer == "img1":
            state["is_clear"] = True
            st.success("クイズに正解しました")

        else:
            state["is_clear"] = False
            st.error("不正解です")

        save_table(state, session)
