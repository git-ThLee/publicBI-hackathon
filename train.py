from utils import *
from preprocess import *

import click
import torch
from easydict import EasyDict
import os
import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt

from sklearn.metrics import mean_absolute_error

#######통계 라이브러리##########
from statsmodels.tsa.arima.model import ARIMA

DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

@click.command()

# Required.
#@click.option('--outdir',       help='Where to save the results',           metavar='DIR',      type=str,           required=True)
@click.option('--datadir',      help='Data path',                           metavar='DIR',      type=str,           required=True)
@click.option('--model_name',   help='Model name to train',                 metavar='STR',      type=str,           required=True)

# Optional features.
@click.option('--seed',         help='Random seed',                         metavar='INT',      type=click.IntRange(min=0),                 default=0)

def main(**kwargs):
    ## Arguments
    opts = EasyDict(kwargs)
    print(opts)

    # Seed 
    set_seed(opts.seed)

    # Data load 
    data = pd.read_csv(opts['datadir'], dtype=str)  # 데이터셋 파일명에 맞게 수정
    # train 데이터와 test 데이터 분할
    train_start = '2012-01-01'
    train_end = '2023-03-12'
    test_start = '2023-03-13'
    test_end = '2023-03-19'
    train_data, test_data = split_train_test_data(data, train_start, train_end, test_start, test_end)

    # Preprocess
    train_data = preprocess_data(train_data)
    test_data = preprocess_data(test_data)
    print(train_data.info())
    # Train
    '''
    p (AR 차수): 자기회귀(AR, Autoregressive) 모형의 차수로, 현재 값과 이전 시간 단계의 값을 사용하여 예측합니다. 이전 값의 영향력을 의미합니다. 값이 클수록 과거의 영향이 더 크게 반영됩니다.
    d (차분 차수): 차분(Difference) 차수로, 시계열 데이터의 정상성을 확보하기 위해 필요한 차분 횟수입니다. 데이터가 정상성을 갖지 않을 경우, 차분을 통해 추세나 계절성을 제거하고 예측을 수행합니다. 일반적으로 차분 차수는 1 이상으로 설정됩니다.
    q (MA 차수): 이동평균(MA, Moving Average) 모형의 차수로, 이전 예측 오차를 사용하여 예측합니다. 예측 오차의 이동 평균을 계산하여 현재 값에 대한 예측을 수행합니다. 값이 클수록 이전 예측 오차의 영향이 더 크게 반영됩니다.
    '''
    print('model')
    model = get_model(opts.model_name, train_data)

    print('fit')
    model_fit = model.fit()
    print('fit end')
    # ARIMA 모델을 사용하여 예측 수행
    steps = len(test_data)
    print('predict')
    forecast = model_fit.forecast(steps=steps)
    print('predict end')
    print(forecast)

    # 실제값과 예측값 추출
    actual_values = test_data['현재수요(MW)']  # 실제값 컬럼명을 'target_column'으로 변경해야 함
    predicted_values = forecast[0]  # 예측값은 forecast의 첫 번째 요소로 추출됨

    # MAPE 계산
    mape = np.mean(np.abs((actual_values - predicted_values) / actual_values)) * 100
    print('MAPE:', mape)

if __name__ == '__main__':
    main()