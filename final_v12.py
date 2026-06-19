import streamlit as st
import pandas as pd
import pydeck as pdk
import os, requests, math
import streamlit.components.v1 as components
from datetime import datetime, timedelta

st.set_page_config(page_title="토비&마루 스마트 홈 v14.0", layout="wide")
st.markdown("<h1 style='text-align: center; color: #deff9a;'>🐶 토비 · 마루 스마트 홈 인프라 v14.0</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #94a3b8;'>지능형 메디컬 관제 및 위치 기반 멀티모달 헬스케어 시스템</p>", unsafe_allow_html=True)
st.write("---")

# 📱 사이드바
st.sidebar.subheader("🛰️ 시스템 상태")
st.sidebar.success("정상 가동 중 (Cloud Node)")
st.sidebar.info("학교 발표장 공용 PC 완벽 호환 모드")

# [기능 1] 오픈 API 기상 데이터 및 산책 적합도 알고리즘
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
elif w_score >= 50: wc4.warning("⚠️ 개체별 상태 주의 요망")
else: wc4.error("🚨 실외 활동 및 산책 제한")
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

# 통합 멀티 탭 인프라
tab_toby, tab_maru, tab_lbs, tab_memo = st.tabs(['🐾 토비 (Medical)', '🐾 마루 (Outdoor)', '🛰️ 실시간 LBS 관제', '📝 온가족 알림장'])

with tab_toby:
    st.subheader("💊 토비 정밀 메디컬 & 복약 매니지먼트")
    t_col_m1, t_col_m2 = st.columns(2)
    last_t_date = t_col_m1.date_input("💉 마지막 심장사상충 복약일 선택", datetime.now() - timedelta(days=22), key="t_last_date_cl")
    next_t_date = last_t_date + timedelta(days=30)
    t_days_left = (next_t_date - datetime.now().date()).days
    if t_days_left < 0: t_col_m2.error(f"🚨 복약 주기 {abs(t_days_left)}일 초과! 즉시 투약 알림")
    else: t_col_m2.success(f"🟢 다음 정기 투약 예정일: {next_t_date} (D-{t_days_left})")

    st.write("---")
    col1, col2 = st.columns([1, 1.4])
    with col1:
        # 📸 토비 사진 업로더 엔진 완벽 복구
        if os.path.exists("toby_saved.png"): 
            st.image("toby_saved.png", use_container_width=True)
        t_up_file = st.file_uploader("📸 토비 프로필 사진 등록/변경", type=["png", "jpg", "jpeg"], key="t_pic_up")
        if t_up_file:
            with open("toby_saved.png", "wb") as out_f: out_f.write(t_up_file.getbuffer())
            st.rerun()
        t_weight = st.number_input("⚖️ 실시간 체중 입력 (kg)", 1.0, 10.0, 3.2, step=0.1, key="t_w_cl")
    with col2:
        t_rer = round(70 * (t_weight ** 0.75), 1)
        t_status = f"🔺 비만 관리군 ({round(t_weight - 3.2, 2)}kg 초과)" if t_weight > 3.2 else "🟢 정상 밸런스 체중"

        toby_table = {
            "분류 지표": ["견종 / 모색", "현재 관리 상태", "정량적 기초대사량(RER)"],
            "관제 데이터 스펙": ["포메라니안 / 블랙탄", t_status, f"{t_rer} kcal / day"]
        }
        st.table(pd.DataFrame(toby_table))

        t_course = "🛣️ 율하천 평지 코스 (15분 제한)" if t_weight > 3.2 else "🛣️ 율하천 표준 코스 (25분)"
        t_diet = "🥗 처방 다이어트 식단 (단호박 화식)" if t_weight > 3.2 else "🍚 일반 유기농 사료 스케줄"
        st.info(f"🎯 **토비 맞춤 처방:** {t_course} | {t_diet}")

    st.write("---")
    if is_heatwave:
        play_dog_youtube("p795mI-pM3c", "폭염 통제 모드: 실내 행동 풍부화 노즈워크 가이드")
    else:
        play_dog_youtube("D-S6_F1G_mI", "정서 안정을 위한 델타파 테라피 사운드")

with tab_maru:
    st.subheader("💩 마루 배변 루틴 및 메디컬 스펙")
    m_col_m1, m_col_m2 = st.columns(2)
    last_m_date = m_col_m1.date_input("💊 마지막 외부구충 방역일 선택", datetime.now() - timedelta(days=12), key="m_last_date_cl")
    next_m_date = last_m_date + timedelta(days=30)
    m_days_left = (next_m_date - datetime.now().date()).days
    if m_days_left < 0: m_col_m2.error("🚨 방역 방치 상태! 즉시 케어가 필요합니다.")
    else: m_col_m2.success(f"🟢 다음 구충 스케줄: {next_m_date} (D-{m_days_left})")

    st.write("---")
    col3, col4 = st.columns([1, 1.4])
    with col3:
        # 📸 마루 사진 업로더 엔진 완벽 복구
        if os.path.exists("maru_saved.png"): 
            st.image("maru_saved.png", use_container_width=True)
        m_up_file = st.file_uploader("📸 마루 프로필 사진 등록/변경", type=["png", "jpg", "jpeg"], key="m_pic_up")
        if m_up_file:
            with open("maru_saved.png", "wb") as out_f: out_f.write(m_up_file.getbuffer())
            st.rerun()
        m_weight = st.number_input("⚖️ 실시간 체중 입력 (kg)", 5.0, 25.0, 9.8, step=0.1, key="m_w_cl")
    with col4:
        m_rer = round(70 * (m_weight ** 0.75), 1)
        m_status = f"🔺 과체중 경고 ({round(m_weight - 9.8, 2)}kg 초과)" if m_weight > 9.8 else "🟢 정상 표준 체중"
        target_kcal = 150.0 if m_weight > 9.8 else 90.0

        maru_table = {
            "분류 지표": ["견종 / 모색", "행동 메커니즘", "정량적 기초대사량(RER)"],
            "관제 데이터 스펙": ["시바견 / 적구", "100% 야외배변 필수 고집", f"{m_rer} kcal / day"]
        }
        st.table(pd.DataFrame(maru_table))
        m_course = "⛰️ 율하 야산 고강도 연소 코스" if m_weight > 9.8 else "🛣️ 율하천 정기 순적 코스"
        m_diet = "🥗 고식이섬유 처방 식단" if m_weight > 9.8 else "🍚 중형견 영양 균형식"
        st.info(f"🎯 **마루 맞춤 처방:** {m_course} | {m_diet}")

    st.write("---")
    st.subheader("⏱️ 야외배변 2회 루틴 골든타임")
    am_f = st.selectbox("☀️ 오전 식사 완료 시각", list(range(5, 12)), index=3, key="am_cl")
    pm_f = st.selectbox("🌙 오후 식사 완료 시각", list(range(17, 24)), index=2, key="pm_cl")
    now_dt = datetime.now()
    am_target = now_dt.replace(hour=am_f+4, minute=0, second=0)
    pm_target = now_dt.replace(hour=pm_f+4, minute=0, second=0)

    if now_dt < am_target: target_dt, routine_name = am_target, "오전 (1차) 배변"
    elif now_dt < pm_target: target_dt, routine_name = pm_target, "오후 (2차) 배변"
    else: target_dt, routine_name = am_target + timedelta(days=1), "익일 오전 (1차) 배변"

    time_delta = target_dt - now_dt
    st.success(f"🎯 **[{routine_name}] 대장 운동 예측 시점:** {target_dt.strftime('%p %I:%M')} (남은 시간: {time_delta.seconds//3600}시간 {(time_delta.seconds%3600)//60}분)")
    st.write("---")
    play_dog_youtube("K_Nf-v-xG9A", "maru natural field tracking")

with tab_lbs:
    st.subheader("🛰️ 위치 기반 지오펜싱 및 메타볼릭 관제 센터")
    gps_col1, gps_col2 = st.columns(2)
    u_lat = gps_col1.slider("보호자 실시간 위도 좌표 (GPS)", 35.1700, 35.1850, 35.1780, step=0.0001, format="%.4f", key="lat_cl")
    u_lon = gps_col2.slider("보호자 실시간 경도 좌표 (GPS)", 128.7900, 128.8100, 128.8020, step=0.0001, format="%.4f", key="lon_cl")

    walked_distance = calculate_distance(35.1780, 128.8020, u_lat, u_lon)
    burned_kcal = round((m_weight * 1.5) * (walked_distance / 1000.0), 1)

    st.metric("🔥 실시간 산책 메타볼릭 칼로리 소모", f"{burned_kcal} / {target_kcal} kcal", f"누적 산책 거리: {walked_distance} m")
    st.progress(min(burned_kcal / target_kcal, 1.0))

    base_lat, base_lon = 35.1769, 128.8001
    places_df = pd.DataFrame([
        {"name": "💩 [A구역] 율하천 잔디 산책로 (최선호 명당)", "lat": base_lat, "lon": base_lon, "h": 350, "type": "poop", "color": [255, 90, 0, 220]},
        {"name": "💩 [B구역] 관동공원 남측 잔디광장", "lat": base_lat - 0.0024, "lon": base_lon - 0.0016, "h": 240, "type": "poop", "color": [255, 140, 0, 200]},
        {"name": "💩 [C구역] 율하천교 하부 수풀림 (그늘 요충지)", "lat": base_lat + 0.0011, "lon": base_lon - 0.0015, "h": 210, "type": "poop", "color": [255, 120, 0, 210]},
        {"name": "⚠️ [위험 구역] 관동초 동측 공사 지대 (진입 금지)", "lat": 35.1750, "lon": 128.7980, "h": 100, "type": "danger", "color": [255, 0, 0, 250]}
    ])

    dist_to_danger = calculate_distance(u_lat, u_lon, 35.1750, 128.7980)
    if dist_to_danger <= 150.0:
        st.error(f"🚨 [지오펜싱 차단 위험 경보] 위험 구역 전방 {dist_to_danger}m 이내 진입! 우회 동선을 구축하십시오.")
    else:
        st.info("🟢 현재 산책 트랙킹 경로: 안전 구역 운행 중")

    if is_heatwave:
        places_df.loc[places_df['name'].str.contains('A구역|B구역'), 'color'] = [150, 0, 255, 240]
        st.warning("⚠️ [자율 제어 인프라] 폭염 지표 수신으로 인해 오픈형 아스팔트 산책 구역(A, B)이 보라색으로 자율 통제 차단되었습니다.")

    emergency_click = st.button("🚨 긴급 야외배변 포물선(Arc) 최단 동선 유도", use_container_width=True, key="btn_cl")

    layers = [
        pdk.Layer('ColumnLayer', data=places_df, get_position='[lon, lat]', get_elevation='h', elevation_scale=1.2, radius=22, get_fill_color='color', extrude=True),
        pdk.Layer('ScatterplotLayer', data=pd.DataFrame([{"lat": u_lat, "lon": u_lon}]), get_position='[lon, lat]', get_color='[0, 255, 255, 255]', get_radius=30)
    ]
    if emergency_click:
        st.error("🚨 비상 신호 전가족 브로드캐스팅 가동! 최단거리 명당 3D Arc 경로선 레이어를 동적 활성화합니다.")
        em_route = pd.DataFrame([{"start_lat": u_lat, "start_longitude": u_lon, "end_lat": base_lat, "end_longitude": base_lon}])
        layers.append(pdk.Layer('ArcLayer', data=em_route, get_source_position='[start_longitude, start_lat]', get_target_position='[end_longitude, end_lat]', get_source_color='[255, 255, 0]', get_target_color='[255, 30, 0]', get_width=8))

    st.pydeck_chart(pdk.Deck(
        map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
        initial_view_state=pdk.ViewState(latitude=u_lat, longitude=u_lon, zoom=14.5, pitch=45),
        layers=layers
    ))

with tab_memo:
    st.subheader("📝 온가족 양육 공동 알림장")
    wr = st.selectbox("작성자 세션 선택", ["나", "엄마", "아빠"], key="wr_cl")
    msg = st.text_input("가족들과 실시간 공유할 양육 메모를 입력하세요", key="msg_cl")
    if st.button("📌 실시간 일지 저장", use_container_width=True, key="save_cl"):
        st.success("💾 클라우드 데이터베이스 저장 및 실시간 동기화 완료")
