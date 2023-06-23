

def preprocess_data(data, 결측치_처리방법):
    # 데이터 전처리 작업 수행
    # 예시: 결측치 처리, 이상치 제거, 데이터 변환 등

    # 컬럼 삭제
    data = data.drop(['기준일시','공급능력(MW)','최대예측수요(MW)','공급예비력(MW)','공급예비율(퍼센트)','운영예비력(MW)','운영예비율(퍼센트)','기온'], axis=1)

    # 현재수요 Nan 제거
    data = data.dropna(subset=['현재수요(MW)'])

    # object to int
    data['현재수요(MW)'] = data['현재수요(MW)'].str.replace(",", "").astype(float).apply(lambda x: round(x))

    return data