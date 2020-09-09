from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
import json
import os
# from .stock_code.core.StockApi import StockApi
from .stock_tools.StockApi import StockApi
from .stock_tools.PyEchart import StockPyEchart

from stock.models import StockData
import pandas as pd
from django.db import connection
from django.db.models import Avg, Min, Sum, Max
import traceback  # 定位异常

from pyecharts import options as opts
from pyecharts.commons.utils import JsCode
from pyecharts.charts import Kline, Line, Bar, Grid

# Create your views here.
pd.set_option('display.width', 300)
pd.set_option('display.max_columns', 300)
pd.set_option('display.max_colwidth', 300)
pd.set_option('display.max_row', 1000)

curPath = os.path.abspath(os.path.dirname(__file__))
config_path = curPath

with open(config_path + '/stock_tools/config.json', 'r', encoding='utf8')as fp:
    conf = json.load(fp)


def v1_update(request):
    '''增量更新'''
    vt_symbol = request.GET.get('vt_symbol')
    interval = request.GET.get('interval')
    status = "error"
    msg = ""
    result = {
        "status": status,
        "vt_symbol": vt_symbol,
        "interval": interval,
        "msg": msg,
    }

    if vt_symbol and interval:
        df_stock_code = [vt_symbol]
        symbol, exchange = vt_symbol.split('.')

        try:
            SA = StockApi(conf)
            df = SA.update_stock_csv(df_stock_code, ktype=interval)
            df = df.sort_index()  # 要正序添加到数据库
            df = df.dropna(axis=0, how='any', subset=["open_price"])  # 去掉空数据
            # 2000-01-01 变成utc:2020-01-01 00:00:00+00:00
            df['datetime'] = pd.to_datetime(df.index, utc=True, format="%Y-%m-%d")
            df['exchange'] = exchange
            df['interval'] = interval
            df['open_interest'] = 0
            df = df[['symbol', 'exchange', 'datetime', 'interval', 'volume',
                     'open_interest', 'open_price', 'high_price', 'low_price', 'close_price']]

            # 建立数据库连接
            connection.connect()
            conn = connection.connection
            # import sqlite3
            # 连接到SQlite数据库
            # conn = sqlite3.connect('db.sqlite3')
            # 从数据库获取对应的数据用于对比
            old_stock_data = StockData.objects.filter(symbol=symbol, exchange=exchange, interval=interval)
            d = pd.DataFrame(old_stock_data.values())
            if len(d):
                diff_df = df[~df['datetime'].isin(d['datetime'])]  # 查出数据库中没有的时间
            else:
                diff_df = df  # 若数据库没数据，则diff_df的不同数据为所有df数据
            # 存入数据库
            diff_df.to_sql(StockData._meta.db_table, conn, if_exists='append', index=False)
            status = 200
            msg = f'新增{len(diff_df)}条数据'
        except Exception as e:
            status = 'error'
            msg = f"{traceback.format_exc()}"
    result['status'] = status
    result['msg'] = msg

    data = json.dumps(result, ensure_ascii=False)
    return HttpResponse(data, content_type="application/json,charset=utf-8")


def v1_get_kline_chart(request):

    vt_symbol = request.GET.get('vt_symbol')
    interval = request.GET.get('interval')
    symbol, exchange = vt_symbol.split('.')

    def kline_chart(symbol, exchange, interval):
        old_stock_data = StockData.objects.filter(symbol=symbol, exchange=exchange, interval=interval).order_by(
            'datetime')
        df = pd.DataFrame(old_stock_data.values())
        df = df[:50]
        # 根据不同周期不同格式化
        if interval == "D":
            f = '%Y-%m-%d'
        elif interval == "60":
            f = '%Y-%m-%d %H:%M'
            # df['datetime'] = df.index
        df = df.set_index("datetime")
        df.index = df.index.strftime(f)
        SPY = StockPyEchart(conf)
        chart = SPY.draw_charts(df)

        return chart

    chart = kline_chart(symbol, exchange, interval)
    html = chart.render()
    with open(html, 'r') as f:
        h = f.read()
    # options = chart.dump_options_with_quotes()  # 这个js代码无效，即没办法分配颜色，先用html的方法实现
    data = json.dumps(h, ensure_ascii=False)
    return HttpResponse(data, content_type="application/json,charset=utf-8")


def kline(request):
    ctx = {}
    if request.POST:
        vt_symbol = request.POST.get('vt_symbol')
        interval = request.POST.get('interval')
        symbol, exchange = vt_symbol.split('.')
        interval = 'D'

        def kline_chart(symbol, exchange, interval):
            old_stock_data = StockData.objects.filter(symbol=symbol, exchange=exchange, interval=interval).order_by(
                'datetime')
            df = pd.DataFrame(old_stock_data.values())

            # 根据不同周期不同格式化
            if interval == "D":
                f = '%Y-%m-%d'
            elif interval == "60":
                f = '%Y-%m-%d %H:%M'
                # df['datetime'] = df.index
            df = df.set_index("datetime")
            df.index = df.index.strftime(f)
            SPY = StockPyEchart(conf)
            chart = SPY.draw_charts(df)
            return chart

        chart = kline_chart(symbol, exchange, interval)
        html = chart.render()
        with open(html, 'r') as f:
            h = f.read()
        # options = chart.dump_options_with_quotes()  # 这个js代码无效，即没办法分配颜色，先用html的方法实现
        data = json.dumps(h, ensure_ascii=False)

        if request.POST:
            ctx['rlt'] = h
    return render(request, "kline.html", ctx)


def v1_all_update(request):
    '''增量更新所有数据'''
    s = int(request.GET.get('s'))
    e = int(request.GET.get('e'))

    status = "error"
    msg = ""
    result = {
        "status": status,
        "msg": msg,
    }
    connection.connect()
    conn = connection.connection
    SA = StockApi(conf)
    all_df_stock_code = SA.pro.stock_basic(exchange='', list_status='L',
                                         fields='ts_code,symbol,name,area,industry,list_date')
    all_df_stock_code = list(all_df_stock_code['ts_code'])
    all_df_stock_code = all_df_stock_code[s:e]
    interval = 'D'
    for df_stock_code in all_df_stock_code:
        symbol, exchange = df_stock_code.split('.')
        df = SA.update_stock_csv([df_stock_code], ktype=interval)
        if df is not None and not df.empty:
            df = df.sort_index()  # 要正序添加到数据库
            df = df.dropna(axis=0, how='any', subset=["open_price"])  # 去掉空数据
            # 2000-01-01 变成utc:2020-01-01 00:00:00+00:00
            df['datetime'] = pd.to_datetime(df.index, utc=True, format="%Y-%m-%d")
            df['exchange'] = exchange
            df['interval'] = interval
            df['open_interest'] = 0
            df = df[['symbol', 'exchange', 'datetime', 'interval', 'volume',
                     'open_interest', 'open_price', 'high_price', 'low_price', 'close_price']]

            old_stock_data = StockData.objects.filter(symbol=symbol, exchange=exchange, interval=interval)
            d = pd.DataFrame(old_stock_data.values())
            if len(d):
                diff_df = df[~df['datetime'].isin(d['datetime'])]  # 查出数据库中没有的时间
            else:
                diff_df = df  # 若数据库没数据，则diff_df的不同数据为所有df数据
            # 存入数据库
            diff_df.to_sql(StockData._meta.db_table, conn, if_exists='append', index=False)

        # =========================================================================================================
        task_rate = round(((all_df_stock_code.index(df_stock_code) + 1) / len(all_df_stock_code)) * 100, 2)
        print(f'\r all update task: {task_rate}%', end='', flush=True)

    status = 200
    msg = f'新增{len(all_df_stock_code)}条数据'

    result['status'] = status
    result['msg'] = msg

    data = json.dumps(result, ensure_ascii=False)
    return HttpResponse(data, content_type="application/json,charset=utf-8")
