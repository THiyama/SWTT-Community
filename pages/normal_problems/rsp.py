import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark import functions as F

from utils.utils import save_table, init_state, clear_submit_button
from utils.attempt_limiter import check_is_failed, init_attempt, process_exceeded_limit
from utils.designs import header_animation, display_problem_statement

MAX_ATTEMPTS_MAIN = 2


class ABCConverter:
    def __init__(self):
        self.abc_to_answer = {"A": "DATA FOUNDATION", "B": "AI", "C": "APP"}
        self.answer_to_abc = {v: k for k, v in self.abc_to_answer.items()}

    def to_answer(self, abc: str) -> str:
        return self.abc_to_answer[abc]

    def to_abc(self, answer: str) -> str:
        return self.answer_to_abc[answer]


def add_new_command(session, team_id, hand):
    converter = ABCConverter()
    hand = converter.to_abc(hand)
    insert_query = f"""
    INSERT INTO hand_data (team_id, hand)
    VALUES ('{team_id}', '{hand}')
    """
    session.sql(insert_query).collect()


@st.cache_data
def selection_to_image(selection: str, failed: bool) -> str:
    if selection == "DATA FOUNDATION":
        key = "A"
    elif selection == "AI":
        key = "B"
    elif selection == "APP":
        key = "C"
    else:
        return ""
    if failed:
        key += "_failed"
    return f"pages/normal_problems/resources/rsp/selection_{key}.jpeg"


def present_quiz(tab_name: str, max_attempts: int) -> str:
    header_animation()
    st.header("Gain Insight!", divider="rainbow")

    display_problem_statement(
        """
                              <i>“人々の選択で世界は刻々と変化していき、AIデータクラウドはそれを克明に映し出す。
                              英雄は映し出された姿からすぐさま意味を紡ぎ出すだろう。”———一の賢者、トール</i><br />
                              <br />
                              現時点で最も投票が少ない選択肢に投票すればクリア。最も投票が少ない選択肢を予測するのだ！
                              """
    )

    st.write(f"投票回数の上限は {max_attempts}回です。")
    st.subheader("選択肢")
    options = ["DATA FOUNDATION", "AI", "APP"]
    answer = st.radio("Your choice:", options, index=None, key=f"{tab_name}_answer")
    image_file = selection_to_image(answer, False)
    if image_file:
        st.image(image_file, use_column_width=True)
    return answer


def process_answer(answer: str, state, session: Session) -> None:
    # 正解は最も少ない投票数の選択肢
    # hand_dataテーブルを読み込み
    converter = ABCConverter()
    hand_data = session.table("hand_data")
    hand_counts = (
        hand_data.groupBy("hand")
        .agg(F.count("*").alias("frequency"))
        .sort(F.col("frequency"), ascending=True)
    )

    # 投票結果の表示
    st.subheader("投票結果")
    # hands_countsとanswerを突合して、answerよりも投票数が多い選択肢が何個あるかを確認する
    hand_counts_df = hand_counts.toPandas()
    hand_counts_df["HAND"] = hand_counts_df["HAND"].apply(converter.to_answer)
    # answerの投票数を取得
    vote_counts = hand_counts_df[hand_counts_df["HAND"] == answer]["FREQUENCY"].values[
        0
    ]
    # answerよりも投票数が多い選択肢の数を取得
    lower_detected_times = len(
        hand_counts_df[hand_counts_df["FREQUENCY"] < vote_counts]
    )

    # デバッグのためにテーブルと選択肢を標準出力にダンプ
    # st.table(hand_counts_df)
    print(hand_counts_df.to_string())
    print(f"answer: {answer}")

    if lower_detected_times == 0:
        st.write("あなたは投票数が最も少ない選択肢を選びました！")
        image_file = selection_to_image(answer, False)
        if image_file:
            st.image(image_file, use_column_width=True)
    elif lower_detected_times == 1:
        st.write("あなたは投票数が2番目に多い選択肢を選びました。")
        image_file = selection_to_image(answer, True)
        if image_file:
            st.image(image_file, use_column_width=True)
    elif lower_detected_times >= 2:
        st.write("あなたは投票数が最も多い選択肢を選びました。")
        image_file = selection_to_image(answer, True)
        if image_file:
            st.image(image_file, use_column_width=True)

    # 投票が最も少ない選択肢が正解
    if lower_detected_times == 0:
        state["is_clear"] = True
        st.success("クイズに正解しました")
    else:
        state["is_clear"] = False
        st.error("不正解です")

    add_new_command(session, state["team_id"], answer)
    save_table(state, session)


def run(tab_name: str, session: Session):
    state = init_state(tab_name, session, MAX_ATTEMPTS_MAIN)
    main_attempt = init_attempt(
        max_attempts=MAX_ATTEMPTS_MAIN, tab_name=tab_name, session=session, key="main"
    )

    answer = present_quiz(tab_name, MAX_ATTEMPTS_MAIN)  # ★

    placeholder = st.empty()
    if check_is_failed(session, state):
        process_exceeded_limit(placeholder, state)
    elif placeholder.button("submit", key=f"{tab_name}_submit"):
        if main_attempt.check_attempt():
            if answer:
                process_answer(answer, state, session)  # ★
            else:
                st.warning("選択してください")

        else:
            process_exceeded_limit(placeholder, state)

    clear_submit_button(placeholder, state)
