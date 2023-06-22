'''
5분 단위로 데이터가 존재하는지 확인하는 py파일
'''

import os
import pandas as pd
import glob

def check_csv_files(directory):
    # file_list = glob.glob(directory + '/**/*.csv', recursive=True)
    # for file_path in file_list:
    #     file_name = os.path.basename(file_path)
    file_path = directory
    df = pd.read_csv(file_path, encoding='cp949')
    missing_times = find_missing_times(df['기준일시'])

    if missing_times:
        print(f"{0}: {', '.join(missing_times)}\n")

def find_missing_times(time_column):
    expected_times = [f"{hour:02d}:{minute:02d}" for hour in range(24) for minute in range(0, 60, 5)]
    existing_times = time_column.str[-5:].unique()
    missing_times = [time for time in expected_times if time not in existing_times]
    
    return missing_times

# 크롤링 디렉토리 경로
directory = 'data\한국전력거래소_5분단위 전력수급현황_20220407.csv'

# 디렉토리 탐색 및 CSV 파일 분석
check_csv_files(directory)
