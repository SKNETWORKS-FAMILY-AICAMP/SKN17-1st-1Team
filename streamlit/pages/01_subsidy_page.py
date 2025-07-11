import streamlit as st
import pandas as pd
import mysql.connector

@st.cache_data
def load_ev_subsidy_data():
    conn = mysql.connector.connect(
        host="localhost",
        user="ohgiraffers",
        password="ohgiraffers",
        database="primusdb"
    )

    query = """
        SELECT 
            es.manufacturer,
            es.model_name,
            es.subsidy_amount,
            ri.province_city,
            ri.district_city
        FROM ev_subsidy es
        INNER JOIN region_info ri ON es.region_code = ri.region_code
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# 데이터 로딩
subsidy_df = load_ev_subsidy_data()

# 페이지 설정
st.set_page_config(page_title="EV 보조금 계산기", layout="wide")
st.title("🚗 전기차 지자체 보조금 계산기 (승용)")
st.info("이 페이지는 2025년 상반기 공개 정보를 기준으로 제작되었으며, 실제 보조금 및 차량 가격은 변동될 수 있습니다.")
st.markdown("---")

st.header("🔍 조건 설정")
st.write(f"현재 **{format(len(subsidy_df), ',')}** 개의 차량 정보를 제공합니다.")

# 시/도 선택
province_list = sorted(subsidy_df['province_city'].dropna().unique())
selected_province = st.selectbox("📍 시/도 선택", options=["-- 선택 --"] + province_list)

# 시/군/구 선택
district_list, selected_district = [], None
if selected_province and selected_province != "-- 선택 --":
    district_df = subsidy_df[subsidy_df['province_city'] == selected_province]
    district_list = sorted(district_df['district_city'].dropna().unique())
    if district_list:
        selected_district = st.selectbox("🏙️ 시/군/구 선택", options=["-- 선택 --"] + district_list)

# 제조사 선택
if selected_province and selected_province != "-- 선택 --":
    if selected_district and selected_district != "-- 선택 --":
        region_filter = (subsidy_df['province_city'] == selected_province) & \
                        (subsidy_df['district_city'] == selected_district)
    else:
        region_filter = (subsidy_df['province_city'] == selected_province)

    region_manufacturers = subsidy_df[region_filter]['manufacturer'].dropna().unique()
    selected_manufacturer = st.selectbox("🚗 제조사 선택", options=["-- 선택 --"] + sorted(region_manufacturers.tolist()))
    
    # 모델 선택
    if selected_manufacturer and selected_manufacturer != "-- 선택 --":
        model_df = subsidy_df[region_filter & (subsidy_df['manufacturer'] == selected_manufacturer)]
        model_df['district_city'] = model_df['district_city'].fillna('')
        model_list = sorted(model_df['model_name'].dropna().unique())
        selected_model = st.selectbox("🚘 차량 모델 선택", options=["-- 선택 --"] + model_list)

        # 보조금 결과 표시
        if selected_model and selected_model != "-- 선택 --":
            row = model_df[model_df['model_name'] == selected_model].iloc[0]
            
            province = selected_province or ""
            district = selected_district or ""
            district_str = f" {district}" if district else ""

            location_info = f"{province}{district_str} / {selected_manufacturer} / {selected_model}"

            st.markdown(f"""
                <div style="background-color:#F0FAF4;padding:30px;border-radius:20px;text-align:center;">
                    <h2 style="color:#27AE60;font-size:32px;">💰 보조금 금액</h2>
                    <h1 style="color:#219653;font-size:48px;">{row['subsidy_amount']:,} 만원</h1>
                    <p style="font-size:16px;">{location_info}</p>
                </div>
            """, unsafe_allow_html=True)