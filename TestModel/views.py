from django.shortcuts import render
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode
from pyecharts.charts import Kline, Line, Bar, Grid
from django.http import HttpResponse
import pandas as pd
from TestModel.models import TestData
# Create your views here.
from django.db.models import Avg,Min,Sum,Max

import json


def index(request):
    context = {}
    context['hello'] = 'Hello TEST!'
    return render(request, 'index.html', context)


def testdata(request):
    context = {}
    context['hello'] = 'Hello World!'
    return render(request, 'testdata.html', context)


def bar_base() -> Bar:
    all_data = TestData.objects.values('producers').annotate(Sum('speed'))
    x = []
    y = []
    for i in all_data:
        x.append(i['producers'][:7])
        y.append(i['speed__sum'])
    c = (
        Bar(
        )
            .add_xaxis(x,)
            .add_yaxis("id", y)
            .set_global_opts(
            title_opts=opts.TitleOpts(title="Bar-基本示例", subtitle="我是副标题"),
            toolbox_opts=opts.ToolboxOpts(),
            legend_opts=opts.LegendOpts(is_show=False),

        )
    )
    return c


def get_bar_chart(request):

    c = bar_base()
    result = c.dump_options_with_quotes()
    data = json.dumps(result, ensure_ascii=False)
    return HttpResponse(data, content_type="application/json,charset=utf-8")


def test(request):
    result = {"status": "错误", "data": "", "city": "北京"}
    # json返回为中文


# 数据库操作
def testdb(request):
    df = pd.read_csv('testdata.csv', dtype={'代号': str, '设备编码': str,})
    for i, row in df.iterrows():
        # data = {
        #     'name': row['设备名称'],
        #     'procurement_data': row['采购日期'],
        #     'production_data': row['生产日期'],
        #     'code': row['设备编码'],
        #     'department': row['单位'],
        #     'producers': row['生产商'],
        #     'speed': row['速度'],
        # }
        td = TestData()
        td.name = row['设备名称']
        # td.procurement_data = row['采购日期']
        # td.production_data = row['生产日期']
        td.code = row['设备编码']
        td.department = row['单位']
        td.producers = row['生产商']
        td.speed = row['速度']
        td.save()
    return HttpResponse("<p>数据添加成功！</p>")
