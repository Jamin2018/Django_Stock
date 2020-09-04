import tushare as ts
import pandas as pd
import time

max_row = 1000

pd.set_option('display.width', 300)
pd.set_option('display.max_columns', 300)
pd.set_option('display.max_colwidth', 300)
pd.set_option('display.max_row', max_row)

import sys

"""
大盘指数监控
"""

n = 0
while True:
    df = ts.get_index()
    df.rename(columns={'close': '现价', }, inplace=True)

    df['t'] = (df['现价'] - df['preclose']) / df['preclose'] * 100

    s = """上证指数：%.2f%% %.2f  深证成指：%.2f%% %.2f 创业板指：%.2f%% %.2f""" % (
    df[df['name'] == '上证指数']['t'].values[0],
    df[df['name'] == '上证指数']['现价'].values[0],

    df[df['name'] == '深证成指']['t'].values[0],
    df[df['name'] == '深证成指']['现价'].values[0],

    df[df['name'] == '创业板指']['t'].values[0],
    df[df['name'] == '创业板指']['现价'].values[0],
)
    print('\r' + str(s), end='', flush=True)
    time.sleep(3)
