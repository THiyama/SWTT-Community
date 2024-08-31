import streamlit as st
from streamlit_image_select import image_select

# 問題用のデータセットを定義する
@st.cache_data
def get_data():
    lst = [
        ["button0", "",                       "",  "pages/normal_problems/resources/problem1/none.png",    "pages/normal_problems/resources/problem1/button1.none.png"],
        ["button1", "Data Sharing",           "1", "pages/normal_problems/resources/problem1/button1.png", "pages/normal_problems/resources/problem1/button1.inactive.png"],
        ["button2", "Snowpark",               "2", "pages/normal_problems/resources/problem1/button2.png", "pages/normal_problems/resources/problem1/button2.inactive.png"],
        ["button3", "Streamlit in Snowflake", "3", "pages/normal_problems/resources/problem1/button3.png", "pages/normal_problems/resources/problem1/button3.inactive.png"],
        ["button4", "Dynamic Tables",         "4", "pages/normal_problems/resources/problem1/button4.png", "pages/normal_problems/resources/problem1/button4.inactive.png"],
        ["button5", "Native Apps Framework",  "5", "pages/normal_problems/resources/problem1/button5.png", "pages/normal_problems/resources/problem1/button5.inactive.png"],
        # ["button6", "Universal Search",       "6", "pages/normal_problems/resources/problem1/button6.png", "pages/normal_problems/resources/problem1/button6.inactive.png"],
    ]
    # TODO: チームごとに異なる順番で表示するための処理を追加する
    return lst

# キャプションを生成する
def make_captions(data, show_hint):
    if show_hint:
        result = []
        for row in data:
            if row[1] == "":
                result.append(row[2])
            else:
                result.append(f"{row[2]}: {row[1]}")
        return result
    else:
        return [row[2] for row in data]

# 画像一覧を取得する
def get_images(data, selected_list=[]):
    result = []
    for row in data:
        if row[0] in selected_list:
            result.append(row[4])
        else:
            result.append(row[3])
    return result

# 機能名を取得する
def get_name(data, button_id, show_hint=True):
    for row in data:
        if row[0] == button_id:
            if show_hint:
                return row[1]
            else:
                return row[2]

# データを取得する
data = get_data()

# ヒントを表示するかどうかを選択するトグルボタン
show_hint = st.toggle("ヒント：機能名を表示する", False)

# キャプションを生成する
captions = make_captions(data, show_hint)

# 選択順をリセットする
if st.button("選択をリセットする"):
    del st.session_state.problem1

# 画像表示のために選択順を一時的に取得する。選択順の初期化や追加は後で行う
if not "problem1" in st.session_state:
    selected_list = []
else:
    selected_list = st.session_state.problem1

# 画像を選択する
img = image_select(
    label="",
    images=get_images(data, selected_list),
    captions=captions,
    use_container_width=False,
)

# 取得した画像のパスからボタンIDを取得
button_id = img.split("/")[-1].split(".")[0]

# セッション変数に選択順があるかどうかを確認
if not "problem1" in st.session_state:
    st.session_state.problem1 = []
else:
    # 選択したボタンIDを選択順に追加する
    if button_id != "none":
        if button_id not in st.session_state.problem1:
            st.session_state.problem1.append(button_id)

# 選択順を表示する
order_text = ""
for i, button_id in enumerate(st.session_state.problem1):
    if order_text != "":
        order_text += " → "
    name = get_name(data, button_id, show_hint)
    order_text += f"{name}"
for i in range(len(st.session_state.problem1), 5):
    if order_text != "":
        order_text += " → "
    order_text += f"???"
st.write(order_text)

# 回答する
button_disable = len(st.session_state.problem1) < 5
if st.button("回答する", disabled=button_disable):
    st.snow()


def run(tab_name: str, session: Session):
    pass
