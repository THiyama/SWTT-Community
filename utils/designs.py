import streamlit as st


DEFAULT_TOP_TEXT_AREA = "custom-text-area"
DEFAULT_HEADER_ANIMATION_AREA = "custom-animation-header-area"
DEFAULT_PROBLEM_STATEMENT_AREA = "custom-problem-statement-area"


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


def header_animation(css_name: str = DEFAULT_HEADER_ANIMATION_AREA) -> None:
    st.html(
        f"""
        <div class="{css_name}">
        </div>
        <style>
        .{css_name} {{
            position:relative;
            overflow:hidden;
            box-shadow:0 4px 20px rgba(0, 0, 0, 0.2);
            margin:0 auto;
            width:300px;
            height:30px;
            background-color:#f0f8ff;
            margin: 0 calc(50% - 50vw);
            width: 100vw;
        }}
        .{css_name}::before,
        .{css_name}::after {{
            position:absolute;
            left:-50%;
            width:200%;
            height:200%;
            content:"";
            background-color:#1e90ff;
            animation:wave linear 6s infinite;
        }}
        .{css_name}::before {{
            top:-150%;
            border-radius:50% 50% / 50% 70%;
        }}
        .{css_name}::after {{
            top:-146%;
            border-radius:30% 70% / 30% 50%;
            opacity:0.2;
            animation-delay:0.4s;
        }}
        @keyframes wave {{
            from {{
                transform:rotate(0deg);
            }}
            to {{
                transform:rotate(360deg);
            }}
        }}
        </style>
        """
    )


def display_problem_statement(html_message: str, css_name: str = DEFAULT_PROBLEM_STATEMENT_AREA):
    st.html(
        f"""
        <p>
            <div class="{css_name}">
            {html_message}
            </div>
            <style>
            .{css_name} {{
                background-color: rgb(190, 205, 214);
                padding: 30px;
            }}
            .{css_name} .box {{
                border-radius: 10px;
            }}
            .{css_name} {{
                background-color: rgb(240, 240, 250);
                transition: box-shadow 0.5s;
                color: #696969;
                box-shadow:
                    10px 10px 30px transparent,
                    -10px -10px 30px transparent,
                    inset 10px 10px 30px rgba(18, 47, 61, 0.5),
                    inset -10px -10px 30px rgba(248, 253, 255, 0.9);
            }}
            .{css_name}:hover {{
                color: #a0522d;
                box-shadow:
                    10px 10px 30px rgba(18, 47, 61, 0.5),
                    -10px -10px 30px rgba(248, 253, 255, 0.9),
                    inset 10px 10px 30px transparent,
                    inset -10px -10px 30px transparent;
            }}
            </style>
        </p>
        """
    )
