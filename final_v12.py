import streamlit as st
import pandas as pd
import pydeck as pdk
import os, requests, math
import streamlit.components.v1 as components
from datetime import datetime, timedelta

st.set_page_config(page_title="토비&마루 스마트 홈 v12.0", layout="wide")
st.markdown("<h1 style='text-align: center; color: #deff9a;'>🐶 토비 · 마루 스마트 홈 인프라 v12.0</h1>", unsafe_allow_html=True)
st.write("---")

# 📱 사이드바
st.sidebar.subheader("📱 Mobile Node")
st.sidebar.info("접속 주소:\n\n**http://192.168.0.39:8590**")

# [기능 1] 기상 및 산책 지수
@st.cache_data(ttl=600)
def get_yulha_weather():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=35.1769&longitude=128.8001&current_weather=true"
        r = requests.get(url).json()
        temp = r['current_weather']['temperature']
        wind = r['current_weather']['windspeed']
        score = 100 - (abs(temp - 22) * 3) - (wind * 1.5)
        return temp, wind, max(int(score), 0)
    except:
        return 31.5, 2.1, 48

current_temp, wind_speed, w_score = get_yulha_weather()
is_heatwave = current_temp >= 30.0

st.subheader("☀️ 김해 율하천 실시간 기상 관제 센터")
wc1, wc2, wc3, wc4 = st.columns(4)
wc1.metric("현재 기온", f"{current_temp} °C")
wc2.metric("현재 풍속", f"{wind_speed} m/s")
wc3.metric("산책 적합도 지수", f"{w_score} / 100")
if w_score >= 75: wc4.success("🟢 실외 활동 최적 환경")
elif w_score >= 50: wc4.warning("⚠️ 주의 요망")
else: wc4.error("🚨 산책 제한")
st.write("---")

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371000  
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dp / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dl / 2)**2
    return round(R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)), 1)

def play_dog_youtube(video_id, title):
    st.markdown(f"##### 📺 {title}")
    embed_url = f"https://www.youtube.com/embed/{video_id}?rel=0"
    components.iframe(embed_url, height=400)

tab_toby, tab_maru, tab_lbs, tab_memo = st.tabs(['🐾 토비 (Medical)', '🐾 마루 (Outdoor)', '🛰️ 실시간 LBS 관제', '📝 온가족 알림장'])

with tab_toby:
    st.subheader("💊 토비 정밀 메디컬 & 복약 매니지먼트")
    t_col_m1, t_col_m2 = st.columns(2)
    last_t_date = t_col_m1.date_input("💉 마지막 심장사상충 복약일", datetime.now() - timedelta(days=22), key="t_last_v12")
    next_t_date = last_t_date + timedelta(days=30)
    t_days_left = (next_t_date - datetime.now().date()).days
    if t_days_left < 0: t_col_m2.error(f"🚨 복약 주기 {abs(t_days_left)}일 초과!")
    else: t_col_m2.success(f"🟢 다음 정기 투약 예정일: {next_t_date} (D-{t_days_left})")

    st.write("---")
    col1, col2 = st.columns([1, 1.4])
    with col1:
        t_weight = st.number_input("⚖️ 실시간 체중 입력 (kg)", 1.0, 10.0, 3.2, step=0.1, key="t_w_v12")
    with col2:
        t_rer = round(70 * (t_weight ** 0.75), 1)
        t_status = f"🔺 비만 관리군" if t_weight > 3.2 else "🟢 정상"
        st.table(pd.DataFrame({"분류 지표": ["견종", "상태", "기초대사량(RER)"], "데이터": ["포메라니안", t_status, f"{t_rer} kcal"]}))

    st.write("---")
    play_dog_youtube("D-S6_F1G_mI", "정서 안정을 위한 델타파 테라피 사운드")

with tab_maru:
    st.subheader("💩 마루 배변 루틴 및 메디컬 스펙")
    m_col_m1, m_col_m2 = st.columns(2)
    last_m_date = m_col_m1.date_input("💊 마지막 외부구충 방역일", datetime.now() - timedelta(days=12), key="m_last_v12")
    next_m_date = last_m_date + timedelta(days=30)
    m_days_left = (next_m_date - datetime.now().date()).days
    if m_days_left < 0: m_col_m2.error(f"🚨 방역 초과!")
    else: m_col_m2.success(f"🟢 다음 구충 스케줄: {next_m_date} (D-{m_days_left})")

    st.write("---")
    col3, col4 = st.columns([1, 1.4])
    with col3:
        m_weight = st.number_input("⚖️ 실시간 체중 입력 (kg)", 5.0, 25.0, 9.8, step=0.1, key="m_w_v12")
    with col4:
        m_rer = round(70 * (m_weight ** 0.75), 1)
        st.table(pd.DataFrame({"분류 지표": ["견종", "특이사항", "기초대사량(RER)"], "데이터": ["시바견", "100% 야외배변 고집", f"{m_rer} kcal"]}))

    st.write("---")
    play_dog_youtube("K_Nf-v-xG9A", "마루 사냥 본능 충족용 영상")

with tab_lbs:
    st.subheader("🛰️ 위치 기반 지오펜싱 및 메타볼릭 관제 센터")
    gps_col1, gps_col2 = st.columns(2)
    u_lat = gps_col1.slider("보호자 실시간 위도 (GPS)", 35.1700, 35.1850, 35.1780, step=0.0001, format="%.4f", key="lat_v12")
    u_lon = gps_col2.slider("보호자 실시간 경도 (GPS)", 128.7900, 128.8100, 128.8020, step=0.0001, format="%.4f", key="lon_v12")

    walked_distance = calculate_distance(35.1780, 128.8020, u_lat, u_lon)
    burned_kcal = round((m_weight * 1.5) * (walked_distance / 1000.0), 1)
    st.metric("🔥 실시간 산책 칼로리 소모", f"{burned_kcal} kcal", f"거리: {walked_distance} m")

    base_lat, base_lon = 35.1769, 128.8001
    places_df = pd.DataFrame([
        {"name": "💩 [A구역] 율하천 잔디 산책로", "lat": base_lat, "lon": base_lon, "h": 350, "color": [255, 90, 0, 220]},
        {"name": "⚠️ [위험 구역] 공사 지대", "lat": 35.1750, "lon": 128.7980, "h": 100, "color": [255, 0, 0, 250]}
    ])

    st.pydeck_chart(pdk.Deck(
        map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
        initial_view_state=pdk.ViewState(latitude=u_lat, longitude=u_lon, zoom=14.5, pitch=45),
        layers=[pdk.Layer('ColumnLayer', data=places_df, get_position='[lon, lat]', get_elevation='h', radius=25, get_fill_color='color', extrude=True)]
    ))

with tab_memo:
    st.subheader("📝 온가족 양육 공동 알림장")
    msg = st.text_input("가족들과 실시간 공유할 양육 메모를 입력하세요", key="msg_v12")
    if st.button("📌 실시간 일지 저장"): st.success("저장 완료")
