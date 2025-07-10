import pandas as pd
import numpy as np

# 1. 차량등록 엔티티 생성
registered_evs = pd.read_csv('registered_evs_data.csv', encoding='utf-8-sig')
registered_evs_df = pd.DataFrame(registered_evs)

# 전처리 및 그룹화
selected_columns = ['시군구별', '승용']
filtered_df = registered_evs_df[selected_columns]
grouped_df = filtered_df.groupby('시군구별', as_index=False).sum()
split_data = grouped_df['시군구별'].str.split(' ', expand=True)
grouped_df['시도'] = split_data[0]
grouped_df['시군구'] = split_data[1]
grouped_df = grouped_df.drop('시군구별', axis=1)

registered_station = pd.read_csv('registered_station_data.csv', encoding='utf-8-sig')
registered_station_df = pd.DataFrame(registered_station)

columns_to_drop = [
    '기종(대)',
    '기종(소)',
    '시설구분(대)',
    '시설구분(소)',
    '운영기관(대)',
    '운영기관(소)',
    '이용자제한',
    '충전기타입',
    '충전소명',
    '주소'
]


registered_station_df = registered_station_df.drop(columns=columns_to_drop, axis=1)
cols = registered_station_df.columns.tolist()
cols.remove('군구')
insert_pos = cols.index('시도') + 1
cols.insert(insert_pos, '군구')
registered_station_df = registered_station_df[cols]
registered_station_df = registered_station_df.rename(columns={'군구': '시군구'})

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

grouped_df['시도'] = grouped_df['시도'].map(sido_name_map)
car_entity = grouped_df
location_df = grouped_df[['시도', '시군구']]
location_df = location_df.drop_duplicates(subset=['시도', '시군구']).reset_index(drop=True)
location_entity = location_df
station_location_df = registered_station_df[['시도','시군구']]
station_location_df_no_duplicates = station_location_df.drop_duplicates()

# 두 데이터프레임에서 '시도'와 '시군구' 컬럼만 선택하여 합치기
combined_df = pd.concat([
    car_entity[['시도', '시군구']],
    location_entity[['시도', '시군구']]
])

# 중복된 행 제거
combined_df.drop_duplicates(inplace=True)
# 정렬 (예: '시도' 컬럼으로 먼저 정렬 후 '시군구' 컬럼으로 정렬)
combined_df.sort_values(by=['시도', '시군구'], inplace=True)
combined_df.dropna(inplace=True) # Null값 들어간 row 지우기
# 인덱스 값 초기화
combined_df.reset_index(drop=True, inplace=True)

combined_location_df = combined_df
combined_location_df1 = combined_location_df.reset_index().rename(columns={'index': '지역코드'})

local_list = ['서울 서울특별시', '부산 부산광역시', '대구 대구광역시', '인천 인천광역시', '광주 광주광역시', '대전 대전광역시', '울산 울산광역시', '세종 세종특별자치시', '경기 수원시', '경기 성남시', '경기 의정부시', '경기 안양시', '경기 부천시', '경기 광명시', '경기 평택시', '경기 동두천시', '경기 안산시', '경기 고양시', '경기 과천시', '경기 구리시', '경기 남양주시', '경기 오산시', '경기 시흥시', '경기 군포시', '경기 의왕시', '경기 하남시', '경기 용인시', '경기 파주시', '경기 이천시', '경기 안성시', '경기 김포시', '경기 화성시', '경기 광주시', '경기 양주시', '경기 포천시', '경기 여주시', '경기 연천군', '경기 가평군', '경기 양평군', '강원 춘천시', '강원 원주시', '강원 강릉시', '강원 동해시', '강원 태백시', '강원 속초시', '강원 삼척시', '강원 홍천군', '강원 횡성군', '강원 영월군', '강원 평창군', '강원 정선군', '강원 철원군', '강원 화천군', '강원 양구군', '강원 인제군', '강원 고성군', '강원 양양군', '충북 청주시', '충북 충주시', '충북 제천시', '충북 보은군', '충북 옥천군', '충북 증평군', '충북 영동군', '충북 진천군', '충북 괴산군', '충북 음성군', '충북 단양군', '충남 천안시', '충남 공주시', '충남 보령시', '충남 아산시', '충남 서산시', '충남  논산시', '충남 계룡시', '충남 당진시', '충남 금산군', '충남 부여군', '충남 서천군', '충남 청양군', '충남 홍성군', '충남 예산군', '충남 태안군', '전북 전주시', '전북 군산시', '전북 익산시', '전북 정읍시', '전북 남원시', '전북 김제시', '전북 완주군', '전북 진안군', '전북 무주군', '전북 장수군', '전북 임실군', '전북 순창군', '전북 고창군', '전북 부안군', '전남 목포시', '전남 여수시', '전남 순천시', '전남 나주시', '전남 광양시', '전남 담양군', '전남 곡성군', '전남 구례군', '전남 고흥군', '전남 보성군', '전남 화순군', '전남 장흥군', '전남 강진군', '전남 해남군', '전남 영암군', '전남 무안군', '전남 함평군', '전남 영광군', '전남 장성군', '전남 완도군', '전남 진도군', '전남 신안군', '경북 포항시', '경북 경주시', '경북 김천시', '경북 안동시', '경북 구미시', '경북 영주시', '경북 영천시', '경북 상주시', '경북 문경시', '경북 경산시', '경북 의성군', '경북 청송군', '경북 영양군', '경북 영덕군', '경북 청도군', '경북  고령군', '경북 성주군', '경북 칠곡군', '경북 예천군', '경북 봉화군', '경북 울진군', '경북 울릉군', '경남 창원시', '경남 진주시', '경남 통영시', '경남 사천시', '경남 김해시', '경남 밀양시', '경남 거제시', '경남 양산시', '경남 의령군', '경남 함안군', '경남 창녕군', '경남 고성군', '경남 남해군', '경남 하동군', '경남 산청군', '경남 함양군', '경남 거창군', '경남 합천군', '제주 제주특별자치도']
local_df = pd.DataFrame(local_list, columns=['시도'])
local_df[['시도','군구']] = local_df['시도'].str.split(' ', n=1, expand=True)

local_df['시도'] = local_df['시도'].map(sido_name_map)
local_df = local_df.rename(columns={'군구': '시군구'})
subsidiary_location = local_df

combined_location_final_df = pd.concat([
    combined_location_df1[['시도', '시군구']],
    subsidiary_location[['시도', '시군구']]
])

# 중복된 행 제거
combined_location_final_df.drop_duplicates(inplace=True)
# 정렬 (예: '시도' 컬럼으로 먼저 정렬 후 '시군구' 컬럼으로 정렬)
combined_location_final_df.sort_values(by=['시도', '시군구'], inplace=True)
combined_location_final_df.dropna(inplace=True) # Null값 들어간 row 지우기
# 인덱스 값 초기화
combined_location_final_df.reset_index(drop=True, inplace=True)

final_location_df = combined_location_final_df.reset_index().rename(columns={'index': '지역코드'})
final_location_df.loc[final_location_df['시도'] == final_location_df['시군구'], '시군구'] = np.nan


car_entity_with_location_code = pd.merge(
    car_entity,
    final_location_df[['시도', '시군구', '지역코드']], # location_entity에서 필요한 컬럼만 선택
    on=['시도', '시군구'], # 병합할 기준 컬럼
    how='left' # car_entity의 모든 행을 유지
)

car_entity_with_location_code['지역코드'] = car_entity_with_location_code['지역코드'].astype('Int64')

station_entity_with_location_code = pd.merge(
    registered_station_df,
    final_location_df[['시도', '시군구', '지역코드']], # location_entity에서 필요한 컬럼만 선택
    on=['시도', '시군구'], # 병합할 기준 컬럼
    #how='left' # registered_station_df의 모든 행을 유지
)

s1 = station_entity_with_location_code.drop('급속충전량', axis=1)
s2 = s1.drop('위도경도', axis=1)
s2['지역코드'] = s2['지역코드'].astype('Int64')


s2.to_csv('station_entity_with_location_code.csv', index=False, encoding='utf-8-sig')
final_location_df.to_csv('final_location_df.csv', index=False, encoding='utf-8-sig')
car_entity_with_location_code.to_csv('car_entity_with_location_code.csv', index=False, encoding='utf-8-sig')