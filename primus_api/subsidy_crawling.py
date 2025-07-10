from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd

# 1. chrome 브라우저 실행
path = 'chromedriver.exe'
#path = './chromedriver.exe'
service = webdriver.chrome.service.Service(path)
driver = webdriver.Chrome(service=service)

# 2. url 접근
driver.get('https://ev.or.kr/nportal/buySupprt/initSubsidyPaymentCheckAction.do')
time.sleep(1)

# 지자체 차종별 보조금
popup_btn = driver.find_element(By.XPATH, "//a[contains(text(), '지자체 차종별 보조금')]")
popup_btn.click()
time.sleep(1)

# 3. 팝업으로 전환
main_window = driver.current_window_handle
while len(driver.window_handles) == 1:
    time.sleep(0.5)
popup_window = [w for w in driver.window_handles if w != main_window][0]
driver.switch_to.window(popup_window)
time.sleep(1)

# 4. 시도, 지역 선택 후 데이터 가져오기
btn_info_list = []
buttons = driver.find_elements(By.CSS_SELECTOR, 'a.btnDown')
for i, btn in enumerate(buttons):
    parent_tr = btn.find_element(By.XPATH, "./ancestor::tr")
    tds = parent_tr.find_elements(By.TAG_NAME, "td")

    sido = tds[0].text.strip()
    sigungu = tds[1].text.strip()

    btn_info_list.append((i, sido, sigungu))

# 맨 마지막 항목(공단 데이터) 제외
btn_with_region = btn_info_list[:-1]

# 크롤링 결과를 저장할 변수 생성
results = []

for idx, (btn_idx, sido, gungu) in enumerate(btn_info_list):
    buttons = driver.find_elements(By.CSS_SELECTOR, 'a.btnDown')
    btn = buttons[btn_idx]

    before_popup_handles = driver.window_handles
    btn.click()
    time.sleep(1)

    # 팝업 대기
    while len(driver.window_handles) == len(before_popup_handles):
        time.sleep(0.2)
    new_popup = [h for h in driver.window_handles if h not in before_popup_handles][0]
    driver.switch_to.window(new_popup)
    time.sleep(1)

    # 테이블 추출
    thead_th = driver.find_element(By.CSS_SELECTOR, 'table.table01.fz15 thead tr th')
    if '차종' in thead_th.text:
        rows = driver.find_elements(By.CSS_SELECTOR, "table.table01.fz15 tr")
        for row in rows[1:]:
            try:
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) >= 6:
                    COMPANY = cols[1].text.strip()
                    MODEL = cols[2].text.strip()
                    PRICE = cols[5].text.strip()
                    results.append([sido, gungu, COMPANY, MODEL, PRICE])
            except Exception as e:
                print(f"❗row 파싱 중 오류 발생❗: {e}")
                continue
   
    driver.close()

    driver.switch_to.window(popup_window)
    time.sleep(2)

# 결과 확인
print(f"\n총 {len(results)}개 항목 수집 완료!")
print(results)

# 5. 브라우저 종료 (드라이버 종료)
driver.quit()


