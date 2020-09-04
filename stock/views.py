from django.shortcuts import render
from django.http import HttpResponse
import json
import os
from .stock_code.core.StockApi import StockApi
from stock.models import StockData
import numpy as np
import pandas as pd
# Create your views here.

curPath = os.path.abspath(os.path.dirname(__file__))
config_path = curPath

with open(config_path + '/stock_code/config.json', 'r', encoding='utf8')as fp:
    conf = json.load(fp)

def api(request):
    result = {
        "status": 200
    }
    data = json.dumps(result, ensure_ascii=False)
    return HttpResponse(data, content_type="application/json,charset=utf-8")


def v1_update(request):
    '''根据'''
    vt_symbol = request.GET.get('vt_symbol')
    interval = request.GET.get('interval')
    msg = ""
    status = ""
    if vt_symbol and interval:
        df_stock_code = [vt_symbol]
        SA = StockApi(conf)
        df = SA.update_stock_csv(df_stock_code, ktype=interval)
        df = df.sort_index()  # 要正序添加到数据库
        df = df.dropna(axis=0, how='any', subset=["open"])
        df = df[:10]

        # FIXME index 转成UTC时间格式
        # https://www.cnblogs.com/Cheryol/p/13479418.html
        # print(df.index)
        # print(pd.DataFrame(df.index))
        # dt = dt.datetime.astimezone("UTC")
        # dt = dt.replace(tzinfo=None)
        # dt = dt.strftime('%Y-%m-%d %H:%M:%S')
        # print(dt)
        symbol, exchange = vt_symbol.split('.')

        for production_data, row in df.iterrows():
            sd = StockData()
            if interval == 'D':
                production_data = production_data + " 00:00:00"
            sd.production_data = production_data
            sd.symbol = symbol
            sd.exchange = exchange
            sd.interval = interval
            sd.volume = row['volume']
            sd.open_interest = 0
            sd.open_price = row['open']
            sd.high_price = row['high']
            sd.low_price = row['low']
            sd.close_price = row['close']
            # sd.save()

        if df is not None:
            status = 200
        else:
            status = 'error'
            msg = "ts接口没获取到：" + vt_symbol
    else:
        status = 'error'
    result = {
        "status": status,
        "vt_symbol": vt_symbol,
        "interval": interval,
        "msg": msg
    }
    data = json.dumps(result, ensure_ascii=False)
    return HttpResponse(data, content_type="application/json,charset=utf-8")