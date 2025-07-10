import mysql.connector
import pandas as pd



file_path = 'C:/skn_17/SKN17-1st-1Team/primus_api/car_entity_with_location_code.csv'
cars_df = pd.read_csv(file_path, encoding='utf-8')

connection = mysql.connector.connect(
    host="localhost",           # MYSQL 서버 주소
    user="ohgiraffers",         # 사용자 이름
    password="ohgiraffers",     # 비밀번호
    database="primusdb"           # 사용할 데이터비이스(스키마)
)

cursor = connection.cursor()

sql = "INSERT INTO EV_Registration (region_code, registrtation_count)" \
"VALUES (%s, %s)"

# 각 행을 반복해서 DB에 INSERT
for idx, row in cars_df.iterrows():
    region_code = int(row['지역코드'])+1 if pd.notna(row['지역코드']) else None
    registrtation_count = int(row['승용']) if pd.notna(row['승용']) else None

    values = (region_code, registrtation_count)

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