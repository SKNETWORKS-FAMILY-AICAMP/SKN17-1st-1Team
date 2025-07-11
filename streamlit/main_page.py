import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import random
from faker import Faker
import json
import requests

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="EV-Wise 대시보드",
    page_icon="🗺️",
    layout="wide"
)

# --- 데이터 로딩 함수 (샘플 데이터 생성) ---
@st.cache_data
def generate_fake_charger_data(num_records=2000):
    """Faker를 사용하여 대용량 충전소 샘플 데이터를 생성합니다."""
    fake = Faker('ko_KR')
    data = []
    sido_list = ['서울특별시', '부산광역시', '대구광역시', '인천광역시', '광주광역시', '대전광역시', '울산광역시', '세종특별자치시', '경기도', '강원특별자치도', '충청북도', '충청남도', '전북특별자치도', '전라남도', '경상북도', '경상남도', '제주특별자치도']
    
    for _ in range(num_records):
        sido = random.choice(sido_list)
        full_address = fake.address()
        # 주소에 시/도 이름이 포함되지 않은 경우, 맨 앞에 추가
        if not any(s in full_address for s in sido_list):
            full_address = f"{sido} {full_address}"
        
        record = {'addr': full_address}
        data.append(record)
    
    return pd.DataFrame(data)

@st.cache_data
def get_ev_registration_data():
    """지역별 전기차 등록 현황 샘플 데이터를 생성합니다."""
    data = {
        'sido': ['서울특별시', '부산광역시', '대구광역시', '인천광역시', '광주광역시', '대전광역시', '울산광역시', '세종특별자치시', '경기도', '강원특별자치도', '충청북도', '충청남도', '전북특별자치도', '전라남도', '경상북도', '경상남도', '제주특별자치도'],
        'ev_count': [150000, 45000, 38000, 55000, 25000, 30000, 18000, 15000, 220000, 32000, 35000, 48000, 37000, 41000, 52000, 68000, 50000],
    }
    return pd.DataFrame(data)

# --- GeoJSON 데이터 로드 ---
@st.cache_data
def get_geojson_data():
    """URL에서 GeoJSON 데이터를 로드합니다."""
    url = 'https://raw.githubusercontent.com/southkorea/southkorea-maps/master/kostat/2013/json/skorea_provinces_geo_simple.json'
    response = requests.get(url)
    return response.json()

geojson_data = get_geojson_data()

# --- 데이터 로딩 실행 ---
# 샘플 데이터 개수를 361,043개로 설정 (기존 코드와 동일)
charger_df_raw = generate_fake_charger_data(num_records=361043)
ev_reg_df = get_ev_registration_data()

# --- 충전소 데이터를 시/도 별로 집계하는 함수 ---
@st.cache_data
def aggregate_chargers_by_sido(charger_df, sido_list):
    """충전소 데이터프레임에서 주소를 기반으로 시/도별 충전소 개수를 집계합니다."""
    def extract_sido(address):
        if '강원' in address: return '강원특별자치도'
        if '전북' in address: return '전북특별자치도'
        for sido_name in sido_list:
            if sido_name in address:
                return sido_name
        return None

    charger_df['sido'] = charger_df['addr'].apply(extract_sido)
    charger_counts = charger_df.dropna(subset=['sido']).groupby('sido').size().reset_index(name='charger_count')
    return charger_counts

sido_list = ev_reg_df['sido'].tolist()
charger_counts_by_sido_df = aggregate_chargers_by_sido(charger_df_raw.copy(), sido_list)

# --- 데이터와 지도의 행정구역 이름 맞추기 ---
sido_name_mapping = {
    '강원특별자치도': '강원도',
    '전북특별자치도': '전라북도'
}
# 데이터프레임 복사 후 이름 변경
charger_counts_for_map = charger_counts_by_sido_df.copy()
charger_counts_for_map['sido'] = charger_counts_for_map['sido'].replace(sido_name_mapping)

ev_reg_for_map = ev_reg_df.copy()
ev_reg_for_map['sido'] = ev_reg_for_map['sido'].replace(sido_name_mapping)

# --- 사이드바 UI 구성 ---
with st.sidebar:
    st.header("🗺️ EV-Wise 대시보드")
    st.markdown("전기차 관련 정보를 시각적으로 확인하세요.")
    
    view_mode = st.selectbox(
        "확인하고 싶은 정보를 선택하세요.",
        ("지역별 충전소 개수", "지역별 전기차 등록 현황"),
        index=0,
        key='map_view_select'
    )
    st.markdown("---")
    st.info("이 페이지의 데이터는 시뮬레이션을 위해 생성된 샘플 데이터입니다.", icon="ℹ️")


# --- 메인 페이지 UI 구성 ---
st.title("EV-Wise: 지역별 전기차 현황 지도")
st.markdown(f"사이드바에서 **'{view_mode}'** 모드를 선택했습니다. 지도를 통해 지역별 현황을 확인해 보세요.")
st.markdown("---")

# --- Folium 지도 생성 (VWorld 타일 사용) ---
m = folium.Map(
    location=[36.5, 127.5],
    zoom_start=7,
    tiles='https://xdworld.vworld.kr/2d/Base/202002/{z}/{x}/{y}.png',
    attr='VWorld',
    min_zoom=7,
    max_bounds=[(32, 123), (40, 133)]
)

# --- 선택된 모드에 따라 지도 내용 변경 ---
if view_mode == "지역별 충전소 개수":
    folium.Choropleth(
        geo_data=geojson_data,
        name='choropleth',
        data=charger_counts_for_map,
        columns=['sido', 'charger_count'],
        key_on='feature.properties.name',
        fill_color='PuBuGn',
        fill_opacity=0.8,
        line_opacity=0.3,
        legend_name='샘플 충전소 개수'
    ).add_to(m)
    st.success(f"**지역별 샘플 충전소 개수**를 색상 지도로 표시합니다. (전국 총 {charger_counts_for_map['charger_count'].sum():,}개)")

elif view_mode == "지역별 전기차 등록 현황":
    folium.Choropleth(
        geo_data=geojson_data,
        name='choropleth',
        data=ev_reg_for_map,
        columns=['sido', 'ev_count'],
        key_on='feature.properties.name',
        fill_color='YlGn',
        fill_opacity=0.8,
        line_opacity=0.3,
        legend_name='전기차 등록 대수'
    ).add_to(m)
    st.success(f"**지역별 전기차 등록 현황**을 색상 지도로 표시합니다. (전국 총 {ev_reg_for_map['ev_count'].sum():,}대)")

# --- 지도 출력 ---
st_folium(m, width='100%', height=600, returned_objects=[])