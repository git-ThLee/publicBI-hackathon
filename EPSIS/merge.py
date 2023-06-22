'''
1. 수집한 2022-2023 데이터 merge하는 py파일
2. 수집한 2022-2023 데이터와 기존 5분단위 데이터 merge하는 py파일
'''
### 수집한 2022 ~ 2023 데이터 merge 코드
# import os
# import glob
# import pandas as pd

# # CSV 파일이 있는 디렉토리 경로
# directory = 'crawling'

# # 모든 CSV 파일의 경로 가져오기
# csv_files = glob.glob(os.path.join(directory, '**/*.csv'), recursive=True)

# # CSV 파일들을 담을 빈 데이터프레임 생성
# merged_df = pd.DataFrame()

# # 모든 CSV 파일을 순회하며 데이터프레임에 추가
# for csv_file in csv_files:
#     df = pd.read_csv(csv_file)  # CSV 파일 읽기
#     merged_df = pd.concat([merged_df, df], ignore_index=True)  # 데이터프레임에 추가

# # 결과를 하나로 합친 CSV 파일로 저장
# merged_df.to_csv('merged.csv', index=False)
# print(merged_df)
### -------------------------------------------------------------------------------------------
### 기존 5분단위 데이터와 새로 수집한 5분 단위 데이터 merge 
import pandas as pd

# A.csv 파일과 B.csv 파일 경로
file_a = 'data\한국전력거래소_5분단위 전력수급현황_20220407.csv'
file_b = 'EPSIS\merged.csv'

# A.csv 파일 읽기
df_a = pd.read_csv(file_a, encoding='cp949')

# B.csv 파일 읽기
df_b = pd.read_csv(file_b)

# A.csv와 B.csv 합치기
merged_df = pd.concat([df_a, df_b], ignore_index=True)

# 결과를 합쳐진 CSV 파일로 저장
merged_df.to_csv('all_merged.csv', index=False)