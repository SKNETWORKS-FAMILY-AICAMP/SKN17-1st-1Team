import requests
import math
import pandas as pd 


base_url = "https://api.odcloud.kr/api"
get_url = "/15142951/v1/uddi:4b80ee12-8cb5-4ac9-b08b-fd58b7dac635"
request_url = base_url + get_url
service_key = "V7WX8wu3WbY17WbChZbu6WRpJZkjCOaW8mIEr7Y8Nvn7uiY8Bksa8FmZY2rVsKYQA+LXrDrX3qvAkDbIZzLQpA==" # 발급받은 키 (보안주의)


params = {
    "page": 1,
    "perPage": 1,  # 한 건만 가져와서 총 개수만 확인
    "serviceKey": service_key
}
response = requests.get(request_url, params=params)
data = response.json()
total_count = data['totalCount']

#print(f"총 데이터 개수: {total_count}")

per_page = 100
total_pages = math.ceil(total_count / per_page)




# 지역별 등록된 전기차 정보 담는 리스트
registered_evs = [] 



for page in range(1, total_pages + 1):
    params = {
        "page": page,
        "perPage": per_page,
        "serviceKey": service_key
    }
    response = requests.get(request_url, params=params)
    items = response.json().get('data', [])
    registered_evs.extend(items)




