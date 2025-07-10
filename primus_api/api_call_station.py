import requests
import math

# API 요청 정보
base_url = "https://api.odcloud.kr/api"
get_url = "/15125089/v1/uddi:00dd2278-6e4b-459e-9ad2-b7b3f876513a"
request_url = base_url + get_url
service_key = "V7WX8wu3WbY17WbChZbu6WRpJZkjCOaW8mIEr7Y8Nvn7uiY8Bksa8FmZY2rVsKYQA+LXrDrX3qvAkDbIZzLQpA==" # 발급받은 키 (보안주의)

# 1. 데이터 총 카운트 확인
params = {
    "page": 1,
    "perPage": 1,  # 한 건만 가져와서 총 개수만 확인
    "serviceKey": service_key
}
response = requests.get(request_url, params=params)
data = response.json()
total_count = data['totalCount']

# print(f"총 데이터 개수: {total_count}") # 361,163 

# 2. API 호출 (전체 요청 시작)
per_page = 100
total_pages = math.ceil(total_count / per_page) 
#total_pages = math.ceil(2000 / per_page) # 너무 많으니까 테스트 는 작게 해서 보기


# 지역별 설치된 충전소 정보 담는 리스트
registered_station = [] 



for page in range(1, total_pages + 1): 
    params = {
        "page": page,
        "perPage": per_page,
        "serviceKey": service_key
    }
    response = requests.get(request_url, params=params)
    items = response.json().get('data', [])
    registered_station.extend(items)


