import streamlit as st


DEFAULT_TOP_TEXT_AREA = "custom-text-area"


def apply_default_custom_css():
    st.markdown(
        """
        <style>
        ."""
        + DEFAULT_TOP_TEXT_AREA
        + """ {
            background-color: #1e1e1e;  /* ダーク背景 */
            padding: 20px;
            border-radius: 10px;
            border: 2px solid #11567F;  /* グレーのボーダー */
            border-left: 5px solid #29B5E8;  /* Snowflake色のサイドライン */
            color: #ffffff;  /* 白文字 */
            font-family: 'Cinzel', serif;  /* 古代っぽいフォント */
            font-size: 16px;
            line-height: 1.6;
        }
        ."""
        + DEFAULT_TOP_TEXT_AREA
        + """ h3 {
            color: #5cc5eb;  /* 淡いSnowflake色 */
            text-shadow: 2px 2px #000000;  /* 影を付けて浮き上がる効果 */
        }
        ."""
        + DEFAULT_TOP_TEXT_AREA
        + """ strong {
            color: #5cc5eb;  /* 強調部分も淡いSnowflake色に */
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    return DEFAULT_TOP_TEXT_AREA


def display_applied_message(message: str, css_name: str = DEFAULT_TOP_TEXT_AREA):
    if css_name == DEFAULT_TOP_TEXT_AREA:
        apply_default_custom_css()
    else:
        apply_default_custom_css()

    st.markdown(
        f"""
        <div class='{css_name}'>
        {message}
        """,
        unsafe_allow_html=True,
    )
