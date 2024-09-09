import pandas as pd
import plotly.express as px
import streamlit as st
import snowflake.snowpark.functions as F

from utils.utils import (
    display_team_id_sidebar,
    display_page_titles_sidebar,
    get_session,
    get_team_id,
    TAB_TITLES,
    TEAMS,
)
from utils.designs import (
    apply_default_custom_css,
    display_applied_message,
    background_image,
)


CLEAR_COUNT = 12
is_display_ranking = False
num_display_ranking = 3

st.title("📊挑戦状況")
background_image("pages/common/images/library.png")
display_page_titles_sidebar()
display_team_id_sidebar()
get_team_id()

with st.sidebar:
    display_on_pc = st.toggle("文字サイズ：大")

css_name = apply_default_custom_css()
message = "ここでは、現在の各チームの挑戦状況を確認できるぞ。\n\nそなたらもどんどん挑戦して進むのだ！"
display_applied_message(message, css_name)
st.write("")

session = get_session()


session = st.session_state.snow_session

try:
    problem_ids = st.session_state.problem_ids
except AttributeError as e:
    st.warning("一度挑戦の場を訪れるが良い。")
    if st.button("挑戦の場に行く"):
        st.switch_page("pages/01_normal_problems.py")
    st.stop()

pdf_problem_ids = pd.DataFrame(problem_ids, columns=["problem_id"])
pdf_problem_ids["problem_name"] = pdf_problem_ids["problem_id"].map(TAB_TITLES)

reversed_team_ids = {v: k for k, v in TEAMS.items()}

for problem_id in problem_ids:
    if f"{problem_id}_is_over_clear" not in st.session_state:
        st.session_state[f"{problem_id}_is_over_clear"] = False


st.subheader("問題ごとの正解チーム数")
chart_placeholder = st.empty()


@st.fragment(run_every="10s")
def update_chart():
    df = session.table("submit2")
    df_grouped = (
        df.select(F.col("problem_id"), F.col("team_id"), F.col("is_clear"))
        .group_by([F.col("problem_id"), F.col("team_id")])
        .agg(F.call_builtin("boolor_agg", F.col("is_clear")).alias("is_clear"))
        .group_by([F.col("problem_id")])
        .agg(F.count(F.col("is_clear")).alias("is_clear"))
        .to_pandas()
    )

    result = pdf_problem_ids.merge(
        df_grouped, left_on="problem_id", right_on="PROBLEM_ID", how="left"
    )

    result["IS_CLEAR"] = result["IS_CLEAR"].fillna(0)

    result["color"] = "#29B5E8"  # デフォルトカラー（薄いSnowflake色）

    # 雪を降らせる処理
    for index, row in result.iterrows():
        if row["IS_CLEAR"] >= CLEAR_COUNT:
            result.at[index, "color"] = "#c2e5f2"  # 色を薄い青色に変更

            # クリアカウントを超えた場合の通知の表示と雪を降らせる処理
            if not st.session_state[f"{row['problem_id']}_is_over_clear"]:
                st.success(f"「{row['problem_name'][:-1]}」の的屋が解放されたようだ！")
                st.snow()
                st.session_state[f"{row['problem_id']}_is_over_clear"] = True

    fig = px.bar(
        result,
        x="problem_name",
        y="IS_CLEAR",
        color="color",
        color_discrete_map="identity",
        labels={"problem_name": "", "IS_CLEAR": "正解チーム数"},
        category_orders={"problem_name": pdf_problem_ids["problem_name"].tolist()},
    )

    if display_on_pc:
        fig.update_xaxes(tickfont_size=20, tickangle=45)
        fig.update_yaxes(tickfont_size=16)
        fig.update_layout(height=600, width=1000)

        fig.update_layout(
            xaxis_range=[-0.5, 7.5],
            yaxis_range=[0, 25],
            plot_bgcolor="rgba(30, 30, 30, 0.7)",
            paper_bgcolor="rgba(10, 10, 10, 0.5)",
            yaxis_title_font_size=26,
        )

    else:
        fig.update_layout(
            xaxis_range=[-0.5, 7.5],
            yaxis_range=[0, 25],
            plot_bgcolor="rgba(30, 30, 30, 0.7)",
            paper_bgcolor="rgba(10, 10, 10, 0.5)",
        )

    fig.add_shape(
        type="line",
        x0=-0.5,
        x1=7.5,
        y0=CLEAR_COUNT,
        y1=CLEAR_COUNT,
        line=dict(color="#ff4b4b", width=3),
    )

    chart_placeholder.plotly_chart(fig, use_container_width=True)


@st.fragment(run_every="10s")
def update_ranking():
    df_submit = session.table("submit2")

    # Step 1: 各チームが最初に解けた問題を取得
    df_solved_problems = (
        df_submit.filter(F.col("is_clear") == True)
        .group_by(F.col("team_id"), F.col("problem_id"))
        .agg(F.min(F.col("timestamp")).alias("first_clear_time"))
    )

    # Step 2: チームごとの解けた問題数と解答速度（秒単位）を計算
    df_team_scores = df_solved_problems.group_by(F.col("team_id")).agg(
        F.count(F.col("problem_id")).alias("solved_problems_count"),
        F.sum(
            F.datediff(
                "second",
                F.to_timestamp(F.lit("2024-09-01 00:00:00")),
                F.col("first_clear_time"),
            )
        ).alias("total_solve_time"),
    )

    # Step 3: スコアを計算し、最終的な結果を取得
    pdf_final_scores = (
        df_team_scores.select(
            F.col("team_id"),
            F.col("solved_problems_count"),
            (
                F.col("solved_problems_count") * 100000
                - (F.col("total_solve_time") / 3600)
            ).alias("score"),
        )
        .order_by(F.col("score").desc())
        .limit(num_display_ranking)
        .to_pandas()
    )

    # 結果の表示
    pdf_final_scores["TEAM_NAME"] = pdf_final_scores["TEAM_ID"].map(reversed_team_ids)
    pdf_final_scores.index = range(1, len(pdf_final_scores) + 1)

    st.dataframe(pdf_final_scores["TEAM_NAME"])


update_chart()

if is_display_ranking:
    st.subheader(f"ランキング（Top{num_display_ranking}）")
    update_ranking()

st.write("\n\n\n")
