import mysql.connector
import pandas as pd



file_path = "C:/Users/Playdata/Desktop/SKN17-1st-1Team/primus_api/final_location_df.csv" # 경로 본인 상태에 맞게 수정 요망!
location_df = pd.read_csv(file_path, encoding='utf-8')

connection = mysql.connector.connect(
    host="localhost",           # MYSQL 서버 주소
    user="ohgiraffers",         # 사용자 이름
    password="ohgiraffers",     # 비밀번호
    database="primusdb"           # 사용할 데이터비이스(스키마)
)

cursor = connection.cursor()

sql = "INSERT INTO Region_Info (province_city, district_city)" \
"VALUES (%s, %s)"

# 각 행을 반복해서 DB에 INSERT
for idx, row in location_df.iterrows():
    province_city = str(row['시도']) if pd.notna(row['시도']) else None
    district_city = str(row['시군구']) if pd.notna(row['시군구']) else None

    values = (province_city, district_city)

    try:
        cursor.execute(sql, values)
    except Exception as e:
        print(f"[ERROR] {idx}번째 row에서 오류 발생: {e}")
        continue  # 오류가 나도 다음 row로 계속 진행

# commit 처리
connection.commit()

print(f"@@@{cursor.rowcount}개의 행 삽입 완료@@@")

cursor.close()
connection.close()