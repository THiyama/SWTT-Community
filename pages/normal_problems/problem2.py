import streamlit as st

def run(tab_name):
    st.write("Question 2: What is 2 + 2?")
    answer = st.text_input("Your answer:", key=f"{tab_name}_answer")
    if answer:
        st.write(f"You answered: {answer}")
