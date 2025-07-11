import mysql.connector
import pandas as pd



file_path = 'car_entity_with_location_code.csv' # 경로 본인 상태에 맞게 수정 요망!
cars_df = pd.read_csv(file_path, encoding='utf-8')

""" 이런 케이스 groupby 처리
249  2294     충청북도  청주시  237.0
250  2121     충청북도  청주시  237.0
251  2255     충청북도  청주시  237.0
252  3972     충청북도  청주시  237.0
253  2694     충청북도  충주시  238.0
"""
cars_df = cars_df.groupby(['지역코드'], as_index=False)['승용'].sum()
print(cars_df)

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