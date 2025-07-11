import streamlit as st
import pandas as pd
import random
from faker import Faker
import re
import mysql.connector
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="지역별 충전소 개수 확인",
    page_icon="🔎",
    layout="centered"
)

# --- 데이터베이스 연결 함수 ---
@st.cache_resource
def get_db_connection():
    """데이터베이스 연결을 생성합니다."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="ohgiraffers",
            password="ohgiraffers",
            database="primusdb"
        )
        return connection
    except Exception as e:
        st.error(f"데이터베이스 연결 실패: {e}")
        return None



# --- 데이터 로딩 및 처리 함수 (캐시 사용) ---
@st.cache_data
def load_charger_data_from_db():
    """데이터베이스에서 충전소 데이터를 로드합니다."""
    connection = get_db_connection()
    
    if connection is None:
        # 데이터베이스 연결 실패 시 샘플 데이터 사용
        return generate_fake_charger_data()
    
    try:
        # SQL 쿼리로 충전소 데이터 가져오기
        query = """
        SELECT 
            r.province_city as sido,
            r.district_city as sigungu,
            CONCAT(r.province_city, ' ', r.district_city) as addr,
            c.install_year
        FROM ev_charger c
        JOIN region_info r ON c.region_code = r.region_code
        WHERE c.install_year IS NOT NULL
        """
        
        df = pd.read_sql(query, connection)
        connection.close()
        
        if len(df) == 0:
            st.warning("데이터베이스에서 데이터를 찾을 수 없어 샘플 데이터를 사용합니다.")
            return generate_fake_charger_data()
        
        return df
        
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        connection.close()
        return generate_fake_charger_data()

@st.cache_data
def generate_fake_charger_data(num_records=100000):
    """Faker를 사용하여 충전소 샘플 데이터를 생성합니다."""
    fake = Faker('ko_KR')
    data = []
    sido_list = ['서울특별시', '부산광역시', '대구광역시', '인천광역시', '광주광역시', '대전광역시', '울산광역시', '세종특별자치시', '경기도', '강원특별자치도', '충청북도', '충청남도', '전북특별자치도', '전라남도', '경상북도', '경상남도', '제주특별자치도']
    
    for _ in range(num_records):
        sido = random.choice(sido_list)
        full_address = fake.address()
        if not any(s in full_address for s in sido_list):
            full_address = f"{sido} {full_address}"
        
        record = {'addr': full_address}
        data.append(record)
    
    return pd.DataFrame(data)

def extract_sido(address, sido_list):
    """주소에서 시/도 이름을 추출합니다."""
    if '강원' in address: return '강원특별자치도'
    if '전북' in address: return '전북특별자치도'
    for sido_name in sido_list:
        if sido_name in address:
            return sido_name
    return None

def extract_sigungu(address):
    """주소에서 시/군/구 이름을 추출합니다."""
    if '세종특별자치시' in address:
        return '세종시'
    match = re.search(r'(\S+[시군구])(?=\s)', address)
    if match:
        return match.group(1)
    return None

@st.cache_data
def process_data(charger_df):
    """
    데이터베이스에서 온 데이터는 이미 처리된 상태이므로
    sido, sigungu 컬럼이 있으면 그대로 사용하고,
    없으면 주소에서 추출합니다.
    """
    df = charger_df.copy()
    
    # 데이터베이스에서 온 데이터는 이미 sido, sigungu가 있음
    if 'sido' in df.columns and 'sigungu' in df.columns:
        return df.dropna(subset=['sido', 'sigungu']).copy()
    
    # 샘플 데이터인 경우 주소에서 추출
    sido_list = ['서울특별시', '부산광역시', '대구광역시', '인천광역시', '광주광역시', '대전광역시', '울산광역시', '세종특별자치시', '경기도', '강원특별자치도', '충청북도', '충청남도', '전북특별자치도', '전라남도', '경상북도', '경상남도', '제주특별자치도']
    
    df['sido'] = df['addr'].apply(lambda x: extract_sido(x, sido_list))
    df['sigungu'] = df['addr'].apply(extract_sigungu)
    
    processed_df = df.dropna(subset=['sido', 'sigungu']).copy()
    return processed_df

# --- 데이터 로딩 및 전처리 ---
# 먼저 데이터베이스에서 데이터를 시도하고, 실패하면 샘플 데이터 사용
charger_data = load_charger_data_from_db()
charger_data = process_data(charger_data)

# --- 페이지 UI 구성 ---
st.title("🔎 지역별 충전소 개수 조회")
st.markdown("확인하고 싶은 지역을 선택하면, 해당 지역의 실제 충전소 개수를 알려드립니다.")

# 데이터 소스 표시
data_source = "🗄️ **데이터 소스**: " 
if 'install_year' in charger_data.columns:
    data_source += "실제 데이터베이스 (primusdb)"
    st.success(data_source)
else:
    data_source += "샘플 데이터 (데이터베이스 연결 실패)"
    st.warning(data_source)

st.markdown("---")

# --- 지역 선택 메뉴 (두 개의 버튼) ---

# 1. 시/도 선택
unique_sidos = sorted(charger_data['sido'].dropna().unique().tolist())
selected_sido = st.selectbox(
    '**시/도를 선택하세요.**',
    unique_sidos,
    index=0,
    help="대한민국의 시/도 목록입니다."
)

# 2. 시/군/구 선택 (선택된 시/도에 따라 동적으로 변경)
if selected_sido:
    # 선택된 시/도에 해당하는 시/군/구만 필터링
    filtered_sigungu_df = charger_data[charger_data['sido'] == selected_sido]
    unique_sigungus = sorted(filtered_sigungu_df['sigungu'].dropna().unique().tolist())

    if unique_sigungus:
        selected_sigungu = st.selectbox(
            '**시/군/구를 선택하세요.**',
            unique_sigungus,
            index=0,
            help=f"{selected_sido}에 해당하는 시/군/구 목록입니다."
        )
    else:
        st.warning(f"'{selected_sido}'에 해당하는 시/군/구 데이터가 없습니다.")
        selected_sigungu = None
else:
    selected_sigungu = None


st.markdown("---")

# --- 선택된 지역의 충전소 개수 계산 및 표시 ---
if selected_sido and selected_sigungu:
    sigungu_count = len(charger_data[
        (charger_data['sido'] == selected_sido) & 
        (charger_data['sigungu'] == selected_sigungu)
    ])

    st.subheader("💡 조회 결과")
    
    # 데이터 소스에 따라 라벨 변경
    if 'install_year' in charger_data.columns:
        label_text = f"**{selected_sido} {selected_sigungu}**의 충전소 개수"
    else:
        label_text = f"**{selected_sido} {selected_sigungu}**의 샘플 충전소 개수"
    
    st.metric(
        label=label_text,
        value=f"{sigungu_count:,} 개"
    )
    
    # 추가 정보 표시
    if 'install_year' in charger_data.columns:
        # 연도별 설치 현황 보기
        region_data = charger_data[
            (charger_data['sido'] == selected_sido) & 
            (charger_data['sigungu'] == selected_sigungu)
        ]
        
        if len(region_data) > 0 and 'install_year' in region_data.columns:
            st.subheader("📊 연도별 설치 현황")
            year_counts = region_data['install_year'].value_counts().sort_index()
            
            if len(year_counts) > 0:
                # 간단한 막대 차트
                st.bar_chart(year_counts)
                
                # 최신/최구 설치 연도
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("최초 설치년도", f"{year_counts.index.min()}년")
                with col2:
                    st.metric("최근 설치년도", f"{year_counts.index.max()}년")
    
    # --- 추가 분석 및 시각화 ---
    st.markdown("---")
    
    # 1. 전체 지역 비교 시각화
    st.subheader("📈 전체 지역 비교")
    
    # 탭으로 구분
    tab1, tab2, tab3 = st.tabs(["시/도별 비교", "시/군/구별 비교", "연도별 추이"])
    
    with tab1:
        if selected_sido:
            # 전체 시/도별 충전소 개수
            sido_counts = charger_data.groupby('sido').size().reset_index(name='충전소수')
            sido_counts = sido_counts.sort_values('충전소수', ascending=True)
            
            # 선택된 시도를 강조
            colors = ['red' if x == selected_sido else 'lightblue' for x in sido_counts['sido']]
            
            fig = px.bar(
                sido_counts, 
                x='충전소수', 
                y='sido',
                title="전국 시/도별 충전소 개수 비교",
                color=sido_counts['sido'],
                color_discrete_map={selected_sido: 'red'},
                text='충전소수'
            )
            fig.update_traces(texttemplate='%{text}', textposition='outside')
            fig.update_layout(height=600, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            
            # 전국 충전소 정보
            selected_count = sido_counts[sido_counts['sido'] == selected_sido]['충전소수'].iloc[0]
            total_all = sido_counts['충전소수'].sum()
            percentage = (selected_count / total_all * 100) if total_all > 0 else 0
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("선택지역 충전소 수", f"{selected_count:,}개")
            with col2:
                st.metric("전국 대비 비율", f"{percentage:.1f}%")
    
    with tab2:
        if selected_sido and selected_sigungu:
            # 선택된 시/도 내 시/군/구별 비교
            sido_data = charger_data[charger_data['sido'] == selected_sido]
            sigungu_counts = sido_data.groupby('sigungu').size().reset_index(name='충전소수')
            sigungu_counts = sigungu_counts.sort_values('충전소수', ascending=True)
            
            fig = px.bar(
                sigungu_counts, 
                x='충전소수', 
                y='sigungu',
                title=f"{selected_sido} 시/군/구별 충전소 개수",
                color='충전소수',
                color_continuous_scale='Greens',
                text='충전소수'
            )
            fig.update_traces(texttemplate='%{text}', textposition='outside')
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            
            # 시/도 내 비율 정보
            sido_total = sigungu_counts['충전소수'].sum()
            gu_percentage = (sigungu_count / sido_total * 100) if sido_total > 0 else 0
            
            st.metric(f"{selected_sido} 내 비율", f"{gu_percentage:.1f}%")
    
    with tab3:
        if 'install_year' in charger_data.columns:
            # 전국 vs 선택 지역 연도별 설치 추이 비교
            
            # 전국 데이터
            national_yearly = charger_data.groupby('install_year').size().reset_index(name='전국')
            
            # 선택 지역 데이터
            region_yearly = region_data.groupby('install_year').size().reset_index(name='선택지역')
            
            # 데이터 병합
            yearly_comparison = pd.merge(national_yearly, region_yearly, on='install_year', how='outer').fillna(0)
            
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            # 전국 데이터 (막대)
            fig.add_trace(
                go.Bar(x=yearly_comparison['install_year'], y=yearly_comparison['전국'], 
                       name="전국", marker_color='lightblue', opacity=0.7),
                secondary_y=False,
            )
            
            # 선택 지역 데이터 (선)
            fig.add_trace(
                go.Scatter(x=yearly_comparison['install_year'], y=yearly_comparison['선택지역'], 
                           mode='lines+markers', name=f"{selected_sido} {selected_sigungu}", 
                           line=dict(color='red', width=3)),
                secondary_y=True,
            )
            
            fig.update_xaxes(title_text="연도")
            fig.update_yaxes(title_text="전국 설치수", secondary_y=False)
            fig.update_yaxes(title_text="선택지역 설치수", secondary_y=True)
            fig.update_layout(title_text="연도별 충전소 설치 추이 비교", height=400)
            
            st.plotly_chart(fig, use_container_width=True)
    
elif selected_sido and not selected_sigungu:
    st.info(f"'{selected_sido}'에 해당하는 시/군/구를 선택해주세요.")
else:
    st.info("먼저 시/도와 시/군/구를 선택해주세요.")