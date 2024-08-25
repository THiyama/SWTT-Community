from datetime import datetime

import streamlit as st
import snowflake.snowpark.functions as F
from snowflake.snowpark import Session

from utils.utils import save_table, init_state


def run(tab_name: str, session: Session):
    state = init_state(tab_name, session)

    st.write(
        "Question 2: select * 〇〇 from <tables>; で、〇〇のオプションとして存在しないものはどれ？"
    )
    options = ["EXCLUDE", "RENAME", "ILIKE", "REPLACE", "CAST"]
    answer = st.selectbox("Your answer:", options=options, key=f"{tab_name}_answer")

    if st.button("submit", key=f"{tab_name}_submit"):
        if not answer:
            st.warn("選択してください")

        state["timestamp"] = datetime.now()
        st.write(f"You answered: {answer}")

        if answer == "RENAME":
            state["is_clear"] = True
            st.success("クイズに正解しました")

        else:
            state["is_clear"] = False
            st.error("不正解です")

        save_table(state, session)
