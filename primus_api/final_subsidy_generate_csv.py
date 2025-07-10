from subsidy_crawling import results
import pandas as pd
import numpy as np

subsidy_df = pd.DataFrame(results)

subsidy_df.columns = ['시도', '시군구', '제조사', '모델', '보조금']

# 쉼표 제거, float 형으로 변환
subsidy_df['보조금'] = subsidy_df['보조금'].astype(str).str.replace(',', '')
subsidy_df['보조금'] = subsidy_df['보조금'].astype(float)


sido_name_map = {
    '서울': '서울특별시',
    '부산': '부산광역시',
    '대구': '대구광역시',
    '인천': '인천광역시',
    '광주': '광주광역시',
    '대전': '대전광역시',
    '울산': '울산광역시',
    '세종': '세종특별자치시',
    '경기': '경기도',
    '강원': '강원특별자치도',
    '충북': '충청북도',
    '충남': '충청남도',
    '전북': '전북특별자치도',
    '전남': '전라남도',
    '경북': '경상북도',
    '경남': '경상남도',
    '제주': '제주특별자치도'
}

subsidy_df['시도'] = subsidy_df['시도'].map(sido_name_map)


# '시도'와 '시군구'가 같은 경우 → '시군구'를 NaN으로 변경
subsidy_df.loc[subsidy_df['시군구'] == subsidy_df['시도'], '시군구'] = np.nan
# '시도'가 NaN인 행 제거
subsidy_df = subsidy_df.dropna(subset=['시도'])

# 지역테이블 정보 불러오기
location_code_path = 'c:/skn_17/SKN17-1st-1Team/primus_api/final_location_df.csv'

# CSV 파일 읽기
try:
    location_code_df = pd.read_csv(location_code_path, encoding='utf-8')  # encoding='cp949'도 한글 인코딩 깨질 때 시도해봐
    #print("CSV 파일 로딩 완료!")
    #print(location_code_df.head())  # 상위 5개 행 출력
except FileNotFoundError:
    print(f"파일을 찾을 수 없습니다: {location_code_path}")
except Exception as e:
    print(f"파일 로딩 중 오류 발생: {e}")


# 보조금 테이블에 지역코드 넣어주기
#merged_df = subsidy_df.merge(location_code_df, on=['시도', '시군구'], how='left')
final_subsidy_df = subsidy_df.merge(location_code_df, on=['시도', '시군구'])


# csv로 저장
final_subsidy_df.to_csv('final_subsidy_data.csv', index=False, encoding='utf-8-sig')