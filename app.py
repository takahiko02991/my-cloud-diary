import streamlit as st
from supabase import create_client
from datetime import datetime
import pytz
import requests # 天気データを取得するために必要
import streamlit as st
import requests
import pandas as pd

# 1. 接続設定
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# ★ 天気設定（あなたが取得した情報をセット）
API_KEY = st.secrets["OPENWEATHER_API_KEY"]
CITY_NAME = "Kitakyushu" # 福岡市なら "Fukuoka" に変更してください
WEATHER_URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY_NAME}&appid={API_KEY}&units=metric&lang=ja"

# ページ設定
st.set_page_config(page_title="My Cloud Diary", page_icon="🌤️")

# --- データ取得：天気 ---
def get_weather():
    try:
        response = requests.get(WEATHER_URL)
        data = response.json()
        temp = data["main"]["temp"]
        weather_desc = data["weather"][0]["description"]
        icon = data["weather"][0]["icon"]
        icon_url = f"http://openweathermap.org/img/wn/{icon}@2x.png"
        return temp, weather_desc, icon_url
    except:
        return None, None, None

temp, desc, icon_url = get_weather()
def show_multi_weather_chart():
    st.subheader("🌡️ 北九州市 vs 西都市 気温比較")

    # 北九州(Kitakyushu)と西都市(Saito)の緯度経度
    # 北九州: 33.88, 130.88 / 西都市: 32.11, 131.40
    locations = {
        "北九州市": {"lat": 33.8833, "lon": 130.8833},
        "西都市": {"lat": 32.11, "lon": 131.40}
    }

    try:
        combined_data = {}
        
        for name, coords in locations.items():
            url = f"https://api.open-meteo.com/v1/forecast?latitude={coords['lat']}&longitude={coords['lon']}&hourly=temperature_2m"
            res = requests.get(url).json()
            
            # 初回だけ時間軸を作成
            if not combined_data:
                combined_data["時間"] = pd.to_datetime(res["hourly"]["time"])
            
            # 各都市の気温を追加
            combined_data[name] = res["hourly"]["temperature_2m"]

        # まとめてDataFrameにする
        df = pd.DataFrame(combined_data).set_index("時間")

        # グラフを表示（自動で2本の線になります）
        st.line_chart(df)
        
        st.info("宮崎（西都市）の方が暖かいかな？グラフの線で比較してみてね！")

    except Exception as e:
        st.error(f"データの取得に失敗しました: {e}")


# --- 時刻と天気の表示エリア ---
jp_tz = pytz.timezone('Asia/Tokyo')
current_time = datetime.now(jp_tz).strftime("%Y/%m/%d %H:%M")

# 画面表示
col_a, col_b = st.columns([0.6, 0.4])
with col_a:
    st.markdown(f"#### 📍 {CITY_NAME}, Japan")
    st.markdown(f"##### 🕒 {current_time}")

with col_b:
    if temp:
        st.image(icon_url, width=70)
        st.write(f"{temp}℃ / {desc}")

st.divider()
show_multi_weather_chart()
# タイトル
st.markdown("<h1 style='text-align: center; color: #4A90E2;'>📝 My Cloud Diary</h1>", unsafe_allow_html=True)

# --- 入力・一覧表示エリア（以下は以前と同じ） ---
with st.container(border=True):
    content = st.text_area("今日のできごとは？", placeholder="今日は〇〇をしたよ！")
    submitted = st.button("日記を保存する", use_container_width=True, type="primary")
    
    if submitted and content:
        supabase.table("diary").insert({"content": content}).execute()
        st.success("クラウドに保存しました！")
        st.rerun()

st.header("📖 これまでの日記")
response = supabase.table("diary").select("*").order("created_at", desc=True).execute()
for row in response.data:
    with st.container(border=True):
        col1, col2 = st.columns([0.85, 0.15])
        with col1:
            dt = datetime.fromisoformat(row['created_at'].replace('Z', '+00:00')).astimezone(jp_tz)
            st.caption(f"📅 {dt.strftime('%Y/%m/%d %H:%M')}")
        with col2:
            if st.button("🗑️", key=f"del_{row['id']}"):
                supabase.table("diary").delete().eq("id", row['id']).execute()
                st.rerun()
        st.write(row['content'])






