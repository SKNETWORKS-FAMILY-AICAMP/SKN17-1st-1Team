from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import time
import os

def crawl_kia_ev_faq_with_selenium(url):
    driver_path = os.path.join(os.getcwd(), 'chromedriver.exe') 
   
    if not os.path.exists(driver_path):
        print(f"오류: ChromeDriver를 찾을 수 없습니다. 경로를 다시 확인해주세요: {driver_path}")
        print("ChromeDriver를 다운로드하여 이 스크립트와 같은 폴더에 두거나, 정확한 경로를 지정해야 합니다.")
        return {}

    
    service = Service(driver_path)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless') 
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    options.add_argument('accept-language=ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7')

    driver = None 
    try:
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
       
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'cmp-accordion__item'))
        )
       
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        faq_data = {}
        
        faq_items = soup.find_all('div', class_='cmp-accordion__item')

        if not faq_items:
            print("오류: Selenium으로 로드한 페이지에서도 'cmp-accordion__item' 클래스를 가진 FAQ 항목을 찾을 수 없습니다.")
            print("이는 웹사이트 구조가 예상과 매우 다르거나, 다른 동적 로딩 방식이 사용될 수 있음을 의미합니다.")
            return {}

        print("정보: 명시적인 카테고리 섹션을 찾을 수 없어, 모든 FAQ 항목을 '전체 FAQ'로 묶어 처리합니다.")
        
        category_title = '전체 FAQ'
        current_category_faqs = []

        for item in faq_items:
            question_button = item.find('button', class_='cmp-accordion__button')
            question_tag = question_button.find('span', class_='cmp-accordion__title') if question_button else None
            
            answer_panel = item.find('div', class_='cmp-accordion__panel')
            
            answer_text = "답변을 찾을 수 없습니다."
            if answer_panel:
                paragraphs = answer_panel.find_all('p')
                if paragraphs:
                    answer_text = '\n'.join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
                else:
                    answer_text = answer_panel.get_text('\n', strip=True)

            question = question_tag.get_text(strip=True) if question_tag else "질문을 찾을 수 없습니다."
            
            current_category_faqs.append({
                "질문": question,
                "답변": answer_text
            })
        
        if current_category_faqs:
            faq_data[category_title] = current_category_faqs

        return faq_data

    except Exception as e:
        print(f"Selenium 크롤링 중 오류 발생: {e}")
        return {}
    finally:
        if driver: 
            driver.quit() 

if __name__ == "__main__":
    kia_faq_url = "https://www.kia.com/kr/vehicles/kia-ev/guide/faq"
    print(f"'{kia_faq_url}'에서 기아 EV FAQ 크롤링을 시작합니다...")

    crawled_data = crawl_kia_ev_faq_with_selenium(kia_faq_url)

    if crawled_data:
        print("\n--- 크롤링된 데이터 ---")
        print(json.dumps(crawled_data, indent=4, ensure_ascii=False))
        
        file_name = 'kia_ev_faq_crawled.json'
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(crawled_data, f, indent=4, ensure_ascii=False)
        print(f"\n데이터가 '{file_name}' 파일로 저장되었습니다.")
    else:
        print("크롤링된 데이터가 없거나 오류가 발생했습니다.")


