from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import time
import pandas as pd


# 크롬드라이버 실행
path = 'chromedriver.exe'
service = Service(path)
driver = webdriver.Chrome(service=service)

# 페이지 접속
driver.get('https://jejuevservice.com/echarger')
time.sleep(1)

# - 스크롤 처리(한번)
driver.execute_script("window.scrollBy(0, 500);")     
time.sleep(1)

q_a_list = []

def parse_faq_page():
    # 화살표 누르기
    faq_buttons = driver.find_elements(By.CSS_SELECTOR, "i.acd_icon.fa.fa-sort-down") 
    for btn in faq_buttons:
        btn.click()
        time.sleep(0.3)

    # 데이터 가져오기
    faq_items = driver.find_elements(By.CSS_SELECTOR, "div.acd_body")
    for item in faq_items:
        content_div = item.find_element(By.CSS_SELECTOR, ".board_contents.fr-view")
        p_tags = content_div.find_elements(By.TAG_NAME, "p")

        question = ""
        answer_lines = ""

        for _, p in enumerate(p_tags):
            text = p.text.strip()
            if not text:
                continue
            if text.startswith("Q:"):
                question = text
            elif len(p_tags) >= 1:
                question = p_tags[0].text.strip()
                answer_lines = [p.text.strip() for p in p_tags[1:] if p.text.strip()]
                concat_answer = ' '.join(answer_lines)
                
                

                
            else:
                #answer_lines.append(text)
                concat_answer = text

        
        q_a_list.append((question,concat_answer))

page2 = driver.find_element(By.LINK_TEXT, "1")
time.sleep(1)
parse_faq_page()



page2 = driver.find_element(By.LINK_TEXT, "2")
page2.click()
time.sleep(1)
parse_faq_page()


# 종료
driver.quit()

