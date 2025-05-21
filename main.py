import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import datetime
import os

# --- Google Sheets API認証 ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_path = "google-credentials.json"
if os.path.exists(creds_path):
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)
    sheet = client.open("202505-WSH-Form").worksheet("topics")
else:
    st.error("Google認証ファイルが見つかりません。google-credentials.json を配置してください。")
    sheet = None

# --- データ取得 ---
def load_data():
    if sheet:
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    return pd.DataFrame(columns=["Name", "Topic", "Votes"])  # パスワード列を削除

# --- データ保存 ---
def save_data(name, topic):  # パスワードパラメータを削除
    if sheet:
        sheet.append_row([name, topic, 1])  # パスワードを保存しない

# --- 投票数更新 ---
def update_votes(index, votes):
    if sheet:
        sheet.update_cell(index + 2, 3, votes)  # Google Sheetsは1行目がヘッダー
        st.rerun()  # ページをリロード

# --- カスタムCSSの追加 ---
st.markdown(
    """
    <style>
    /* ボタンの色を青に変更 */
    div.stButton > button {
        background-color: #007BFF; /* 青色 */
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
        border: none;
    }
    div.stButton > button:hover {
        background-color: #0056b3; /* ホバー時の色 */
    }

    /* テキスト入力欄のラベルを大きくする */
    label {
        font-size: 18px; /* サイズを1段階大きく */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- アンケートフォーム ---
st.title("WSH（週末共有会）")
st.title("トピック投稿・投票フォーム")
st.write("以下のフォームに、聞きたいことor話したいことを入力してください！")

# 入力欄
name = st.text_input("あなたの名前（下のリストには表示されないので、お気軽に！）")
topic = st.text_input("誰からどんな話を")

# ボタン
col1, col2, col3 = st.columns([2, 1, 2])
with col1:
    listen_button = st.button("聞きたい！")
with col2:
    st.write("### or")
with col3:
    talk_button = st.button("話したい！")

if listen_button:
    if name and topic:
        save_data(name, f"● {topic}【聞きたい！】")
        st.success("送信されました！【聞きたい！】")
    else:
        st.error("すべてのフィールドを入力してください。")

if talk_button:
    if name and topic:
        save_data(name, f"● {topic}【話したい！】")
        st.success("送信されました！【話したい！】")
    else:
        st.error("すべてのフィールドを入力してください。")

# 罫線とスペースの追加
st.markdown("---")  # 罫線
st.write("")  # 1行分のスペース

# --- 送信済みデータの表示 ---
st.write("### 投稿されたトピック案")
st.write("話題にしたいトピックに投票してください！")
st.write("間違って入力してしまったなど、削除したい場合はしょうさんまでお知らせください。")
st.write("")  # 1行分のスペース
data = load_data()

if not data.empty:
    for index, row in data.iterrows():
        col1, col2, col3 = st.columns([3, 1, 1])  # 列幅の比率を設定
        with col1:
            st.write(f"**{row['Topic']}**")
        with col2:
            st.write(f"👍 {row['Votes']}")
        with col3:
            if st.button("投票", key=f"vote_{index}"):
                new_votes = row['Votes'] + 1
                update_votes(index, new_votes)
                st.success("投票しました！")
else:
    st.write("まだ送信されたデータはありません。")