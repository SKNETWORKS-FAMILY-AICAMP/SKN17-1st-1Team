import streamlit as st
import pandas as pd

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="EV 보조금 계산기 (승용/화물)",
    page_icon="🚚",
    layout="wide"
)

# --- 앱 제목 및 설명 ---
st.title("🚗 2025 전기차 보조금 계산기 (승용/화물)")
st.info("이 페이지는 2025년 상반기 공개 정보를 기준으로 제작되었으며, 실제 보조금 및 차량 가격은 변동될 수 있습니다.")


# --- 데이터 로드 함수 ---
@st.cache_data
def load_passenger_ev_data():
    """ 2025년 기준 승용 전기차 데이터 """
    data = {
        'manufacturer': ['현대', '현대', '현대', '현대', '현대', '기아', '기아', '기아', '기아', '기아', '기아'],
        'model': ['아이오닉 5 (롱레인지)', '아이오닉 6 (롱레인지)', '코나 일렉트릭 (롱레인지)', '아이오닉 5 N', '캐스퍼 일렉트릭', 'EV6 (롱레인지)', 'EV9 (2WD 롱레인지)', '니로 EV', '레이 EV', 'EV3 (롱레인지)', 'EV5 (스탠다드)'],
        'price': [54100000, 56050000, 47520000, 76000000, 31500000, 52600000, 73370000, 51400000, 27750000, 42080000, 51500000],
        'gov_subsidy_base': [6500000, 6500000, 6340000, 2690000, 5000000, 6300000, 3010000, 5810000, 4520000, 6000000, 6500000]
    }
    return pd.DataFrame(data)

@st.cache_data
def load_commercial_ev_data():
    """ 2025년 기준 화물 전기차 데이터 """
    data = {
        'manufacturer': ['현대', '기아'],
        'model': ['포터 II 일렉트릭', '봉고 III EV'],
        'price': [43950000, 43650000],
        'gov_subsidy_base': [10500000, 10500000] # 소형 화물 기준
    }
    return pd.DataFrame(data)

@st.cache_data
def get_local_passenger_subsidy():
    """ 지역별 승용차 지자체 보조금 """
    return {'서울': 1500000, '부산': 2500000, '대구': 2500000, '인천': 2800000, '광주': 3500000, '대전': 2000000, '울산': 2500000, '세종': 1500000, '경기': 2000000, '강원': 3000000, '충북': 5000000, '충남': 4000000, '전북': 4500000, '전남': 5500000, '경북': 5000000, '경남': 5000000, '제주': 3000000}

@st.cache_data
def get_local_commercial_subsidy():
    """ 지역별 화물차 지자체 보조금 (승용차와 다를 수 있음 - 예시) """
    return {'서울': 2500000, '부산': 3000000, '대구': 3500000, '인천': 4000000, '광주': 4500000, '대전': 3000000, '울산': 3500000, '세종': 2000000, '경기': 3000000, '강원': 4000000, '충북': 6000000, '충남': 5000000, '전북': 5500000, '전남': 6000000, '경북': 6000000, '경남': 6000000, '제주': 4000000}


# --- 사이드바: 사용자 입력 ---
with st.sidebar:
    st.header("🔍 조건 설정")

    # 1. 차종 선택 (승용/화물)
    vehicle_type = st.radio("차종 선택", ("승용", "화물"), horizontal=True)

    # 2. 선택된 차종에 따라 데이터 로드
    if vehicle_type == "승용":
        ev_df = load_passenger_ev_data()
        local_subsidy_data = get_local_passenger_subsidy()
    else: # 화물
        ev_df = load_commercial_ev_data()
        local_subsidy_data = get_local_commercial_subsidy()

    # 3. 소상공인 추가 지원 여부 (화물차일 때만 표시)
    is_small_business = False
    if vehicle_type == "화물":
        st.markdown("---")
        is_small_business = st.checkbox("✅ 소상공인 추가 지원 적용 (국비 30%)")
        st.caption("소상공인이 전기 화물차 구매 시 국비 지원액의 30%가 추가 지원됩니다.")
        st.markdown("---")

    # 4. 지역 선택
    region = st.selectbox("📍 거주 지역", options=list(local_subsidy_data.keys()))

    # 5. 제조사 선택
    manufacturers = sorted(list(ev_df['manufacturer'].unique()))
    selected_manufacturer = st.selectbox("🚗 제조사", options=manufacturers)

    # 6. 모델 선택
    model_list = sorted(list(ev_df[ev_df['manufacturer'] == selected_manufacturer]['model']))
    selected_model = st.selectbox("🚘 차량 모델", options=model_list)


# --- 메인 화면: 결과 분석 ---
car_info = ev_df[ev_df['model'] == selected_model].iloc[0]

st.header(f"'{selected_model}' 구매 비용 분석")
st.markdown("---")

price = car_info['price']
gov_subsidy_base = car_info['gov_subsidy_base']
gov_subsidy = 0
local_subsidy = 0

# --- 보조금 계산 로직 ---
# 승용차 보조금 계산
if vehicle_type == "승용":
    if price >= 85000000:
        gov_subsidy = 0
    elif price >= 55000000:
        gov_subsidy = gov_subsidy_base * 0.5
    else:
        gov_subsidy = gov_subsidy_base
    
    local_subsidy_base_amount = local_subsidy_data[region]
    local_subsidy = local_subsidy_base_amount * (gov_subsidy / gov_subsidy_base) if gov_subsidy_base > 0 else 0

# 화물차 보조금 계산
else: # 화물
    gov_subsidy = gov_subsidy_base
    if is_small_business:
        gov_subsidy += (gov_subsidy_base * 0.3) # 소상공인 30% 추가 지원
    
    # 화물차 지자체 보조금은 국비와 별개로 정액 지급되는 경우가 많음 (예시)
    local_subsidy = local_subsidy_data[region]


# 최종 계산
total_subsidy = gov_subsidy + local_subsidy
final_price = price - total_subsidy

# --- 결과 표시 ---
col1, col2, col3 = st.columns(3)
col1.metric("차량 기본가", f"{price/10000:,.1f} 만원")
col2.metric("총 보조금", f"▼ {total_subsidy/10000:,.1f} 만원")
col3.metric("최종 구매가", f"{final_price/10000:,.1f} 만원")

st.progress(total_subsidy / price if price > 0 else 0)
st.caption("차량 가격 대비 총 보조금 비율")
st.markdown("---")


# --- 전체 데이터 테이블 ---
st.subheader(f"📊 {vehicle_type} 전기차 데이터 비교")
st.dataframe(ev_df)