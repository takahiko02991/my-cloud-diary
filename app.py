import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime
import pytz
import requests

# --- 1. 接続設定 & ページ設定 ---
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

API_KEY = st.secrets["OPENWEATHER_API_KEY"]
jp_tz = pytz.timezone('Asia/Tokyo')
current_time = datetime.now(jp_tz).strftime("%Y/%m/%d %H:%M")

st.set_page_config(page_title="My Cloud Diary", page_icon="🌤️")

# --- 2. 共通で使う場所データ ---
locations = {
    "北九州市": {"lat": 33.8833, "lon": 130.8833, "query": "Kitakyushu"},
    "西都市": {"lat": 32.11, "lon": 131.40, "query": "Saito"}
}

# --- 3. 関数定義エリア ---

def get_weather(city_query):
    """現在の天気を取得"""
    api_url = f"http://api.openweathermap.org/data/2.5/weather?q={city_query}&appid={API_KEY}&units=metric&lang=ja"
    try:
        response = requests.get(api_url)
        data = response.json()
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        icon = data["weather"][0]["icon"]
        icon_url = f"http://openweathermap.org/img/wn/{icon}@2x.png"
        return temp, desc, icon_url
    except:
        return None, None, None

def show_horizontal_forecast(city_name, lat, lon):
    """1週間予報を横スクロールで表示"""
    st.markdown(f"#### 📅 {city_name} の1週間予報")
    url_forecast = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=weathercode,temperature_2m_max,temperature_2m_min&timezone=Asia%2FTokyo"
    
    try:
        res = requests.get(url_forecast).json()
        daily = res["daily"]
        
        forecast_html = """
        <style>
            .scroll-container { display: flex; overflow-x: auto; white-space: nowrap; padding: 10px 0; gap: 15px; -webkit-overflow-scrolling: touch; }
            .forecast-card { flex: 0 0 auto; width: 80px; background-color: #f0f2f6; border-radius: 10px; padding: 10px; text-align: center; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
            .emoji { font-size: 24px; margin: 5px 0; }
            .date { font-size: 12px; font-weight: bold; color: #333; }
            .temp-max { color: #ff4b4b; font-size: 14px; }
            .temp-min { color: #1f77b4; font-size: 14px; }
        </style>
        <div class="scroll-container">
        """
        
        def get_emoji(code):
            if code == 0: return "☀️"
            if code <= 3: return "☁️"
            if code >= 51 and code <= 67: return "☔"
            return "🌦️"

        for i in range(7):
            date = pd.to_datetime(daily["time"][i]).strftime("%m/%d")
            emoji = get_emoji(daily["weathercode"][i])
            max_t = daily["temperature_2m_max"][i]
            min_t = daily["temperature_2m_min"][i]
            forecast_html += f"""
            <div class="forecast-card">
                <div class="date">{date}</div>
                <div class="emoji">{emoji}</div>
                <div class="temp-max">{max_t}℃</div>
                <div class="temp-min">{min_t}℃</div>
            </div>
            """
        forecast_html += "</div>"
        st.components.v1.html(forecast_html, height=130)
    except:
        st.error("予報の取得に失敗しました")

def show_multi_weather_chart():
    """比較グラフを表示"""
    st.subheader("🌡️ 北九州市 vs 西都市 気温比較")
    try:
        combined_data = {}
        for name, coords in locations.items():
            url_chart = f"https://api.open-meteo.com/v1/forecast?latitude={coords['lat']}&longitude={coords['lon']}&hourly=temperature_2m"
            res = requests.get(url_chart).json()
            if not combined_data:
                combined_data["時間"] = pd.to_datetime(res["hourly"]["time"])
            combined_data[name] = res["hourly"]["temperature_2m"]

        df = pd.DataFrame(combined_data).set_index("時間")
        st.line_chart(df)
        st.info("宮崎（西都市）の方が暖かいかな？グラフの線で比較してみてね！")
    except Exception as e:
        st.error(f"グラフの取得に失敗しました: {e}")

# --- 4. 実際の表示実行エリア ---

st.markdown(f"### 🕒 {current_time}")

col_k, col_s = st.columns(2)
with col_k:
    t_k, d_k, i_k = get_weather(locations["北九州市"]["query"])
    st.markdown("#### 📍 北九州市")
    if t_k:
        st.image(i_k, width=70)
        st.write(f"**{t_k}℃** / {d_k}")

with col_s:
    t_s, d_s, i_s = get_weather(locations["西都市"]["query"])
    st.markdown("#### 📍 西都市")
    if t_s:
        st.image(i_s, width=70)
        st.write(f"**{t_s}℃** / {d_s}")

st.divider()

# 1週間予報を表示
show_horizontal_forecast("北九州", locations["北九州市"]["lat"], locations["北九州市"]["lon"])
show_horizontal_forecast("西都市", locations["西都市"]["lat"], locations["西都市"]["lon"])

st.divider()

# 比較グラフを表示
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










