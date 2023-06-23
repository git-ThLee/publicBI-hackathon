import pandas as pd
import numpy as np
import os
import random
import torch
from statsmodels.tsa.arima.model import ARIMA

def set_seed(seed):
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)  # if use multi-GPU
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

def split_train_test_data(data, train_start, train_end, test_start, test_end):
    # 날짜 기준으로 데이터 정렬
    data['기준일시'] = pd.to_datetime(data['기준일시'])
    data = data.sort_values('기준일시')

    # train 데이터와 test 데이터 추출
    train_data = data[(data['기준일시'] >= train_start) & (data['기준일시'] <= train_end)]
    test_data = data[(data['기준일시'] >= test_start) & (data['기준일시'] <= test_end)]

    return train_data, test_data

def get_model(model_name,data):
    if model_name == 'arima':
        '''
        p (AR 차수): 자기회귀(AR, Autoregressive) 모형의 차수로, 현재 값과 이전 시간 단계의 값을 사용하여 예측합니다. 이전 값의 영향력을 의미합니다. 값이 클수록 과거의 영향이 더 크게 반영됩니다.
        d (차분 차수): 차분(Difference) 차수로, 시계열 데이터의 정상성을 확보하기 위해 필요한 차분 횟수입니다. 데이터가 정상성을 갖지 않을 경우, 차분을 통해 추세나 계절성을 제거하고 예측을 수행합니다. 일반적으로 차분 차수는 1 이상으로 설정됩니다.
        q (MA 차수): 이동평균(MA, Moving Average) 모형의 차수로, 이전 예측 오차를 사용하여 예측합니다. 예측 오차의 이동 평균을 계산하여 현재 값에 대한 예측을 수행합니다. 값이 클수록 이전 예측 오차의 영향이 더 크게 반영됩니다.
        '''
        model = ARIMA(data, order=(1, 1, 1))
    else:
        raise Exception("model name is incorrect")

    return model