import tushare as ts
import pandas as pd
import json
import time

import sys, os

curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]  # 这里的rootpath是你的工程根目录
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






