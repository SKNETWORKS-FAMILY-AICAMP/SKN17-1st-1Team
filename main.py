import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import requests
import json
import random
from faker import Faker

# --- 페이지 기본 설정 ---
st.set_page_config(layout="wide")

# --- 데이터 로딩 함수 (샘플 데이터 생성) ---

@st.cache_data
def generate_fake_charger_data(num_records=1000):
    """Faker를 사용하여 대용량 충전소 샘플 데이터를 생성합니다."""
    fake = Faker('ko_KR')
    
    charger_types = {'01': 'DC차데모', '03': 'DC차데모+AC3상', '06': 'DC콤보', '07': 'DC차데모+DC콤보'}
    statuses = {'1': '통신이상', '2': '충전가능', '3': '충전중', '4': '운영중지', '5': '점검중'}
    
    data = []
    lat_range = (33.1, 38.6)
    lng_range = (125.9, 129.8)

    for _ in range(num_records):
        record = {
            'statNm': f'{fake.city()} {random.choice(["이마트", "시청", "공영주차장", "주민센터"])}점',
            'addr': fake.address(),
            'lat': random.uniform(lat_range[0], lat_range[1]),
            'lng': random.uniform(lng_range[0], lng_range[1]),
            'chgerType': random.choice(list(charger_types.values())),
            'stat': random.choice(list(statuses.values()))
        }
        data.append(record)
    
    df = pd.DataFrame(data)
    df[['lat', 'lng']] = df[['lat', 'lng']].apply(pd.to_numeric)
    return df

@st.cache_data
def get_ev_registration_data():
    """지역별 전기차 등록 현황 샘플 데이터를 생성합니다."""
    data = {
        'sido': ['서울특별시', '부산광역시', '대구광역시', '인천광역시', '광주광역시', '대전광역시', '울산광역시', '세종특별자치시', '경기도', '강원도', '충청북도', '충청남도', '전라북도', '전라남도', '경상북도', '경상남도', '제주특별자치도'],
        'ev_count': [150000, 45000, 38000, 55000, 25000, 30000, 18000, 15000, 220000, 32000, 35000, 48000, 37000, 41000, 52000, 68000, 50000],
    }
    return pd.DataFrame(data)

# --- GeoJSON 데이터 로드 ---
GEOJSON_URL = 'https://raw.githubusercontent.com/southkorea/southkorea-maps/master/kostat/2013/json/skorea_provinces_geo_simple.json'


# --- 데이터 로딩 실행 ---
fake_charger_df = generate_fake_charger_data(num_records=2000)
ev_reg_df = get_ev_registration_data()


# --- 사이드바 UI 구성 ---
with st.sidebar:
    # st.image(...) # 이 라인을 삭제했습니다.
    st.header("EV-Wise")
    st.markdown("전기차 충전소 및 등록 현황")
    
    view_mode = st.selectbox(
        "확인하고 싶은 정보를 선택하세요.",
        ("충전소 위치 (클러스터)", "지역별 전기차 등록 현황"),
        index=0
    )
    st.markdown("---")
    st.info("현재 샘플 데이터를 사용하여 지도를 표시합니다.", icon="ℹ️")


# --- 메인 페이지 UI 구성 ---
st.title("EV-Wise: 지역별 전기차 현황")
st.markdown(f"현재 **'{view_mode}'** 모드로 보고 있습니다.")
st.markdown("---")


# --- Folium 지도 생성 ---
m = folium.Map(
    location=[36.5, 127.5],
    zoom_start=7,
    tiles='https://xdworld.vworld.kr/2d/Base/202002/{z}/{x}/{y}.png',
    attr='VWorld',
    min_zoom=7,
    max_bounds=[(32, 123), (40, 133)]
)


# --- 선택된 모드에 따라 지도 내용 변경 ---
if view_mode == "충전소 위치 (클러스터)":
    if not fake_charger_df.empty:
        marker_cluster = MarkerCluster().add_to(m)
        
        for idx, row in fake_charger_df.iterrows():
            popup_html = f"""
            <b>{row['statNm']}</b><br>
            주소: {row['addr']}<br>
            충전기 타입: {row['chgerType']}<br>
            상태: {row['stat']}
            """
            folium.Marker(
                location=[row['lat'], row['lng']],
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=row['statNm'],
                icon=folium.Icon(color='blue', icon='bolt', prefix='fa')
            ).add_to(marker_cluster)
        st.success(f"총 {len(fake_charger_df)}개의 샘플 충전소 위치를 표시합니다.")

elif view_mode == "지역별 전기차 등록 현황":
    folium.Choropleth(
        geo_data=GEOJSON_URL,
        name='choropleth',
        data=ev_reg_df,
        columns=['sido', 'ev_count'],
        key_on='feature.properties.name',
        fill_color='YlGn',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='전기차 등록 대수'
    ).add_to(m)
    st.success("지역별 전기차 등록 현황을 색상 지도로 표시합니다.")


# --- 지도 출력 ---
st_folium(m, width='100%', height=600)