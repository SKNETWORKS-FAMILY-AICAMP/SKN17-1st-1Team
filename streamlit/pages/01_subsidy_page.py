import streamlit as st
import pandas as pd
import numpy as np
import random

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="EV 보조금 계산기",
    page_icon="🚗",
    layout="wide"
)

# --- 앱 제목 및 설명 ---
st.title("🚗 2025 전기차 보조금 계산기 (승용)")
st.info("이 페이지는 2025년 상반기 공개 정보를 기준으로 제작되었으며, 실제 보조금 및 차량 가격은 변동될 수 있습니다.")
st.markdown("---")

# --- 데이터 로드 함수 (승용차 전용) ---
@st.cache_data
def load_passenger_ev_data():
    """ 2025년 기준 17,235개의 가상 승용 전기차 데이터를 생성합니다. """
    num_entries = 17235
    # 데이터 생성 시 '현대', '기아'가 포함되도록 유지합니다.
    manufacturers_pool = ['현대', '기아', 'Tesla', 'BMW', 'Mercedes-Benz', 'Audi', 'Volvo', 'Polestar', 'KG Mobility', 'GM']
    model_prefixes = ['IONIQ', 'EV', 'Kona', 'Niro', 'Model', 'i', 'EQ', 'e-tron', 'XC', 'C']
    model_suffixes = ['Standard', 'Long Range', 'Performance', '2WD', 'AWD', 'Pro', 'Light', 'GT', 'Air']

    data = {
        'manufacturer': [random.choice(manufacturers_pool) for _ in range(num_entries)],
        'model': [f"{random.choice(model_prefixes)}{i} {random.choice(model_suffixes)}" for i in range(num_entries)],
        'price': np.random.randint(2500, 9500, size=num_entries) * 10000,
        'gov_subsidy_base': np.random.randint(200, 700, size=num_entries) * 10000,
    }
    df = pd.DataFrame(data)
    # 중복 모델명 제거하여 고유하게 만듦
    df = df.drop_duplicates(subset=['model'], keep='first').reset_index(drop=True)
    return df

@st.cache_data
def get_local_passenger_subsidy():
    """ 지역별 승용차 지자체 보조금 """
    return {'서울': 1500000, '부산': 2500000, '대구': 2500000, '인천': 2800000, '광주': 3500000, '대전': 2000000, '울산': 2500000, '세종': 1500000, '경기': 2000000, '강원': 3000000, '충북': 5000000, '충남': 4000000, '전북': 4500000, '전남': 5500000, '경북': 5000000, '경남': 5000000, '제주': 3000000}

# 데이터 로딩
ev_df = load_passenger_ev_data()
local_subsidy_data = get_local_passenger_subsidy()

# --- 메인 화면: 사용자 입력 ---
st.header("🔍 조건 설정")
# 현대, 기아 차량만 필터링하여 카운트
filtered_ev_df = ev_df[ev_df['manufacturer'].isin(['현대', '기아'])]
st.write(f"현재 **{len(filtered_ev_df)}**개의 현대, 기아 차량 정보를 제공합니다.")
col1, col2, col3 = st.columns(3)


with col1:
    region = st.selectbox("📍 거주 지역", options=list(local_subsidy_data.keys()))

with col2:
    # --- 이 부분을 수정했습니다 ---
    # 제조사 목록을 '현대', '기아'로 고정합니다.
    manufacturers = ['현대', '기아']
    selected_manufacturer = st.selectbox("🚗 제조사", options=manufacturers)

with col3:
    # 선택된 제조사(현대 또는 기아)에 따라 모델 리스트 필터링 및 정렬
    model_list = sorted(list(filtered_ev_df[filtered_ev_df['manufacturer'] == selected_manufacturer]['model']))
    if not model_list:
        selected_model = None
    else:
        selected_model = st.selectbox("🚘 차량 모델", options=model_list)

st.markdown("---")


if selected_model:
    # --- 메인 화면: 결과 분석 ---
    car_info = filtered_ev_df[filtered_ev_df['model'] == selected_model].iloc[0]

    st.header(f"'{selected_model}' 구매 비용 분석")

    price = car_info['price']
    gov_subsidy_base = car_info['gov_subsidy_base']

    # --- 보조금 계산 로직 (승용차 전용) ---
    if price >= 85000000:
        gov_subsidy = 0
    elif price >= 55000000:
        gov_subsidy = gov_subsidy_base * 0.5
    else:
        gov_subsidy = gov_subsidy_base

    local_subsidy_base_amount = local_subsidy_data[region]
    # 국고 보조금 비율에 따라 지방비 보조금 계산
    local_subsidy = local_subsidy_base_amount * (gov_subsidy / gov_subsidy_base) if gov_subsidy_base > 0 else 0

    # 최종 계산
    total_subsidy = gov_subsidy + local_subsidy

    # --- 결과 표시 ---
    # 중앙 정렬을 위해 빈 컬럼 사용
    _, res_col, _ = st.columns([1, 1, 1])
    res_col.metric("총 보조금", f"▼ {total_subsidy/10000:,.1f} 만원")

else:
    st.warning("선택된 제조사의 차량 모델이 없습니다. 다른 제조사를 선택해주세요.")