from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
from selenium.common.exceptions import StaleElementReferenceException
import os
from selenium.common.exceptions import NoSuchElementException , TimeoutException

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
'''
[문제점]
1. "일시" 와 "공급량. 기온 등" 는 다른 태그 안에 있다. (한 줄씩 수집 불가능)
2. <div> 태그 안에 데이터가 <span> 안에 들어가 있는데, <span>이 한 페이지에 19개 씩 보여지며, 스크롤바를 이용해 다음 데이터를 불러와야함. 
문제는 처음 19개 데이터를 수집하고, 다음 19개를 보기위해 스크롤바를 밑으로 내리면, 새로운 데이터가 새로운 <span>에 생기는 것이 아니라, 기존에 있는 <span>에 데이터라 덮어써짐
더 큰 문제는 덮어지는 순서가 뒤죽박죽임. 예를 들어, 20번째부터 데이터가 보이기 시작하면, 19번째 span이나 1번째 span에 20번째 데이터가 순서대로 덮어씌어져야 하는데
가끔 24번째 와 25번째가 뒤바뀐 경우가 있음.
3. 가끔 데이터 자체가 없는 날이 있다(ex. 2018-05-06)
'''

def collect_daily_data(driver):
    time.sleep(0.5)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(0.5)

    date_list = list()
    value_1_list = list()
    value_2_list = list()
    value_3_list = list()
    value_4_list = list()
    value_5_list = list()
    try:
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="grid1"]/div/div/div[1]/span[2]'))
        )
        element.click()
    except (NoSuchElementException, TimeoutException):
        return
    action = ActionChains(driver) # //*[@id="grid1"]/div/div/div[1]/span[19] //*[@id="grid1"]/div/div/div
    action.send_keys(Keys.ARROW_DOWN).perform()
    is_running = True
    counting = 0
    while is_running :
        before_len = len(date_list)
        for i in range(2,20):
            try:
                date_element = driver.find_element(By.XPATH, f'//*[@id="grid1"]/div/div/div[1]/span[{i}]').text
                if (date_element != "") and (date_element not in date_list):
                    value_1_element = driver.find_element(By.XPATH, f'/html/body/div[2]/div[2]/div/div[2]/div/div[2]/div/div/div/div/div/div[1]/div[5]/span[{5 * (i - 2) + 1}]').text  # 공급능력
                    value_2_element = driver.find_element(By.XPATH, f'/html/body/div[2]/div[2]/div/div[2]/div/div[2]/div/div/div/div/div/div[1]/div[5]/span[{5 * (i - 2) + 2}]').text  # 현재부하
                    value_3_element = driver.find_element(By.XPATH, f'/html/body/div[2]/div[2]/div/div[2]/div/div[2]/div/div/div/div/div/div[1]/div[5]/span[{5 * (i - 2) + 3}]').text  # 공급예비력
                    value_4_element = driver.find_element(By.XPATH, f'/html/body/div[2]/div[2]/div/div[2]/div/div[2]/div/div/div/div/div/div[1]/div[5]/span[{5 * (i - 2) + 4}]').text  # 공급예비율
                    value_5_element = driver.find_element(By.XPATH, f'/html/body/div[2]/div[2]/div/div[2]/div/div[2]/div/div/div/div/div/div[1]/div[5]/span[{5 * (i - 2) + 5}]').text  # 기온

                    date_list.append(date_element)
                    value_1_list.append(value_1_element)
                    value_2_list.append(value_2_element)
                    value_3_list.append(value_3_element)
                    value_4_list.append(value_4_element)
                    value_5_list.append(value_5_element)
                    print(date_element, ',', value_1_element, ',', value_2_element, ',', value_3_element, ',', value_4_element, ',', value_5_element)
                # 시간 "00:00" 일때, 멈추기
                if date_element.find('00:00') != -1:
                    is_running = False
                    break
            except StaleElementReferenceException:
                continue
        after_len = len(date_list)
        if before_len >= after_len: # 종종 새로고침으로 테이블 클릭 사라짐 방지
            driver.find_element(By.XPATH, '//*[@id="grid1"]/div/div/div[1]/span[19]').click()
            for i in range(counting) :
                action.send_keys(Keys.ARROW_DOWN).perform()
            time.sleep(1)
        
        for _ in range(5):
            action.send_keys(Keys.ARROW_DOWN).perform()
            counting += 1
        time.sleep(0.2)
    data = {
        '일시': date_list,
        '공급능력': value_1_list,
        '현재부하': value_2_list,
        '공급예비력': value_3_list,
        '공급예비율': value_4_list,
        '기온': value_5_list
    }

    # 데이터프레임 생성
    df = pd.DataFrame(data)
    df = df.sort_values(by='일시')
    df = df.drop_duplicates(subset='일시')
    # 2018-01-01
    date_format = driver.find_element(By.XPATH, '//*[@id="selEndDate"]').get_attribute("value")
    year = date_format.split("-")[0]
    month = date_format.split("-")[1]

    year_directory = os.path.join("crawling", year)
    month_directory = os.path.join(year_directory, month)

    if not os.path.exists(year_directory):
        os.mkdir(year_directory)

    if not os.path.exists(month_directory):
        os.mkdir(month_directory)
    df.to_csv(os.path.join(month_directory ,date_format+".csv"), index=False)

if __name__ == '__main__':

    selected_year = 2021
    selected_month = 2
    end_year= 2021

    # Chrome 드라이버 경로
    chrome_driver_path = "chromedriver.exe"

    # 브라우저 꺼짐 방지 옵션
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)

    # Chrome 드라이버 초기화
    driver = webdriver.Chrome(options=chrome_options)

    # 창 크기 설정 (너비, 높이)
    driver.set_window_size(1600, 800)

    # 웹 페이지 접속
    driver.get("https://epsis.kpx.or.kr/epsisnew/selectEkgeEpsMepRealChart.do?menuId=030300")
    # 웹 페이지가 완전히 로드될 때까지 대기
    driver.implicitly_wait(10)  # 추가적인 대기 시간 설정 (옵션)

    # 날짜 캘린더 클릭
    driver.find_element(By.XPATH, r'//*[@id="pageChart"]/div/div[1]/div/span[1]/button[1]').click()

    # 날짜 캘린더의 "월"이 n월이 될때까지 이전 버튼 클릭
    first_span = driver.find_element(By.XPATH, r'//*[@id="ui-datepicker-div"]/div/div/span')
    while first_span.text != (str(selected_month)+"월"):
        second_span = driver.find_element(By.XPATH, r'//*[@id="ui-datepicker-div"]/div/a[1]')
        second_span.click()
        time.sleep(0.2)
        first_span = driver.find_element(By.XPATH, r'//*[@id="ui-datepicker-div"]/div/div/span')

    # 날짜 캘린더의 "년"도 "2018" 선택 - 2017년 12월 21일 부터 값 존재
    select = Select(driver.find_element(By.XPATH, r'//*[@id="ui-datepicker-div"]/div/div/select'))
    select.select_by_visible_text(str(selected_year))
    time.sleep(1)
    # 날짜 캘린더의 "일"도 1일 선택
    table_body = driver.find_element(By.XPATH, r'//*[@id="ui-datepicker-div"]/table/tbody')
    tr_elements = table_body.find_elements(By.TAG_NAME, 'tr')
    td_elements = tr_elements[0].find_elements(By.TAG_NAME, 'td')
    for td in td_elements:
        if td.text != " ":
            td.click()
            break

    time.sleep(1)
    # 여백 클릭
    driver.find_element(By.XPATH, r'//*[@id="cont"]/p').click() 
    time.sleep(1)
    # ------------------------ 
    # 날짜 캘린더 클릭
    driver.find_element(By.XPATH, r'//*[@id="pageChart"]/div/div[1]/div/span[1]/button[1]').click()
    time.sleep(0.5)
    while 1 :
        # 해당 월의 마지막 "일" 구하기
        table_body = driver.find_element(By.XPATH, r'//*[@id="ui-datepicker-div"]/table/tbody')
        tr_elements = table_body.find_elements(By.TAG_NAME, 'tr')
        day_elements_xpath = list()
        for tr_index, tr in enumerate(tr_elements):
            td_elements = tr.find_elements(By.TAG_NAME, 'td')
            for td_index, td in enumerate(td_elements):
                if td.text != " ":
                    day_elements_xpath.append(f'//*[@id="ui-datepicker-div"]/table/tbody/tr[{tr_index+1}]/td[{td_index+1}]')
        last_day = driver.find_element(By.XPATH, day_elements_xpath[-1]).text
        
        # 첫번재 클릭
        time.sleep(0.2)
        driver.find_element(By.XPATH, day_elements_xpath[0]).click()

        # 해당 월의 마지막 "일" 될 때까지 반복
        for i in range(int(last_day)):
            # 날짜 캘린더 클릭
            driver.find_element(By.XPATH, r'//*[@id="pageChart"]/div/div[1]/div/span[1]/button[1]').click()
            time.sleep(0.5)

            driver.find_element(By.XPATH, day_elements_xpath[i]).click()
            time.sleep(0.2)
            collect_daily_data(driver)
            

        break

