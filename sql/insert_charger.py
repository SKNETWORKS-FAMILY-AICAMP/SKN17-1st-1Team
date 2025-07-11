import mysql.connector
import pandas as pd



file_path = 'station_entity_with_location_code.csv' # 경로 본인 상태에 맞게 수정 요망!
charger_df = pd.read_csv(file_path, encoding='utf-8')
print(charger_df)

connection = mysql.connector.connect(
    host="localhost",           # MYSQL 서버 주소
    user="ohgiraffers",         # 사용자 이름
    password="ohgiraffers",     # 비밀번호
    database="primusdb"           # 사용할 데이터비이스(스키마)
)

cursor = connection.cursor()

sql = "INSERT INTO EV_Charger (region_code, install_year)" \
"VALUES (%s, %s)"

# 각 행을 반복해서 DB에 INSERT
for idx, row in charger_df.iterrows():
    region_code = int(row['지역코드'])+1 if pd.notna(row['지역코드']) else None
    install_year = int(row['설치년도']) if pd.notna(row['설치년도']) else None

    values = (region_code, install_year)

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