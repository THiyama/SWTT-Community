from datetime import datetime

import streamlit as st
import snowflake.snowpark.functions as F
from snowflake.snowpark import Session

from utils.utils import save_table, init


def run(tab_name: str, session: Session):
    state = init(tab_name, session)

    st.write("Question 1: What is the capital of France?")
    answer = st.text_input("Your answer:", key=f"{tab_name}_answer")

    if st.button("submit", key=f"{tab_name}_submit"):
        state["timestamp"] = datetime.now()
        st.write(f"You answered: {answer}")

        if answer == "Pari":
            state["is_clear"] = True
            st.success("クイズに正解しました")

        else:
            state["is_clear"] = False
            st.error("不正解です")

        save_table(state, session)
