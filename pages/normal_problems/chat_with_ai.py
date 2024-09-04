from datetime import datetime
import streamlit as st
from snowflake.snowpark import Session
from utils.utils import save_table, init_state, clear_submit_button
from utils.attempt_limiter import check_is_failed, init_attempt, process_exceeded_limit
from snowflake.cortex import Complete as CompleteText


class ABCConverter:
    def __init__(self):
        self.abc_to_answer = {
            "😺": "snowflake-arctic",
            "🤡": "mixtral-8x7b",
            "👽": "mistral-7b",
        }
        self.answer_to_abc = {v: k for k, v in self.abc_to_answer.items()}

    def to_answer(self, abc: str) -> str:
        return self.abc_to_answer[abc]

    def to_abc(self, answer: str) -> str:
        return self.answer_to_abc[answer]


MAX_ATTEMPTS_MAIN = 3


def initialize_chat_history():
    if "messages" not in st.session_state:
        st.session_state.messages = []


def display_chat_history():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def ai_problem(tab_name: str, max_attempts: int, session: Session) -> str:
    st.write(
        "Question Cortex AI：3つのモデルと会話してその中からSnowflake Arcticだと思うものを選んで回答してください"
    )
    initialize_chat_history()
    converter = ABCConverter()
    abc_options = list(converter.abc_to_answer.keys())

    if "selected_abc" not in st.session_state:
        st.session_state.selected_abc = abc_options[0]

    selected_abc = st.selectbox("Select AI Model", abc_options, key="selected_abc")
    selected_model = converter.to_answer(selected_abc)

    # Define avatar dictionary
    avatars = {"snowflake-arctic": "😺", "mixtral-8x7b": "🤡", "mistral-7b": "👽"}

    if "answer_avatar" not in st.session_state:
        st.session_state.answer_avatar = None

    chat_container = st.container(height=600)
    for message in st.session_state.messages:
        with chat_container.chat_message(message["role"], avatar=message.get("avatar")):
            st.markdown(message["content"])

    prompt = st.chat_input("What is up?")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container.chat_message("user"):
            st.markdown(prompt)

        with chat_container.chat_message("assistant", avatar=avatars[selected_model]):
            response = call_cortex_ai_model(
                selected_model, prompt, st.session_state.messages, session
            )
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": response,
                    "avatar": avatars[selected_model],
                }
            )
            st.session_state.answer_avatar = avatars[selected_model]
            st.rerun()

    st.divider()
    st.write(f"回答回数の上限は {max_attempts}回です。")
    options = ["😺", "🤡", "👽"]
    answer = st.radio("Your answer:", options, index=None, key=f"{tab_name}_answer")
    return answer


def call_cortex_ai_model(model_name, prompt, context, session):
    context_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in context])
    prompt_text = f"""
    #命令文
    あなたは与えられたキャラクター設定について質問があった場合それを共有する情報アシスタントです。
    Context: {context_str}
    Question: {prompt}
    Answer:
    """
    response = CompleteText(model_name, prompt_text, stream=False, session=session)
    return response


def process_answer(answer: str, state, session: Session) -> None:
    correct_answer = "😺"
    if answer.lower() == correct_answer.lower():
        state["is_clear"] = True
        st.success("クイズに正解しました")
    else:
        state["is_clear"] = False
        st.error("不正解です")

    save_table(state, session)


def create_checkbox_group(group_name, options, tab_name):
    st.subheader(group_name)
    selected = []
    for option in options:
        if st.checkbox(option, key=f"{group_name}_{option}_{tab_name}"):
            selected.append(option)
    return selected


def run(tab_name: str, session: Session):
    state = init_state(tab_name, session, MAX_ATTEMPTS_MAIN)
    main_attempt = init_attempt(
        max_attempts=MAX_ATTEMPTS_MAIN, tab_name=tab_name, session=session, key="main"
    )

    answer = ai_problem(tab_name, MAX_ATTEMPTS_MAIN, session)

    placeholder = st.empty()
    if check_is_failed(session, state):
        process_exceeded_limit(placeholder, state)
    elif placeholder.button("submit", key=f"{tab_name}_submit"):
        if main_attempt.check_attempt():
            if answer:
                process_answer(answer, state, session)
            else:
                st.warning("選択してください")
        else:
            process_exceeded_limit(placeholder, state)

    clear_submit_button(placeholder, state)
