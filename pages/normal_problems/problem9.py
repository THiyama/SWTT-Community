from datetime import datetime
import streamlit as st
from snowflake.snowpark import Session
from utils.utils import save_table, init_state


def create_checkbox_group(group_name, options, tab_name):
    st.subheader(group_name)
    selected = []
    for option in options:
        if st.checkbox(option, key=f"{group_name}_{option}_{tab_name}"):
            selected.append(option)
    return selected


def run(tab_name: str, session: Session):
    state = init_state(tab_name, session)

    st.title("グループ別複数選択アプリケーション")

    # 4つのグループとその選択肢を定義
    groups = {
        "販売部": ["🏠監査_WH", "🏠分析_1_WH", "🏠分析_2_WH"],
        "セキュリティ部": ["🏠監査用_WH", "🏠SEC_WH", "🏠処理_WH"],
        "情報システム部": ["🏠監査", "🏠teiki_WH"],
        "資材部": ["🏠監査_1_WH", "🏠監査_2_WH", "🏠PROJ_WH", "🏠集計_WH"],
    }

    # 各グループの選択状況を保存する辞書
    selections = {}

    # 2列レイアウトを作成
    col1, col2 = st.columns(2)

    for i, (group_name, options) in enumerate(groups.items()):
        # 偶数のグループは左列、奇数のグループは右列に配置
        with col1 if i % 2 == 0 else col2:
            selections[group_name] = create_checkbox_group(
                group_name, options, tab_name
            )
    st.write("---")
    # 全体の選択状況をサマリーとして表示
    st.subheader("選択中")
    all_selections = [f"{option}" for group in selections.values() for option in group]
    if all_selections:
        st.write(", ".join(all_selections))
    else:
        st.write("選択された項目はありません")

    if st.button("submit", key=f"{tab_name}_submit"):
        if not all_selections:
            # st.warn("選択してください")
            pass
        state["timestamp"] = datetime.now()

        if set(all_selections) == set(
            ["🏠監査_WH", "🏠監査用_WH", "🏠監査", "🏠監査_1_WH", "🏠監査_2_WH"]
        ):
            state["is_clear"] = True
            st.success("クイズに正解しました")

        else:
            state["is_clear"] = False
            st.error("不正解です")

        save_table(state, session)
