import streamlit as st
from supabase import create_client
from datetime import datetime
import pytz # タイムゾーンを扱うライブラリ

# 1. 接続設定（Secretsから読み込み）
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# ページ設定
st.set_page_config(page_title="My Cloud Diary", page_icon="🌤️")

# --- 時刻と天気の表示エリア ---
# 日本時間を取得
jp_tz = pytz.timezone('Asia/Tokyo')
now = datetime.now(jp_tz)
current_time = now.strftime("%Y/%m/%d %H:%M:%S")

st.markdown(f"### 📍 Kitakyushu, Japan")
st.markdown(f"#### 🕒 {current_time}")

# タイトル
st.markdown("<h1 style='text-align: center; color: #4A90E2;'>📝 My Cloud Diary</h1>", unsafe_allow_html=True)

# --- 入力エリア ---
with st.container(border=True):
    content = st.text_area("今日のできごとは？", placeholder="今日は〇〇をしたよ！")
    submitted = st.button("日記を保存する", use_container_width=True, type="primary")
    
    if submitted and content:
        # 投稿内容と一緒に「投稿時間」も保存（Supabase側で自動設定もできますが、アプリ側から送るのが確実です）
        supabase.table("diary").insert({"content": content}).execute()
        st.success("クラウドに保存しました！")
        st.rerun()

# --- 一覧表示エリア ---
st.header("📖 これまでの日記")

response = supabase.table("diary").select("*").order("created_at", desc=True).execute()
rows = response.data

for row in rows:
    with st.container(border=True):
        col1, col2 = st.columns([0.85, 0.15])
        with col1:
            # 時刻まで細かく表示するように修正
            dt = datetime.fromisoformat(row['created_at'].replace('Z', '+00:00')).astimezone(jp_tz)
            st.caption(f"📅 {dt.strftime('%Y/%m/%d %H:%M')}")
        with col2:
            if st.button("🗑️", key=f"del_{row['id']}"):
                supabase.table("diary").delete().eq("id", row['id']).execute()
                st.rerun()
        st.write(row['content'])

