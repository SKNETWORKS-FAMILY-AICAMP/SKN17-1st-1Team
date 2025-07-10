import mysql.connector
import csv
connection = mysql.connector.connect(
    host="localhost",               
    user="ohgiraffers",              
    password="ohgiraffers",         
    database="primusdb"               
)

cursor = connection.cursor()

file_path = 'faq.csv'
# 2. 파일을 열고, 그 파일 객체를 f 라는 변수로 사용합니다.

with open(file_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)  # 첫 줄은 헤더니까 건너뜀

    for i, row in enumerate(reader):
        question = row[1]  # 첫 번째 컬럼이 질문
        answer = row[2]    # 두 번째 컬럼이 답변

        values = ('jeju', question, answer)  
        sql = "INSERT INTO faq (faq_type, faq_title, faq_answer) VALUES (%s, %s, %s)"
        cursor.execute(sql, values)

connection.commit()
cursor.close()
connection.close()