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

import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import pytz

# ★ 設定
API_KEY = st.secrets["OPENWEATHER_API_KEY"]
jp_tz = pytz.timezone('Asia/Tokyo')
current_time = datetime.now(jp_tz).strftime("%Y/%m/%d %H:%M")

# ページ設定
st.set_page_config(page_title="My Cloud Diary", page_icon="🌤️")

# --- データ取得：天気を共通化 ---
def get_weather(city_name):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_KEY}&units=metric&lang=ja"
    try:
        response = requests.get(url)
        data = response.json()
        temp = data["main"]["temp"]
        weather_desc = data["weather"][0]["description"]
        icon = data["weather"][0]["icon"]
        icon_url = f"http://openweathermap.org/img/wn/{icon}@2x.png"
        return temp, weather_desc, icon_url
    except:
        return None, None, None

# --- 時刻と天気の表示エリア ---
st.markdown(f"### 🕒 {current_time}")

# 2つのカラムで北九州と西都を並べる
col_k, col_s = st.columns(2)

with col_k:
    temp_k, desc_k, icon_k = get_weather("Kitakyushu")
    st.markdown("#### 📍 北九州市")
    if temp_k:
        st.image(icon_k, width=70)
        st.write(f"**{temp_k}℃** / {desc_k}")

with col_s:
    temp_s, desc_s, icon_s = get_weather("Saito")
    st.markdown("#### 📍 西都市")
    if temp_s:
        st.image(icon_s, width=70)
        st.write(f"**{temp_s}℃** / {desc_s}")

st.divider()
def show_weekly_forecast(city_name, lat, lon):
    st.markdown(f"#### 📅 {city_name} の1週間予報")
    
    # Open-Meteoの「日次データ(daily)」を取得
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min,weathercode&timezone=Asia%2FTokyo"
    
    try:
        res = requests.get(url).json()
        daily = res["daily"]
        
        # 7日分を横に並べるためのカラムを作成
        cols = st.columns(7)
        
        # 天気コードをアイコンに変換する簡易的な辞書
        # (0:快晴, 1-3:晴れ/曇り, 45-48:霧, 51-67:雨, 71-77:雪)
        def get_weather_emoji(code):
            if code == 0: return "☀️"
            if code <= 3: return "☁️"
            if code >= 51 and code <= 67: return "☔"
            if code >= 71 and code <= 77: return "❄️"
            return "🌦️"

        for i in range(7):
            with cols[i]:
                # 日付を「月/日」の形式に
                date = pd.to_datetime(daily["time"][i]).strftime("%m/%d")
                emoji = get_weather_emoji(daily["weathercode"][i])
                max_t = daily["temperature_2m_max"][i]
                min_t = daily["temperature_2m_min"][i]
                
                # コンパクトに表示
                st.write(f"**{date}**")
                st.write(f"## {emoji}")
                st.write(f"{max_t}℃")
                st.write(f"_{min_t}℃_")

    except Exception as e:
        st.error(f"予報の取得に失敗しました: {e}")
st.divider()
# 北九州と西都、それぞれ表示
show_weekly_forecast("北九州", 33.88, 130.88)
st.write("") # 少し隙間をあける
show_weekly_forecast("西都市", 32.11, 131.40)
# --- 比較グラフの表示 ---
def show_multi_weather_chart():
    st.subheader("🌡️ 北九州市 vs 西都市 気温比較")
    locations = {
        "北九州市": {"lat": 33.8833, "lon": 130.8833},
        "西都市": {"lat": 32.11, "lon": 131.40}
    }
    try:
        combined_data = {}
        for name, coords in locations.items():
            url = f"https://api.open-meteo.com/v1/forecast?latitude={coords['lat']}&longitude={coords['lon']}&hourly=temperature_2m"
            res = requests.get(url).json()
            if not combined_data:
                combined_data["時間"] = pd.to_datetime(res["hourly"]["time"])
            combined_data[name] = res["hourly"]["temperature_2m"]

        df = pd.DataFrame(combined_data).set_index("時間")
        st.line_chart(df)
        st.info("宮崎（西都市）の方が暖かいかな？グラフの線で比較してみてね！")
    except Exception as e:
        st.error(f"データの取得に失敗しました: {e}")

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








