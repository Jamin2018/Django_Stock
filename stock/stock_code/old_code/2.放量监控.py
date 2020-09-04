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

tk = config['ts_token']
dir = config['work_dir']
dir = dir + '/k_line/'
ts.set_token(tk)
pro = ts.pro_api()


def update_stock_csv(ma=[5, 20, 50, 250]):
    df_stock_code = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    for index, row in df_stock_code.iterrows():
        code = row["ts_code"]
        df = ts.pro_bar(ts_code=code, adj='qfq', ma=ma)
        stock_file_name = code + '.csv'
        df.to_csv(dir + 'stock_D_csv/' + stock_file_name)
        print(dir + 'stock_D_csv/' + stock_file_name , index)
    return df_stock_code

def k_line_v_break(df_stock_code, division=10):
    day = 50
    division = 10
    # 开始执行K线突破判断
    print('开始执行K线放量突破判断')
    # 记录突破的code
    stock_break_code = []
    # 设置突破线
    # df_stock_code = df_stock_code[:3]
    for row in df_stock_code:
        f = 'ma_v_250'
        code = row
        df = pd.read_csv(dir + 'stock_D_csv/%s.csv' % code)
        df = df.dropna(axis=0, how='any', subset=[f])
        df = df[:day]
        if len(df) == day:
            d1 = df[:division]
            d2 = df[division:day]
            position1 = d1['vol'] > (d1['ma_v_250'] * 3)# 3倍均量线小于最高为false
            position2 = (d2['vol']) < d2['ma_v_250'] * 1.5

            # position1.sum() 统计True的个数，即价钱大于均线，记录近期突破的天数，若不为0，则表示近期突破了均线
            # position2.sum() 统计True的个数，即价钱大于均线，记录长期突破的天数，若为0，则表示长期处于均线以下
            if position1.sum() > 5 and position2.sum() > (day-division) * 0.8:
                stock_break_code.append(code)

    d = pd.DataFrame(data=stock_break_code, columns=['code'], dtype=None, copy=False)
    d.to_csv(dir + 'res/' + f + '_%s.csv' % time.strftime('%Y_%m_%d_', time.localtime(time.time())), index=None)
    print('执行完毕:')
    print(stock_break_code)


def run(ma, updata=False):
    # 查询当前所有正常上市交易的股票列表
    if updata:
        df_stock_code = update_stock_csv(ma)
        df_stock_code = df_stock_code["ts_code"]
        print('数据更新完毕')
    else:
        df_stock_code = []
        path = dir + 'stock_D_csv/'
        for root, dirs, files in os.walk(path):
            for i in files:
                df_stock_code.append(i[:-4])
        print('使用已有数据')
    if len(df_stock_code):
        # ======================================================
        k_line_v_break(df_stock_code)   # K线突破
        # ======================================================
        #                   可添加新的判断方法
        #
        # ======================================================


if __name__ == '__main__':
    """
    策略思想:
    是区间时间内成交量大于均量的3倍，之前都是在均线附近的交易量，用于牛市初期
    """
    run(ma=[5, 20, 50, 250],)