import streamlit as st


DEFAULT_TOP_TEXT_AREA = "custom-text-area"
DEFAULT_HEADER_ANIMATION_AREA = "custom-animation-header-area"
DEFAULT_PROBLEM_STATEMENT_AREA = "custom-problem-statement-area"


def apply_default_custom_css():
    st.markdown(
        """
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Zen+Antique&display=swap" rel="stylesheet">
        <style>
        h1, h2, div, p {
            font-family: "Zen Antique", serif !important;
        }
        ."""
        + DEFAULT_TOP_TEXT_AREA
        + """ {
            background-color: #1e1e1e;  /* ダーク背景 */
            padding: 20px;
            border-radius: 10px;
            border: 2px solid #11567F;  /* グレーのボーダー */
            border-left: 5px solid #29B5E8;  /* Snowflake色のサイドライン */
            color: #ffffff;  /* 白文字 */
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
        ."""
        + DEFAULT_TOP_TEXT_AREA
        + """ p:last-child {
            margin-bottom: 0;
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

@st.cache_data
def header_animation(css_name: str = DEFAULT_HEADER_ANIMATION_AREA, image_file: str = 'pages/common/images/sky.png') -> None:
    import base64
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    st.html(
        f"""
        <div class="{css_name}">
        </div>
        <style>
        .{css_name} {{
            position:relative;
            overflow:hidden;
            box-shadow:0 4px 20px rgba(0, 0, 0, 0.2);
            background-image: url(data:image/{"png"};base64,{encoded_string});
            margin:0 auto;
            width:300px;
            height:30px;
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
            background-color:#1e50a2;
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


def display_problem_statement(html_message: str, css_name: str = DEFAULT_PROBLEM_STATEMENT_AREA, image_file: str = 'pages/common/images/quest.jpeg'):
    import base64
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    st.html(
        f"""
        <p>
            <div class="{css_name}">
            {html_message}
            </div>
            <style>
            .{css_name} .box {{
                border-radius: 10px;
            }}
            .{css_name} {{
                background-color: rgba(2, 2, 2, 0);
                background-image: url(data:image/{"png"};base64,{encoded_string});
                background-position: top;
                padding: 40px 5%;
                color: #000
            }}
            </style>
        </p>
        """
    )

@st.cache_data
def background_image(image_file: str = 'pages/common/images/sky.png', dark_mode : bool = True):
    import base64
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()

    dark_mode_css = ''
    if dark_mode:
        dark_mode_css = """
            .main::before {
                background-color: rgba(0,0,0,0.4);
                position: fixed;
                top: 0;
                right: 0;
                bottom: 0;
                left: 0;
                content: ' ';
        }
        """

    st.markdown(
    f"""
    <style>
    [data-testid="stAppViewContainer"] > .main {{
        background-image: url(data:image/{"png"};base64,{encoded_string});
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    {dark_mode_css}
    .stApp > header {{
        display: none;
    }}
    .stAlert{{
        background-color: rgba(0, 0, 0, 0.4);
        border-radius: 0.5rem;
    }}
    .stAlert p, .stTabs button p{{
        color: #fff !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
    )
