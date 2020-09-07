from django.shortcuts import render
from django.http import HttpResponse
import json
import os
# from .stock_code.core.StockApi import StockApi
from .stock_tools.StockApi import StockApi
from .stock_tools.PyEchart import StockPyEchart

from stock.models import StockData
import pandas as pd
from django.db import connection
from django.db.models import Avg,Min,Sum,Max
import traceback  # 定位异常

from pyecharts import options as opts
from pyecharts.commons.utils import JsCode
from pyecharts.charts import Kline, Line, Bar, Grid
# Create your views here.


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
                diff_df = df   # 若数据库没数据，则diff_df的不同数据为所有df数据
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
    def kline_chart():
        all_data = StockData.objects.values('symbol').annotate(Sum('volume'))
        x = []
        y = []
        for i in all_data:
            x.append(i['symbol'])
            y.append(i['volume__sum'])
        c = (
            Bar(
            )
                .add_xaxis(x, )
                .add_yaxis("id", y)
                .set_global_opts(
                title_opts=opts.TitleOpts(title="Bar-基本示例", subtitle="我是副标题"),
                toolbox_opts=opts.ToolboxOpts(),
                legend_opts=opts.LegendOpts(is_show=False),
            )
        )
        return c

    chart = kline_chart()
    options = chart.dump_options_with_quotes()
    data = json.dumps(options, ensure_ascii=False)
    return HttpResponse(data, content_type="application/json,charset=utf-8")


def kline(request):
    return render(request, 'kline.html')