import sys, os
import json
import pandas as pd
from multiprocessing import Pool
import os
import time
from core.StockApi import StockApi
pd.set_option('display.width', 300)
pd.set_option('display.max_columns', 300)
pd.set_option('display.max_colwidth', 300)
pd.set_option('display.max_row', 1000)

curPath = os.path.abspath(os.path.dirname(__file__))
config_path = curPath
with open(config_path + '/config.json', 'r', encoding='utf8')as fp:
    conf = json.load(fp)


# 子进程要执行的代码
def run_proc(conf, df_stock_code, ktype):
    SA = StockApi(conf)
    SA.update_stock_csv(df_stock_code, ktype=ktype)


if __name__=='__main__':
    print('Parent process %s.' % os.getpid())
    SA = StockApi(conf)
    # df_stock_code = ['sh', 'sz', 'cyb']
    # for i in ['60', 'D']:
    #     SA.update_stock_csv(df_stock_code, ktype=i, pro=False)

    # =======================================
    # df_stock_code = SA.pro.stock_basic(exchange='', list_status='L',
    #                                      fields='ts_code,symbol,name,area,industry,list_date')
    # df_stock_code.to_csv()
    df_stock_code = pd.read_csv(SA.data_dir + '/code_list.csv')
    df_stock_code = list(df_stock_code['ts_code'])

    # df_stock_code = df_stock_code[:100]
    # df_stock_code = ['000001.SZ']

    worker = 3
    worker_list = []
    # 分配工作
    df_stock_code_worker = []
    t = len(df_stock_code) // worker
    for i in range(worker):
        if i + 1 == worker:
            df_stock_code_worker.append(df_stock_code[i * t:])
        else:
            df_stock_code_worker.append(df_stock_code[i * t:(i + 1) * t])

    for k in ['D']:
        p = Pool(worker)
        for i in range(worker):
            p.apply_async(run_proc, args=(conf, df_stock_code_worker[i], k,))
        print('Waiting for all subprocesses done...')
        p.close()
        p.join()
        print('All subprocesses done.')