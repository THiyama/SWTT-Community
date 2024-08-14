import streamlit as st

def run(tab_name):
    st.write("Question 1: What is the capital of France?")
    answer = st.text_input("Your answer:", key=f"{tab_name}_answer")
    if answer:
        st.write(f"You answered: {answer}")
