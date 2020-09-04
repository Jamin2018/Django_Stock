import tushare as ts
import sys, os
import json
import pandas as pd
import time

from core.StockEigenvalueExtraction import StockEigenvalueExtraction

max_row = 1000

pd.set_option('display.width', 300)
pd.set_option('display.max_columns', 300)
pd.set_option('display.max_colwidth', 300)
pd.set_option('display.max_row', max_row)


curPath = os.path.abspath(os.path.dirname(__file__))
parent_path = os.path.dirname(curPath) #获得d所在的目录,即d的父级目录

config_path = parent_path
with open(config_path + '/config.json', 'r', encoding='utf8')as fp:
    conf = json.load(fp)

data_dir = conf['options']['data_dir']

c = ['code','name','price','open','pre_close','high','low','bid','ask','volume','amount','time']

monitoring_code = ['sh', 'sz', 'cyb']

ktype = '60'

SEE = StockEigenvalueExtraction()

def current_kdj(df_y, current_df):
    cn = float(current_df['close'].values[0])
    ln_list = list(df_y['low']) + [float(current_df['low'].values[0])]
    hn_list = list(df_y['high']) + [float(current_df['high'].values[0])]

    ln = min(ln_list)
    hn = max(hn_list)
    rsv = ((cn-ln)/(hn-ln)) * 100
    yk = df_y[:1]['kdj_k'].values[0]
    yd = df_y[:1]['kdj_d'].values[0]
    k = yk*2/3 + rsv/3
    d = yd*2/3 + k/3
    j = 3*k - 2*d
    return k,d,j

while True:
    time.sleep(3)
    for code in monitoring_code:
        df_yesterday = pd.read_csv(data_dir + '/stock_%s_csv/%s.csv' % (ktype, code), index_col=['date'])

        df_yesterday = df_yesterday.sort_index()  # 要正序才能计算KDJ
        df_yesterday = SEE.kdj(df_yesterday)
        df_yesterday = df_yesterday.sort_index(ascending=False)  # 倒序
        df_y = df_yesterday[:8]

        df = ts.get_realtime_quotes(code)  # Single stock symbol
        df.rename(
            columns={
                'price': 'close',
            }, inplace=True)
        k, d, j = current_kdj(df_y, df)
        if k >= d:
            print(
                """\033[31m%s  %s  | K(%.1f)  D(%.1f) J(%.1f) | 昨收:%s  当前:%s""" % (df['time'].values[0], code, k, d, j,df_y[:1]['close'].values[0], df['close'].values[0])
            )
        else:
            print(
                """\033[31m%s  %s  | K(%.1f)  D(%.1f) J(%.1f) | 昨收:%s  当前:%s""" % (df['time'].values[0], code, k, d, j,df_y[:1]['close'].values[0], df['close'].values[0])
            )

    print('\033[30m---------------------------------------------------------------------------------------------------')