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
)
from utils.designs import (
    apply_default_custom_css,
    display_applied_message,
    background_image,
)


CLEAR_COUNT = 12

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

for problem_id in problem_ids:
    if f"{problem_id}_is_over_clear" not in st.session_state:
        st.session_state[f"{problem_id}_is_over_clear"] = False

chart_placeholder = st.empty()
st.write("\n\n\n")


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


update_chart()
