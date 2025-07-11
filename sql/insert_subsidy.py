import mysql.connector
import pandas as pd



file_path = 'final_subsidy_data.csv' # 경로 본인 상태에 맞게 수정 요망!
subsidy_df = pd.read_csv(file_path, encoding='utf-8')
print(subsidy_df)

connection = mysql.connector.connect(
    host="localhost",           # MYSQL 서버 주소
    user="root",         # 사용자 이름
    password="uyer1897@@",     # 비밀번호
    database="primusdb"           # 사용할 데이터비이스(스키마)
)

cursor = connection.cursor()

sql = "INSERT INTO EV_Subsidy (region_code, manufacturer, model_name, subsidy_amount)" \
"VALUES (%s, %s, %s, %s)"

# 각 행을 반복해서 DB에 INSERT
for idx, row in subsidy_df.iterrows():
    region_code = int(row['지역코드'])+1 if pd.notna(row['지역코드']) else None
    manufacturer = str(row['제조사']) if pd.notna(row['제조사']) else None
    model_name = str(row['모델']) if pd.notna(row['모델']) else None
    subsidy_amount = int(row['보조금']) if pd.notna(row['보조금']) else None

    values = (region_code, manufacturer, model_name, subsidy_amount)

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