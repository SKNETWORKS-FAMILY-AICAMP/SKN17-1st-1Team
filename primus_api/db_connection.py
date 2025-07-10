import mysql.connector
import json
connection = mysql.connector.connect(
    host="localhost",               
    user="ohgiraffers",              
    password="ohgiraffers",         
    database="primusdb"               
)

cursor = connection.cursor()

file_path = 'kia_ev_faq_crawled.json'
# 2. 파일을 열고, 그 파일 객체를 f 라는 변수로 사용합니다.

# 'r'은 읽기 모드(read), encoding='utf-8'은 한글 깨짐 방지를 위해 필수입니다.
with open(file_path, 'r', encoding='utf-8') as f:
    json_faq = json.load(f)

# 1. '전체 FAQ' 키로 리스트에 접근합니다.
faq_list = json_faq['전체 FAQ']

# 2. 반복문을 돌면서 각 '질문'과 '답변'을 하나씩 출력합니다.
for i, faq_item in enumerate(faq_list):
    question = faq_item['질문']
    answer = faq_item['답변']
    values = ('kia',question, answer,)
    sql = "INSERT INTO faq (faq_type, faq_title, faq_answer) VALUES (%s, %s,%s)"

    cursor.execute(sql, values)

    # print(f"--- {i+1}번째 FAQ ---")
    # print(f"질문: {question}")
    # print(f"답변: {answer}\n")

connection.commit()
