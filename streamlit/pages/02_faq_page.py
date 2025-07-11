import streamlit as st
import mysql.connector # MySQL 연결을 위한 라이브러리 임포트
import pandas as pd # 데이터를 구조화하기 위해 pandas 사용 (선택 사항이지만 편리함)

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="기업별 전기차 FAQ",
    page_icon="🙋‍♂️",
    layout="wide"
)

# --- 앱 제목 및 설명 ---
st.title("🙋‍♂️ 기업별 전기차 FAQ (자주 묻는 질문)")
st.info("궁금한 질문을 클릭하면 답변을 확인하실 수 있습니다.")
st.divider()


# --- FAQ 데이터 로드 함수 ---
@st.cache_data # 데이터를 캐싱하여 앱 성능 향상 (DB에서 데이터를 한 번만 가져옴)
def get_faq_data_from_db():
    """ MySQL 데이터베이스에서 기업별 FAQ 데이터를 불러옵니다. """
    faq_data = {} # 최종적으로 반환할 FAQ 데이터 딕셔너리

    try:
        # 1. MySQL 데이터베이스 연결 설정
        # 이전 스크립트에서 사용하신 연결 정보를 바탕으로 설정합니다.
        # 실제 비밀번호를 'your_password_here' 대신 입력해주세요.
        connection = mysql.connector.connect(
            host="localhost",
            user="ohgiraffers",
            password="ohgiraffers", # ✨ 여기에 실제 MySQL 비밀번호를 입력하세요 ✨
            database="primusdb"
        )

        if connection.is_connected():
            # st.success("데이터베이스에 성공적으로 연결되었습니다.")
            cursor = connection.cursor(dictionary=True) # 딕셔너리 형태로 결과를 가져오도록 설정

            # 2. FAQ 데이터를 저장한 테이블에서 정보 조회
            # 테이블 이름은 'faq_questions'라고 가정합니다.
            # 실제 테이블 이름과 컬럼명(company, question, answer)을 확인해주세요.
            query = "SELECT faq_code, faq_type, faq_title, faq_answer FROM faq ORDER BY faq_code" # question_id는 정렬을 위한 예시 컬럼명

            cursor.execute(query)
            records = cursor.fetchall() # 모든 결과 가져오기

            # 3. 조회된 데이터를 Streamlit 앱에서 사용할 수 있는 형태로 가공
            for row in records:
                faq_code = row['faq_code']
                faq_type = row['faq_type']
                faq_title = row['faq_title']
                faq_answer = row['faq_answer']

                if faq_type not in faq_data:
                    faq_data[faq_type] = [] # 새로운 기업이면 리스트 생성

                faq_data[faq_type].append({"질문": faq_title, "답변": faq_answer})

            # st.success(f"총 {len(records)}개의 FAQ 데이터를 데이터베이스에서 불러왔습니다.")
            
    except mysql.connector.Error as err:
        # 데이터베이스 연결 또는 쿼리 실행 중 오류 발생 시
        st.error(f"데이터베이스 오류 발생: {err}")
        st.warning("데이터베이스 연결 정보(호스트, 사용자, 비밀번호, DB명) 또는 테이블/컬럼명을 확인해주세요.")
        st.info("임시로 하드코딩된 데이터를 사용합니다.")
        # 오류 발생 시 임시 데이터 (또는 빈 데이터)를 반환하여 앱이 작동하도록 함
        faq_data = {
            "기아": [
                {"질문": "데이터 로드 실패: 기아 FAQ", "답변": "데이터베이스 연결에 실패했거나 데이터를 불러오는 중 오류가 발생했습니다. 콘솔의 오류 메시지를 확인하세요."}
            ],
            "제주전기자동차서비스": [
                {"질문": "데이터 로드 실패: 제주전기자동차서비스 FAQ", "답변": "데이터베이스 연결에 실패했거나 데이터를 불러오는 중 오류가 발생했습니다. 콘솔의 오류 메시지를 확인하세요."}
            ]
        }
    finally:
        # 연결이 열려있으면 닫기
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            # st.info("데이터베이스 연결이 종료되었습니다.")
            
    return faq_data

# --- 페이지 렌더링 함수 ---
def render_faq_page():
    """ 기업별 FAQ 페이지 렌더링 """
    # DB에서 데이터를 가져오는 함수 호출
    faq_data = get_faq_data_from_db()
    
    # 동적으로 탭 생성
    # faq_data의 키(기업명)를 기반으로 탭을 생성합니다.
    # 탭 순서를 고정하고 싶다면, `list(faq_data.keys())` 대신 `["기아", "제주전기자동차서비스"]`와 같이 명시적으로 지정할 수 있습니다.
    company_names = list(faq_data.keys())
    tabs = st.tabs([f"**{name}**" for name in company_names])

    for i, company_name in enumerate(company_names):
        with tabs[i]:
            st.subheader(f"{company_name} 전기차 관련 주요 질문")
            if company_name in faq_data and faq_data[company_name]:
                for item in faq_data[company_name]:
                    with st.expander(f"**{item['질문']}**"):
                        st.write(item['답변'])
            else:
                st.warning(f"{company_name}에 대한 FAQ 데이터가 없습니다.")


# --- 메인 앱 실행 ---
if __name__ == "__main__":
    render_faq_page()

