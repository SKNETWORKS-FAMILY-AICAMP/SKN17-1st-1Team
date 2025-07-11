import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import random
from faker import Faker
import json
import requests
import mysql.connector

# DB 연결
connection = mysql.connector.connect(
    host="localhost",           # MYSQL 서버 주소
    user="ohgiraffers",         # 사용자 이름
    password="ohgiraffers",     # 비밀번호
    database="primusdb"           # 사용할 데이터비이스(스키마)
)
cursor = connection.cursor() # 커서 객체 생성
sql = """

"""


# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="EV-Wise 대시보드",
    page_icon="🗺️",
    layout="wide"
)


#-------------------------------------------------------------------------실제 데이터
# '시도'별 차량 등록 대수 불러오는 함수
@st.cache_data
def load_ev_registration_data_from_mysql():
    # DB 연결
    connection = mysql.connector.connect(
        host="localhost",
        user="ohgiraffers",
        password="ohgiraffers",
        database="primusdb"
    )
    cursor = connection.cursor()

    # SQL 실행
    query = """
        SELECT 
            r.province_city AS sido,
            SUM(ev.registrtation_count) AS ev_count
        FROM ev_registration ev
        JOIN region_info r USING(region_code)
        GROUP BY r.province_city;
    """
    cursor.execute(query)

    # 결과 가져오기 + DataFrame 변환
    result = cursor.fetchall()
    columns = ['sido', 'ev_count']
    df = pd.DataFrame(result, columns=columns)

    # 연결 종료
    cursor.close()
    connection.close()

    return df

# '시도'별 충전소 데이터 불러오는 함수
@st.cache_data
def load_charger_counts_from_mysql():
    connection = mysql.connector.connect(
        host="localhost",
        user="ohgiraffers",
        password="ohgiraffers",
        database="primusdb"
    )
    cursor = connection.cursor()

    query = """
        SELECT 
            r.province_city AS sido,
            COUNT(*) AS charger_count
        FROM ev_charger evc
        JOIN region_info r USING(region_code)
        GROUP BY r.province_city;
    """
    cursor.execute(query)
    result = cursor.fetchall()
    df = pd.DataFrame(result, columns=['sido', 'charger_count'])

    cursor.close()
    connection.close()

    return df

#-----------------------------------------------------------------------

# --- GeoJSON 데이터 로드 ---
@st.cache_data
def get_geojson_data():
    """URL에서 GeoJSON 데이터를 로드합니다."""
    url = 'https://raw.githubusercontent.com/southkorea/southkorea-maps/master/kostat/2013/json/skorea_provinces_geo_simple.json'
    response = requests.get(url)
    return response.json()

geojson_data = get_geojson_data()

# --- 데이터 로딩 실행 ---
# --- 데이터와 지도의 행정구역 이름 맞추기 ---
sido_name_mapping = {
    '강원특별자치도': '강원도',
    '전북특별자치도': '전라북도'
}


charger_counts_by_sido_df = load_charger_counts_from_mysql()
charger_counts_by_sido_df['sido'] = charger_counts_by_sido_df['sido'].replace(sido_name_mapping)
charger_counts_for_map = charger_counts_by_sido_df.copy()

ev_reg_df = load_ev_registration_data_from_mysql() #실제 데이터
# ev_count 컬럼을 숫자로 변환
ev_reg_df['ev_count'] = pd.to_numeric(ev_reg_df['ev_count'], errors='coerce')
# 시도 이름 매핑
ev_reg_for_map = ev_reg_df.copy()
ev_reg_for_map['sido'] = ev_reg_for_map['sido'].replace(sido_name_mapping)

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
    #charger_counts = charger_df.dropna(subset=['sido']).groupby('sido').size().reset_index(name='charger_count')
    charger_counts = charger_df[charger_df['sido'].notnull()].groupby('sido').size().reset_index(name='charger_count')

    return charger_counts

sido_list = ev_reg_df['sido'].tolist()
#charger_counts_by_sido_df = aggregate_chargers_by_sido(charger_df_raw.copy(), sido_list)


# 데이터프레임 복사 후 이름 변경
charger_counts_for_map = charger_counts_by_sido_df.copy()
charger_counts_for_map['sido'] = charger_counts_for_map['sido'].replace(sido_name_mapping)

ev_reg_for_map = ev_reg_df.copy()
ev_reg_for_map['sido'] = ev_reg_for_map['sido'].replace(sido_name_mapping)

# --- 사이드바 UI 구성 ---
with st.sidebar:
    st.header("🗺️ 모드 선택")
    
    view_mode = st.selectbox(
        "충전소 개수 혹은 전기차 등록 대수를 확인하세요.",
        ("지역별 충전소 개수", "지역별 전기차 등록 현황"),
        index=0,
        key='map_view_select'
    )
    st.markdown("---")
    st.info("이 페이지의 데이터는 실제 DB 기반의 전기차 및 충전소 현황입니다.", icon="ℹ️")


# --- 메인 페이지 UI 구성 ---
st.title("🚗 전국 시/도별 전기차와 충전소 현황 🔌")
st.markdown(f"전기차 구매를 희망하는 개인 혹은 전기차 인프라 현황을 파악하고 싶은 기관에게 관련 정보를 제공해드립니다.")
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
    thresholds = [6000, 12000, 18000, 30000, 50000, 75000, 100000]
    folium.Choropleth(
    geo_data=geojson_data,
    data=charger_counts_for_map,
    columns=["sido", "charger_count"],
    key_on="feature.properties.name",
    fill_color="YlOrRd",  # 색상도 더 눈에 띄는 색으로 바꿨음
    fill_opacity=0.7,
    line_opacity=0.2,
    threshold_scale=thresholds,
    bins=thresholds,
    legend_name="충전소 개수",
    reset=True
    ).add_to(m)

    

    st.success(f"**지역별 충전소 개수**를 색상 지도로 표시합니다. (전국 총 {charger_counts_for_map['charger_count'].sum():,}개)")

elif view_mode == "지역별 전기차 등록 현황":
    
    thresholds = [7000, 20000, 40000, 60000, 80000, 100000, 130000]
    folium.Choropleth(
    geo_data=geojson_data,
    data=ev_reg_for_map,
    columns=["sido", "ev_count"],
    key_on="feature.properties.name",
    fill_color="YlGnBu",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="전기차 등록 대수",
    threshold_scale=thresholds,
    bins=thresholds,
    reset=True
    ).add_to(m)
    st.success(f"**지역별 전기차 등록 현황**을 색상 지도로 표시합니다. (전국 총 {ev_reg_for_map['ev_count'].sum():,}대)")

# --- 지도 출력 ---
st_folium(m, width='100%', height=600, returned_objects=[])

from st_aggrid import AgGrid, GridOptionsBuilder

# --- 충전소 밀도 비율 표 ---
st.markdown("## ⚖️ 지역별 충전소 밀도 비교 (1기당 차량 수)")

# 데이터 준비
df_ratio = pd.merge(ev_reg_for_map, charger_counts_for_map, on="sido")
df_ratio["충전소 1기당 차량 수"] = (df_ratio["ev_count"] / df_ratio["charger_count"]).round(2)
df_ratio = df_ratio.sort_values(by="충전소 1기당 차량 수", ascending=False)
df_display = df_ratio.rename(columns={
    "sido": "시/도",
    "ev_count": "전기차 등록 대수",
    "charger_count": "충전소 수"
})[["시/도", "전기차 등록 대수", "충전소 수", "충전소 1기당 차량 수"]]

# --- AgGrid 설정 ---
gb = GridOptionsBuilder.from_dataframe(df_display)
gb.configure_default_column(filterable=True, sortable=True, resizable=True)
gb.configure_column("충전소 1기당 차량 수", type=["numericColumn", "numberColumnFilter"], cellStyle={'textAlign': 'center'})
gb.configure_column("전기차 등록 대수", type=["numericColumn"], cellStyle={'textAlign': 'center'})
gb.configure_column("충전소 수", type=["numericColumn"], cellStyle={'textAlign': 'center'})
gridOptions = gb.build()

# --- 표 출력 ---
AgGrid(
    df_display,
    gridOptions=gridOptions,
    height=400,
    fit_columns_on_grid_load=True,
    allow_unsafe_jscode=True,
    theme="alpine"  # "balham", "material", "fresh" 도 있음
)

