import tushare as ts
import pandas as pd
import json
import time

import sys,os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]    #这里的rootpath是你的工程根目录
sys.path.append(rootPath)

max_row = 1000

pd.set_option('display.width', 300)
pd.set_option('display.max_columns', 300)
pd.set_option('display.max_colwidth', 300)
pd.set_option('display.max_row', max_row)

config_path = rootPath


with open(config_path + '\config.json', 'r', encoding='utf8')as fp:
    config = json.load(fp)

dir = config['work_dir']
dir = dir + '/k_line/'


def kdj(df, fastk_period=9, slowk_period=3, slowd_period=3):
    # 计算kd指标
    low_list = df['low'].rolling(9, min_periods=9).min()
    low_list.fillna(value=df['low'].expanding().min(), inplace=True)
    high_list = df['high'].rolling(9, min_periods=9).max()
    high_list.fillna(value=df['high'].expanding().max(), inplace=True)
    rsv = (df['close'] - low_list) / (high_list - low_list) * 100

    df['KDJ_K'] = pd.DataFrame(rsv).ewm(com=2).mean()
    df['KDJ_D'] = df['KDJ_K'].ewm(com=2).mean()
    df['KDJ_J'] = 3 * df['KDJ_K'] - 2 * df['KDJ_D']
    return df

def kdj_jincha(df, j_k=100, j_d=100, j_j=30, d_k=0, d_d=0, d_j=80):
    """

    :param df:
    :param j_k: 金叉买入点k
    :param j_d: 金叉买入点d
    :param j_j: 金叉买入点j
    :param d_k: 死叉卖出点k
    :param d_d: 死叉卖出点d
    :param d_j: 死叉卖出点j
    :return:
    """
    # 计算KDJ指标金叉、死叉情况

    d = df.dropna(axis=0, how='any', subset=["KDJ_K", "KDJ_D", "KDJ_J"])

    d['KDJ_金叉死叉'] = ''
    kdj_position = d['KDJ_K'] > d['KDJ_D']
    d.loc[kdj_position[(kdj_position == True) & (kdj_position.shift() == False)].index, 'KDJ_金叉死叉'] = '金叉'
    d.loc[kdj_position[(kdj_position == False) & (kdj_position.shift() == True)].index, 'KDJ_金叉死叉'] = '死叉'

    # df['KDJ_res'] = ''
    # df.loc[d[(d['KDJ_金叉死叉'] == '金叉') & (d['KDJ_K'] < j_k) & (d['KDJ_D'] < j_d) & (d['KDJ_J'] < j_j)].index, 'KDJ_res'] = True
    # df.loc[d[(d['KDJ_金叉死叉'] != '金叉') & (d['KDJ_K'] > d_k) & (d['KDJ_D'] > d_d) & (d['KDJ_J'] > d_j)].index, 'KDJ_res'] = False

    d['KDJ_res'] = ''
    d.loc[d[(d['KDJ_金叉死叉'] == '金叉') & (d['KDJ_K'] < j_k) & (d['KDJ_D'] < j_d) & (d['KDJ_J'] < j_j)].index, 'KDJ_res'] = True
    d.loc[d[(d['KDJ_金叉死叉'] != '金叉') & (d['KDJ_K'] > d_k) & (d['KDJ_D'] > d_d) & (d['KDJ_J'] > d_j)].index, 'KDJ_res'] = False

    d = d.dropna(axis=0, how='any', subset=["KDJ_金叉死叉", "KDJ_res",])

    return d

def get_kdj_jincha(k='D'):
    df_stock_code = []
    path = dir + 'stock_%s_csv/' % k
    for root, dirs, files in os.walk(path):
        for i in files:
            df_stock_code.append(i[:-4])
    # df_stock_code = df_stock_code[:10]

    # 用日期做索引，两个数据的表头不一样
    if k == 'D':
        index_col = 'trade_date'
    elif k=='60':
        index_col = 'date'

    df_kdj = []
    for row in df_stock_code:
        code = row
        df = pd.read_csv(dir + 'stock_%s_csv/%s.csv' % (k, code), index_col=[index_col])
        df = df.sort_index()    # 要正序才能计算KDJ
        df = kdj(df)
        df = kdj_jincha(df)
        df = df.sort_index(ascending=False) # 倒序判断
        if not df.empty and True in df[:1]['KDJ_res'].values:
            df_kdj.append(code)

    d = pd.DataFrame(data=df_kdj, columns=['code'], dtype=None, copy=False)
    d.to_csv(dir + 'res/' + 'KDJ_%s_%s.csv' % (k, time.strftime('%Y_%m_%d_', time.localtime(time.time()))), index=None)
    print('执行完毕:')
    print(df_kdj)
    return df_kdj

def get_d_kdj_to_select(df_stock_code):
    '''
    通过了d日的，继续判断60的，J小于一定数值
    :param df_kdj:
    :return:
    '''
    k = 'D'
    df_kdj = []
    for row in df_stock_code:
        code = row
        code = change_code_name(code)
        df = pd.read_csv(dir + 'stock_%s_csv/%s.csv' % (k, code), index_col=['trade_date'])
        df = df.sort_index()    # 要正序才能计算KDJ
        df = kdj(df)
        df = kdj_jincha(df)
        df = df.sort_index(ascending=False) # 倒序判断
        if not df.empty and df[:1]['KDJ_J'].values[0] < 0 and df[:1]['KDJ_K'].values[0] < 15:
            df_kdj.append(code)

    d = pd.DataFrame(data=df_kdj, columns=['code'], dtype=None, copy=False)
    d.to_csv(dir + 'res/' + 'KDJ_composite_%s_%s.csv' % (k, time.strftime('%Y_%m_%d_', time.localtime(time.time()))), index=None)
    print('执行完毕:')
    print(df_kdj)
    return df_kdj

def change_code_name(code):
    if code[:1] == '6':
        code = code + '.SH'
    else:
        code = code + '.SZ'
    return code

if __name__ == '__main__':
    """
    策略思想:
    找出近3个区间的金叉
    """
    df_kdj = get_kdj_jincha(k='60')
    get_d_kdj_to_select(df_kdj)
