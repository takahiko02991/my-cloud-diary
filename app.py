import streamlit as st
from supabase import create_client

# 1. 自分の情報に書き換え
url = "https://dvpjezukrfeztvldqtws.supabase.co" 
# メモした「b_publishable...」の文字列をここに入れる
key = "sb_publishable_hwnIVCH5FFQlxAcGawoq-A_EfG5_Arh" 

supabase = create_client(url, key)

# ページの設定（スマホで見やすいように）
st.set_page_config(page_title="My Cloud Diary", page_icon="📝")

# タイトルのデザイン
st.markdown("<h1 style='text-align: center; color: #4A90E2;'>📝 My Cloud Diary</h1>", unsafe_allow_html=True)

# --- 入力エリア (カード風に囲う) ---
with st.container(border=True):
    st.subheader("今日のできごとは？")
    content = st.text_area("内容を入力...", placeholder="今日は〇〇をしたよ！", label_visibility="collapsed")
    submitted = st.button("日記を保存する", use_container_width=True, type="primary")
    
    if submitted and content:
        supabase.table("diary").insert({"content": content}).execute()
        st.success("クラウドに保存しました！")
        st.rerun()

# --- 一覧表示エリア ---
st.header("📖 これまでの日記")

# データを取得（最新順）
response = supabase.table("diary").select("*").order("created_at", desc=True).execute()
rows = response.data

for row in rows:
    # 各日記を枠(カード)で囲む
    with st.container(border=True):
        # 日付とゴミ箱ボタンを横に並べる
        col1, col2 = st.columns([0.85, 0.15])
        
        with col1:
            date_str = row['created_at'].split('T')[0]
            st.caption(f"📅 {date_str}")
        
        with col2:
            # 削除ボタン（ゴミ箱アイコン風）
            if st.button("🗑️", key=f"del_{row['id']}"):
                supabase.table("diary").delete().eq("id", row['id']).execute()
                st.toast("削除しました！")
                st.rerun()
        
        # 本文の表示
        st.write(row['content'])

