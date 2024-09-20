import csv
import time
import os
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 설정
options = Options()
options.add_argument('--headless')  # Headless 모드
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')

# 헤더 설정
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
options.add_argument(f'user-agent={user_agent}')

# 크롬 드라이버 경로 입력
driver = webdriver.Chrome(options=options)

# 수집한 제목, 내용 등등을 저장할 리스트
titles = []
contents = []
posters = []
created_times = []

# 갤러리명
gallery = 'programming'

# 저장 경로(현재 파일 경로)
path = os.getcwd()

# CSV 파일을 저장할 경로
filename = os.path.join(path, 'crawler.csv')

# 저장된 최신글 번호를 가져오는 함수
def get_saved_post_number():
    try:
        with open(filename, 'r', encoding='utf-8-sig') as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)  # 모든 행을 리스트로 가져옴
            if len(rows) > 1:  # 헤더를 제외하고 데이터가 있을 때
                last_row = rows[-1]  # 마지막 행을 가져옴
                return int(last_row[0])  # 첫 번째 열(글 번호)을 정수로 변환해서 반환
            else:
                return 0 # 데이터가 없을 경우 0을 반환
    except FileNotFoundError:
        return 0  # 파일이 없을 경우 0을 반환

while True:
    for page in range(1, 2):
        print(f'{page}페이지 수집중...')
        url = f'https://gall.dcinside.com/board/lists/?id=' + gallery + '&page={page}'
        driver.get(url)

        # 현재 페이지 HTML 가져오기
        html = driver.page_source

        # HTML 파싱
        soup = BeautifulSoup(html, 'html.parser')

        # 글번호 찾기
        num_elements = soup.find_all('td', class_='gall_num')
        nums = [int(num.get_text(strip=True)) for num in num_elements if num.get_text(strip=True).isdigit()]
        nums.reverse()

        # 저장된 가장 최신 글 번호를 가져와서 최신글과 비교
        saved_post_number = get_saved_post_number()
        new_posts = [num for num in nums if num > saved_post_number]

        if new_posts:
            for num in new_posts:  # 저장하지 않은 글만 수집
                try:
                    print(f'{num}번 글 수집중...')
                    post_url = 'https://gall.dcinside.com/board/view/?id=' + gallery + '&no=' + str(num)
                    driver.get(post_url)

                    # 요소가 모두 로딩될 때까지 최대 20초 대기
                    WebDriverWait(driver, 20).until(
                        EC.visibility_of_element_located((By.CLASS_NAME, 'write_div'))
                    )

                    post_html = driver.page_source
                    post_soup = BeautifulSoup(post_html, 'html.parser')

                    # 제목 찾기
                    title_element = post_soup.find('span', class_='title_subject')
                    title = title_element.get_text(strip=True) if title_element else '제목 없음'
                    titles.append(title)

                    # 내용 찾기
                    content_element = post_soup.find('div', class_='write_div')
                    content = content_element.get_text(strip=True) if content_element else '내용 없음'
                    contents.append(content)

                    # 작성자 찾기
                    poster_element = post_soup.find('span', class_='nickname')
                    poster = poster_element.get('title') if poster_element else '작성자 없음'
                    posters.append(poster)

                    # 작성 시각 찾기
                    time_element = post_soup.find('span', class_='gall_date')
                    created_time = time_element.get('title') if time_element else '작성일 없음'
                    created_times.append(created_time)

                    print(f'{num}번 글 수집 완료.')
                except Exception as e:
                    print(f"Error {num}: {e}")
                    continue

                time.sleep(0.3)

            print('CSV 파일로 저장중...')

            # CSV 파일 열기
            with open(filename, 'a', encoding='utf-8-sig', newline='') as csvfile:
                writer = csv.writer(csvfile)
                # 헤더는 처음 한 번만 작성하고, 이후에는 생략
                if os.path.getsize(filename) == 0:  # 파일이 비어있을 경우에만 헤더 작성
                    writer.writerow(['번호', '제목', '내용', '작성자', '작성일'])
                for i in range(len(titles)):
                    writer.writerow([new_posts[i], titles[i], contents[i], posters[i], created_times[i]])

            print(f'{filename} 파일로 저장되었습니다.')

        else:
            print('최신글이 없습니다.')

    time.sleep(5)


