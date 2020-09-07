
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode
from pyecharts.charts import Kline, Line, Bar, Grid

import pandas as pd

from StockEigenvalueExtraction import StockEigenvalueExtraction


class StockPyEchart(object):
    def __init__(self, config_dict):
        self.config = config_dict
        self.options = config_dict['options']
        self.data_dir = config_dict['options']['data_dir']
        self.stock_csv_columns_dict = config_dict['options']['stock_csv_columns_dict']
        self.SEE = StockEigenvalueExtraction()

    def grid_chart(self):
        """
        组合图
        """
        grid_chart = Grid(
            init_opts=opts.InitOpts(
                width="1000px",
                height="800px",
                animation_opts=opts.AnimationOpts(animation=False),
            )
        )
        return grid_chart

    def kline(self, echarts_data, title, range_start, range_end):
        kline_data = echarts_data["data"]
        date = echarts_data["date"]
        kline = (
            Kline()
                .add_xaxis(xaxis_data=date)
                .add_yaxis(
                series_name="Dow-Jones index",
                y_axis=kline_data,
                itemstyle_opts=opts.ItemStyleOpts(color="#ec0000", color0="#00da3c"),
            )
                .set_global_opts(
                legend_opts=opts.LegendOpts(
                    is_show=False, pos_bottom=10, pos_left="center"
                ),

                # 其中inside是支持鼠标缩放
                datazoom_opts=[
                    opts.DataZoomOpts(
                        is_show=True,
                        type_="inside",
                        xaxis_index=[0, 1, 2, 3, 4],
                        range_start=range_start,
                        range_end=range_end,
                    ),
                    opts.DataZoomOpts(
                        is_show=True,
                        xaxis_index=[0, 1, 2, 3, 4],
                        type_="slider",
                        range_start=range_start,
                        range_end=range_end,
                    ),
                ],
                # # 不知道为什么要分开三个写，可能是想通过xaxis_index分别配置
                # datazoom_opts=[
                #     opts.DataZoomOpts(
                #         is_show=False, type_="inside", xaxis_index=[0, 0], range_end=100
                #     ),
                #     opts.DataZoomOpts(
                #         is_show=True, xaxis_index=[0, 1], pos_top="97%", range_end=100
                #     ),
                #     opts.DataZoomOpts(is_show=False, xaxis_index=[0, 2], range_end=100),
                # ],

                yaxis_opts=opts.AxisOpts(
                    is_scale=True,
                    splitarea_opts=opts.SplitAreaOpts(
                        is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
                    ),
                ),

                title_opts=opts.TitleOpts(title=title, subtitle="日K线"),
                tooltip_opts=opts.TooltipOpts(
                    trigger="axis",
                    axis_pointer_type="cross",
                    background_color="rgba(245, 245, 245, 0.8)",
                    border_width=1,
                    border_color="#ccc",
                    textstyle_opts=opts.TextStyleOpts(color="#000"),
                ),
                visualmap_opts=opts.VisualMapOpts(
                    is_show=False,
                    dimension=2,
                    series_index=5,
                    is_piecewise=True,
                    pieces=[
                        {"value": 1, "color": "#00da3c"},
                        {"value": -1, "color": "#ec0000"},
                    ],
                ),
                # 所有图的axis 连在一块
                axispointer_opts=opts.AxisPointerOpts(
                    is_show=True,
                    link=[{"xAxisIndex": "all"}],
                    label=opts.LabelOpts(background_color="#777"),
                ),
                brush_opts=opts.BrushOpts(
                    x_axis_index="all",
                    brush_link="all",
                    out_of_brush={"colorAlpha": 0.1},
                    brush_type="lineX",
                ),
            )
        )

        line = (
            Line()
                .add_xaxis(xaxis_data=date)
                .add_yaxis(
                series_name="MA5",
                y_axis=echarts_data['ma5'],
                is_smooth=True,
                is_hover_animation=False,
                linestyle_opts=opts.LineStyleOpts(width=3, opacity=0.5),
                label_opts=opts.LabelOpts(is_show=False),
                is_symbol_show=False,  # 去掉折线上的小圆点
            )
                .add_yaxis(
                series_name="MA30",
                y_axis=echarts_data['ma30'],
                is_smooth=True,
                is_hover_animation=False,
                linestyle_opts=opts.LineStyleOpts(width=3, opacity=0.5),
                label_opts=opts.LabelOpts(is_show=False),
                is_symbol_show=False,  # 去掉折线上的小圆点
            )
                .set_global_opts(xaxis_opts=opts.AxisOpts(type_="category"))
        )

        # Kline And Line
        overlap_kline_line = kline.overlap(line)
        return overlap_kline_line

    def volume(self, echarts_data):
        bar = (
            Bar()
                .add_xaxis(xaxis_data=echarts_data['date'])
                .add_yaxis(
                series_name="Volume",
                y_axis=echarts_data['volume'],
                xaxis_index=1,
                yaxis_index=1,
                label_opts=opts.LabelOpts(is_show=False),
                #
                # # 变色
                itemstyle_opts=opts.ItemStyleOpts(
                    color=JsCode(
                        """
                    function(params) {
                        var colorList;
                        if (barData[params.dataIndex][1] > barData[params.dataIndex][0]) {
                            colorList = '#ef232a';
                        } else {
                            colorList = '#14b143';
                        }
                        return colorList;
                    }
                    """
                    )
                ),

            )
                .set_global_opts(
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    is_scale=True,
                    grid_index=1,
                    boundary_gap=False,
                    axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                    axistick_opts=opts.AxisTickOpts(is_show=False),
                    splitline_opts=opts.SplitLineOpts(is_show=False),
                    axislabel_opts=opts.LabelOpts(is_show=False),
                    split_number=20,
                    min_="dataMin",
                    max_="dataMax",
                ),
                yaxis_opts=opts.AxisOpts(
                    grid_index=1,
                    is_scale=True,
                    split_number=2,
                    axislabel_opts=opts.LabelOpts(is_show=False),
                    axisline_opts=opts.AxisLineOpts(is_show=False),
                    axistick_opts=opts.AxisTickOpts(is_show=False),
                    splitline_opts=opts.SplitLineOpts(is_show=False),
                ),
                legend_opts=opts.LegendOpts(is_show=False),
                title_opts=opts.TitleOpts(title="volume", pos_top="85%"),  # 标题
            )
        )
        return bar

    def macd(self, echarts_data):
        # Bar-2 (Overlap Bar + Line)
        bar = (
            Bar()
                .add_xaxis(xaxis_data=echarts_data['date'])
                .add_yaxis(
                series_name="MACD",
                y_axis=echarts_data['macd'],
                xaxis_index=2,
                yaxis_index=2,
                label_opts=opts.LabelOpts(is_show=False),
                itemstyle_opts=opts.ItemStyleOpts(
                    color=JsCode(
                        """
                            function(params) {
                                var colorList;
                                if (params.data >= 0) {
                                  colorList = '#ef232a';
                                } else {
                                  colorList = '#14b143';
                                }
                                return colorList;
                            }
                            """
                    )
                ),
            )
                .set_global_opts(
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    grid_index=2,
                    axislabel_opts=opts.LabelOpts(is_show=False),

                    # axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                    axistick_opts=opts.AxisTickOpts(is_show=False),  # 不显示刻度
                    # splitline_opts=opts.SplitLineOpts(is_show=False),   # 不显示刻度
                    # axislabel_opts=opts.LabelOpts(is_show=False),
                    # split_number=20,
                ),
                yaxis_opts=opts.AxisOpts(
                    grid_index=2,
                    split_number=4,
                    axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                    axistick_opts=opts.AxisTickOpts(is_show=False),
                    splitline_opts=opts.SplitLineOpts(is_show=False),
                    axislabel_opts=opts.LabelOpts(is_show=True),
                ),
                legend_opts=opts.LegendOpts(is_show=False),
                title_opts=opts.TitleOpts(subtitle="MACD", pos_top="72%"),
                # legend_opts=opts.LegendOpts(pos_top="68%"),
            )
        )

        macd_line = (
            Line()
                .add_xaxis(xaxis_data=echarts_data['date'])
                .add_yaxis(
                series_name="DIFF",
                y_axis=echarts_data['macd_diff'],
                # xaxis_index=2,
                # yaxis_index=2,
                is_symbol_show=False,  # 去掉折线上的小圆点
                label_opts=opts.LabelOpts(is_show=False),
            )
                .add_yaxis(
                series_name="DEA",
                y_axis=echarts_data["macd_dea"],
                # xaxis_index=2,
                # yaxis_index=2,
                is_symbol_show=False,  # 去掉折线上的小圆点
                label_opts=opts.LabelOpts(is_show=False),
            )
            # .set_global_opts(legend_opts=opts.LegendOpts(is_show=False))
            # .set_global_opts(xaxis_opts=opts.AxisOpts(type_="category"))
        )
        # MACD BAR And MACD Line
        bar_macd_line = bar.overlap(macd_line)
        return bar_macd_line

    def kdj(self, echarts_data):
        # KDJ
        kdj_line = (
            Line()
                .add_xaxis(xaxis_data=echarts_data['date'])
                .add_yaxis(
                series_name="K",
                y_axis=echarts_data['kdj_k'],
                is_symbol_show=False,  # 去掉折线上的小圆点
                label_opts=opts.LabelOpts(is_show=False),
            )
                .add_yaxis(
                series_name="D",
                y_axis=echarts_data["kdj_d"],
                is_symbol_show=False,  # 去掉折线上的小圆点
                label_opts=opts.LabelOpts(is_show=False),
            )
                .add_yaxis(
                series_name="J",
                y_axis=echarts_data["kdj_j"],
                is_symbol_show=False,  # 去掉折线上的小圆点
                label_opts=opts.LabelOpts(is_show=False),
                # markline_opts=opts.MarkLineOpts(
                #     data=[100]
                # ),
            )
                .set_global_opts(
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    grid_index=2,
                    axislabel_opts=opts.LabelOpts(is_show=False),

                    # axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                    axistick_opts=opts.AxisTickOpts(is_show=False),  # 不显示刻度
                    # splitline_opts=opts.SplitLineOpts(is_show=False),   # 不显示刻度
                    # axislabel_opts=opts.LabelOpts(is_show=False),
                    # split_number=20,
                ),
                # title_opts=opts.TitleOpts(subtitle="KDJ"),
                title_opts=opts.TitleOpts(subtitle="KDJ", pos_top="62%"),    # 标题
                legend_opts=opts.LegendOpts(pos_top="58%"),  # 图例位置
            )
        )
        return kdj_line

    def kdj_macd(self, echarts_data, ktype='sum'):
        """
        用kdj的j做成macd趋势图，可以平滑伪金叉
        """
        macd_kdj_bar = (
            Bar()
                .add_xaxis(xaxis_data=echarts_data['date'])
                .add_yaxis(
                series_name="MACD_KDJ",
                y_axis=echarts_data['kdj_macd_%s' % ktype],
                xaxis_index=2,
                yaxis_index=2,
                label_opts=opts.LabelOpts(is_show=False),
                itemstyle_opts=opts.ItemStyleOpts(
                    color=JsCode(
                        """
                            function(params) {
                                var colorList;
                                if (params.data >= 0) {
                                  colorList = '#ef232a';
                                } else {
                                  colorList = '#14b143';
                                }
                                return colorList;
                            }
                            """
                    )
                ),
            )
                .set_global_opts(
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    grid_index=2,
                    axislabel_opts=opts.LabelOpts(is_show=False),

                    # axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                    axistick_opts=opts.AxisTickOpts(is_show=False),  # 不显示刻度
                    # splitline_opts=opts.SplitLineOpts(is_show=False),   # 不显示刻度
                    # axislabel_opts=opts.LabelOpts(is_show=False),
                    # split_number=20,
                ),
                yaxis_opts=opts.AxisOpts(
                    grid_index=2,
                    split_number=4,
                    axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                    axistick_opts=opts.AxisTickOpts(is_show=False),
                    splitline_opts=opts.SplitLineOpts(is_show=False),
                    axislabel_opts=opts.LabelOpts(is_show=True),
                ),
                legend_opts=opts.LegendOpts(is_show=False),
                # title_opts=opts.TitleOpts(subtitle="KDJ_MACD"),
                title_opts=opts.TitleOpts(subtitle="KDJ_M_%s" % ktype, pos_top="52%"),  # 标题
                # legend_opts=opts.LegendOpts(pos_top="45%"),  # 图例位置
            )
        )

        macd_kdj_line = (
            Line()
                .add_xaxis(xaxis_data=echarts_data['date'])
                .add_yaxis(
                series_name="KDJ_DIFF",
                y_axis=echarts_data['kdj_macd_diff_%s' % ktype],
                # xaxis_index=2,
                # yaxis_index=2,
                is_symbol_show=False,  # 去掉折线上的小圆点
                label_opts=opts.LabelOpts(is_show=False),
            )
                .add_yaxis(
                series_name="KDJ_DEA",
                y_axis=echarts_data["kdj_macd_dea_%s" % ktype],
                # xaxis_index=2,
                # yaxis_index=2,
                is_symbol_show=False,  # 去掉折线上的小圆点
                label_opts=opts.LabelOpts(is_show=False),
            )
            # .set_global_opts(legend_opts=opts.LegendOpts(is_show=False))
            # .set_global_opts(xaxis_opts=opts.AxisOpts(type_="category"))
        )
        # MACD BAR And MACD Line
        bar_macd_kdj_line = macd_kdj_bar.overlap(macd_kdj_line)

        return bar_macd_kdj_line

    def p_kdj_macd(self, echarts_data, ktype='sum'):
        """
        p_kdj_macd的百分比图
        """
        bar = (
            Bar()
                .add_xaxis(xaxis_data=echarts_data['date'])
                .add_yaxis(
                series_name="P_MACD_KDJ",
                y_axis=echarts_data['p_kdj_macd_%s' % ktype],
                xaxis_index=2,
                yaxis_index=2,
                label_opts=opts.LabelOpts(is_show=False),
                itemstyle_opts=opts.ItemStyleOpts(
                    color=JsCode(
                        """
                            function(params) {
                                var colorList;
                                if (params.data >= 0) {
                                  colorList = '#ef232a';
                                } else {
                                  colorList = '#14b143';
                                }
                                return colorList;
                            }
                            """
                    )
                ),
            )
                .set_global_opts(
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    grid_index=2,
                    axislabel_opts=opts.LabelOpts(is_show=False),

                    # axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                    axistick_opts=opts.AxisTickOpts(is_show=False),  # 不显示刻度
                    # splitline_opts=opts.SplitLineOpts(is_show=False),   # 不显示刻度
                    # axislabel_opts=opts.LabelOpts(is_show=False),
                    # split_number=20,
                ),
                yaxis_opts=opts.AxisOpts(
                    grid_index=2,
                    split_number=4,
                    axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                    axistick_opts=opts.AxisTickOpts(is_show=False),
                    splitline_opts=opts.SplitLineOpts(is_show=False),
                    axislabel_opts=opts.LabelOpts(is_show=True),
                ),
                legend_opts=opts.LegendOpts(is_show=False),
                # title_opts=opts.TitleOpts(subtitle="KDJ_MACD"),
                title_opts=opts.TitleOpts(subtitle="P_KDJ_M_%s" % ktype, pos_top="52%"),  # 标题
                # legend_opts=opts.LegendOpts(pos_top="45%"),  # 图例位置
            )
        )

        return bar

    def obv(self, echarts_data):
        line = (
            Line()
                .add_xaxis(xaxis_data=echarts_data['date'])
                .add_yaxis(
                series_name="obv",
                y_axis=echarts_data['obv'],
                is_smooth=True,
                is_hover_animation=False,
                label_opts=opts.LabelOpts(is_show=False),
                is_symbol_show=False,  # 去掉折线上的小圆点
            )
                .set_global_opts(
                yaxis_opts=opts.AxisOpts(
                    min_='dataMin'
                ),
                legend_opts=opts.LegendOpts(is_show=False),
                title_opts=opts.TitleOpts(subtitle="obv", pos_top="80%"),  # 标题
                # legend_opts=opts.LegendOpts(pos_top="78%"),  # 图例位置
            )

        )
        return line

    def draw_kline_v1(self, df, filename):
        """
        2020.08.25
        最原始的版本，多了一个kdj的macd
        Kline + kdj_macd +kdj + macd + vol
        """
        df = df.sort_index()  # 要正序才能计算KDJ
        df = df.dropna(axis=0, how='any', subset=["close",])
        df = self.SEE.kdj(df)
        df = self.SEE.kdj_macd(df)
        df = self.SEE.macd(df)
        df = self.SEE.obv(df)
        df = self.SEE.ma(df, 30)

        data = []
        for i, row in df.iterrows():
            data.append([row['open'], row['close'], row['low'], row['high']])
        echarts_data = {
            'data': data,
            'date': list(df.index),
            'volume': list(df['volume']),
            'ma5': list(df['ma5']),
            'ma20': list(df['ma20']),
            'ma30': list(df['ma30']),
            'macd': list(df['macd']),
            'kdj_k': list(df['kdj_k']),
            'kdj_d': list(df['kdj_d']),
            'kdj_j': list(df['kdj_j']),
            'macd_diff': list(df['macd_diff']),
            'macd_dea': list(df['macd_dea']),
            'kdj_macd_d': list(df['kdj_macd_d']),
            'kdj_macd_diff_d': list(df['kdj_macd_diff_d']),
            'kdj_macd_dea_d': list(df['kdj_macd_dea_d']),
            'obv': list(df['obv']),
        }

        # 动态设置只显示30天
        n = 60 / len(df)
        range_start = 0
        if n >= 1:
            range_start = 0
        elif n < 1:
            range_start = (1 - n)*100
        range_end = 100
        kline = self.kline(echarts_data, filename, range_start, range_end)
        volume = self.volume(echarts_data)
        macd = self.macd(echarts_data)
        kdj = self.kdj(echarts_data)
        kdj_macd = self.kdj_macd(echarts_data, ktype='d')

        # Grid Overlap + Bar
        grid_chart = self.grid_chart()

        # 这个是为了把 data.datas 这个数据写入到 html 中,还没想到怎么跨 series 传值
        # demo 中的代码也是用全局变量传的
        # 配合macd中的js代码变色
        grid_chart.add_js_funcs("var barData = {}".format(echarts_data['data']))

        grid_chart.add(
            kline,
            grid_opts=opts.GridOpts(pos_left="10%", pos_right="8%", height="40%"),
        )


        # 加上KDJ的MACD
        grid_chart.add(
            kdj_macd,
            grid_opts=opts.GridOpts(
                pos_left="10%", pos_right="8%", pos_top="50%", height="10%",
            ),
        )

        # 加上KDJ
        grid_chart.add(
            kdj,
            grid_opts=opts.GridOpts(
                pos_left="10%", pos_right="8%", pos_top="60%", height="10%",
            ),
        )

        # 加上MACD
        grid_chart.add(
            macd,
            grid_opts=opts.GridOpts(
                pos_left="10%", pos_right="8%", pos_top="70%", height="10%",
            ),
        )

        grid_chart.add(
            volume,
            grid_opts=opts.GridOpts(
                pos_left="10%", pos_right="8%", pos_top="80%", height="10%"
            ),

        )


        filepath = self.data_dir + '/pyechart/%s.html' % filename
        grid_chart.render(filepath)

    def draw_charts(self, df, filename=None):
        if not filename:
            filename = df[self.stock_csv_columns_dict['股票代码']].values[0]
        self.draw_kline_v1(df, filename)

class StockPyEchart_2(object):
    def __init__(self, config_dict):
        self.config = config_dict
        self.options = config_dict['options']
        self.data_dir = config_dict['options']['data_dir']
        self.stock_csv_columns_dict = config_dict['options']['stock_csv_columns_dict']
        self.SEE = StockEigenvalueExtraction()

    def grid_chart(self):
        """
        组合图
        """
        grid_chart = Grid(
            init_opts=opts.InitOpts(
                width="1000px",
                height="800px",
                animation_opts=opts.AnimationOpts(animation=False),
            )
        )
        return grid_chart

    def kline(self, echarts_data, title, range_start, range_end):
        kline_data = echarts_data["data"]
        date = echarts_data["date"]
        kline = (
            Kline()
                .add_xaxis(xaxis_data=date)
                .add_yaxis(
                series_name="Dow-Jones index",
                y_axis=kline_data,
                itemstyle_opts=opts.ItemStyleOpts(color="#ec0000", color0="#00da3c"),
            )
                .set_global_opts(
                legend_opts=opts.LegendOpts(
                    is_show=False, pos_bottom=10, pos_left="center"
                ),

                # 其中inside是支持鼠标缩放
                datazoom_opts=[
                    opts.DataZoomOpts(
                        is_show=True,
                        type_="inside",
                        xaxis_index=[0, 1, 2, 3, 4,5,6,7],
                        range_start=range_start,
                        range_end=range_end,
                    ),
                    opts.DataZoomOpts(
                        is_show=True,
                        xaxis_index=[0, 1, 2, 3, 4,5,6,7],
                        type_="slider",
                        range_start=range_start,
                        range_end=range_end,
                    ),
                ],
                # # 不知道为什么要分开三个写，可能是想通过xaxis_index分别配置
                # datazoom_opts=[
                #     opts.DataZoomOpts(
                #         is_show=False, type_="inside", xaxis_index=[0, 0], range_end=100
                #     ),
                #     opts.DataZoomOpts(
                #         is_show=True, xaxis_index=[0, 1], pos_top="97%", range_end=100
                #     ),
                #     opts.DataZoomOpts(is_show=False, xaxis_index=[0, 2], range_end=100),
                # ],

                yaxis_opts=opts.AxisOpts(
                    is_scale=True,
                    splitarea_opts=opts.SplitAreaOpts(
                        is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
                    ),
                ),

                title_opts=opts.TitleOpts(title=title, subtitle="日K线"),
                tooltip_opts=opts.TooltipOpts(
                    trigger="axis",
                    axis_pointer_type="cross",
                    background_color="rgba(245, 245, 245, 0.8)",
                    border_width=1,
                    border_color="#ccc",
                    textstyle_opts=opts.TextStyleOpts(color="#000"),
                ),
                visualmap_opts=opts.VisualMapOpts(
                    is_show=False,
                    dimension=2,
                    series_index=5,
                    is_piecewise=True,
                    pieces=[
                        {"value": 1, "color": "#00da3c"},
                        {"value": -1, "color": "#ec0000"},
                    ],
                ),
                # 所有图的axis 连在一块
                axispointer_opts=opts.AxisPointerOpts(
                    is_show=True,
                    link=[{"xAxisIndex": "all"}],
                    label=opts.LabelOpts(background_color="#777"),
                ),
                brush_opts=opts.BrushOpts(
                    x_axis_index="all",
                    brush_link="all",
                    out_of_brush={"colorAlpha": 0.1},
                    brush_type="lineX",
                ),
            )
        )

        line = (
            Line()
                .add_xaxis(xaxis_data=date)
                .add_yaxis(
                series_name="MA5",
                y_axis=echarts_data['ma5'],
                is_smooth=True,
                is_hover_animation=False,
                linestyle_opts=opts.LineStyleOpts(width=3, opacity=0.5),
                label_opts=opts.LabelOpts(is_show=False),
                is_symbol_show=False,  # 去掉折线上的小圆点
            )
                .add_yaxis(
                series_name="MA30",
                y_axis=echarts_data['ma30'],
                is_smooth=True,
                is_hover_animation=False,
                linestyle_opts=opts.LineStyleOpts(width=3, opacity=0.5),
                label_opts=opts.LabelOpts(is_show=False),
                is_symbol_show=False,  # 去掉折线上的小圆点
            )
                .set_global_opts(xaxis_opts=opts.AxisOpts(type_="category"))
        )

        # Kline And Line
        overlap_kline_line = kline.overlap(line)
        return overlap_kline_line

    def volume(self, echarts_data):
        bar = (
            Bar()
                .add_xaxis(xaxis_data=echarts_data['date'])
                .add_yaxis(
                series_name="Volume",
                y_axis=echarts_data['volume'],
                xaxis_index=1,
                yaxis_index=1,
                label_opts=opts.LabelOpts(is_show=False),
                #
                # # 变色
                itemstyle_opts=opts.ItemStyleOpts(
                    color=JsCode(
                        """
                    function(params) {
                        var colorList;
                        if (barData[params.dataIndex][1] > barData[params.dataIndex][0]) {
                            colorList = '#ef232a';
                        } else {
                            colorList = '#14b143';
                        }
                        return colorList;
                    }
                    """
                    )
                ),

            )
                .set_global_opts(
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    is_scale=True,
                    grid_index=1,
                    boundary_gap=False,
                    axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                    axistick_opts=opts.AxisTickOpts(is_show=False),
                    splitline_opts=opts.SplitLineOpts(is_show=False),
                    axislabel_opts=opts.LabelOpts(is_show=False),
                    split_number=20,
                    min_="dataMin",
                    max_="dataMax",
                ),
                yaxis_opts=opts.AxisOpts(
                    grid_index=1,
                    is_scale=True,
                    split_number=2,
                    axislabel_opts=opts.LabelOpts(is_show=False),
                    axisline_opts=opts.AxisLineOpts(is_show=False),
                    axistick_opts=opts.AxisTickOpts(is_show=False),
                    splitline_opts=opts.SplitLineOpts(is_show=False),
                ),
                legend_opts=opts.LegendOpts(is_show=False),
                title_opts=opts.TitleOpts(title="volume", pos_top="85%"),  # 标题
            )
        )
        return bar

    def macd(self, echarts_data):
        # Bar-2 (Overlap Bar + Line)
        bar = (
            Bar()
                .add_xaxis(xaxis_data=echarts_data['date'])
                .add_yaxis(
                series_name="MACD",
                y_axis=echarts_data['macd'],
                xaxis_index=2,
                yaxis_index=2,
                label_opts=opts.LabelOpts(is_show=False),
                itemstyle_opts=opts.ItemStyleOpts(
                    color=JsCode(
                        """
                            function(params) {
                                var colorList;
                                if (params.data >= 0) {
                                  colorList = '#ef232a';
                                } else {
                                  colorList = '#14b143';
                                }
                                return colorList;
                            }
                            """
                    )
                ),
            )
                .set_global_opts(
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    grid_index=2,
                    axislabel_opts=opts.LabelOpts(is_show=False),

                    # axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                    axistick_opts=opts.AxisTickOpts(is_show=False),  # 不显示刻度
                    # splitline_opts=opts.SplitLineOpts(is_show=False),   # 不显示刻度
                    # axislabel_opts=opts.LabelOpts(is_show=False),
                    # split_number=20,
                ),
                yaxis_opts=opts.AxisOpts(
                    grid_index=2,
                    split_number=4,
                    axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                    axistick_opts=opts.AxisTickOpts(is_show=False),
                    splitline_opts=opts.SplitLineOpts(is_show=False),
                    axislabel_opts=opts.LabelOpts(is_show=True),
                ),
                legend_opts=opts.LegendOpts(is_show=False),
                title_opts=opts.TitleOpts(subtitle="MACD", pos_top="72%"),
                # legend_opts=opts.LegendOpts(pos_top="68%"),
            )
        )

        macd_line = (
            Line()
                .add_xaxis(xaxis_data=echarts_data['date'])
                .add_yaxis(
                series_name="DIFF",
                y_axis=echarts_data['macd_diff'],
                # xaxis_index=2,
                # yaxis_index=2,
                is_symbol_show=False,  # 去掉折线上的小圆点
                label_opts=opts.LabelOpts(is_show=False),
            )
                .add_yaxis(
                series_name="DEA",
                y_axis=echarts_data["macd_dea"],
                # xaxis_index=2,
                # yaxis_index=2,
                is_symbol_show=False,  # 去掉折线上的小圆点
                label_opts=opts.LabelOpts(is_show=False),
            )
            # .set_global_opts(legend_opts=opts.LegendOpts(is_show=False))
            # .set_global_opts(xaxis_opts=opts.AxisOpts(type_="category"))
        )
        # MACD BAR And MACD Line
        bar_macd_line = bar.overlap(macd_line)
        return bar_macd_line

    def kdj(self, echarts_data):
        # KDJ
        kdj_line = (
            Line()
                .add_xaxis(xaxis_data=echarts_data['date'])
                .add_yaxis(
                series_name="K",
                y_axis=echarts_data['kdj_k'],
                is_symbol_show=False,  # 去掉折线上的小圆点
                label_opts=opts.LabelOpts(is_show=False),
            )
                .add_yaxis(
                series_name="D",
                y_axis=echarts_data["kdj_d"],
                is_symbol_show=False,  # 去掉折线上的小圆点
                label_opts=opts.LabelOpts(is_show=False),
            )
                .add_yaxis(
                series_name="J",
                y_axis=echarts_data["kdj_j"],
                is_symbol_show=False,  # 去掉折线上的小圆点
                label_opts=opts.LabelOpts(is_show=False),
                # markline_opts=opts.MarkLineOpts(
                #     data=[100]
                # ),
            )
                .set_global_opts(
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    grid_index=2,
                    axislabel_opts=opts.LabelOpts(is_show=False),

                    # axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                    axistick_opts=opts.AxisTickOpts(is_show=False),  # 不显示刻度
                    # splitline_opts=opts.SplitLineOpts(is_show=False),   # 不显示刻度
                    # axislabel_opts=opts.LabelOpts(is_show=False),
                    # split_number=20,
                ),
                # title_opts=opts.TitleOpts(subtitle="KDJ"),
                title_opts=opts.TitleOpts(subtitle="KDJ", pos_top="62%"),    # 标题
                legend_opts=opts.LegendOpts(pos_top="58%"),  # 图例位置
            )
        )
        return kdj_line

    def kdj_macd(self, echarts_data, ktype='sum'):
        """
        用kdj的j做成macd趋势图，可以平滑伪金叉
        """
        macd_kdj_bar = (
            Bar()
                .add_xaxis(xaxis_data=echarts_data['date'])
                .add_yaxis(
                series_name="MACD_KDJ",
                y_axis=echarts_data['kdj_macd_%s' % ktype],
                xaxis_index=2,
                yaxis_index=2,
                label_opts=opts.LabelOpts(is_show=False),
                itemstyle_opts=opts.ItemStyleOpts(
                    color=JsCode(
                        """
                            function(params) {
                                var colorList;
                                if (params.data >= 0) {
                                  colorList = '#ef232a';
                                } else {
                                  colorList = '#14b143';
                                }
                                return colorList;
                            }
                            """
                    )
                ),
            )
                .set_global_opts(
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    grid_index=2,
                    axislabel_opts=opts.LabelOpts(is_show=False),

                    # axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                    axistick_opts=opts.AxisTickOpts(is_show=False),  # 不显示刻度
                    # splitline_opts=opts.SplitLineOpts(is_show=False),   # 不显示刻度
                    # axislabel_opts=opts.LabelOpts(is_show=False),
                    # split_number=20,
                ),
                yaxis_opts=opts.AxisOpts(
                    grid_index=2,
                    split_number=4,
                    axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                    axistick_opts=opts.AxisTickOpts(is_show=False),
                    splitline_opts=opts.SplitLineOpts(is_show=False),
                    axislabel_opts=opts.LabelOpts(is_show=True),
                ),
                legend_opts=opts.LegendOpts(is_show=False),
                # title_opts=opts.TitleOpts(subtitle="KDJ_MACD"),
                # title_opts=opts.TitleOpts(subtitle="KDJ_M_%s" % ktype, pos_top="52%"),  # 标题
                # legend_opts=opts.LegendOpts(pos_top="45%"),  # 图例位置
            )
        )

        macd_kdj_line = (
            Line()
                .add_xaxis(xaxis_data=echarts_data['date'])
                .add_yaxis(
                series_name="KDJ_DIFF",
                y_axis=echarts_data['kdj_macd_diff_%s' % ktype],
                # xaxis_index=2,
                # yaxis_index=2,
                is_symbol_show=False,  # 去掉折线上的小圆点
                label_opts=opts.LabelOpts(is_show=False),
            )
                .add_yaxis(
                series_name="KDJ_DEA",
                y_axis=echarts_data["kdj_macd_dea_%s" % ktype],
                # xaxis_index=2,
                # yaxis_index=2,
                is_symbol_show=False,  # 去掉折线上的小圆点
                label_opts=opts.LabelOpts(is_show=False),
            )
            # .set_global_opts(legend_opts=opts.LegendOpts(is_show=False))
            # .set_global_opts(xaxis_opts=opts.AxisOpts(type_="category"))
        )
        # MACD BAR And MACD Line
        bar_macd_kdj_line = macd_kdj_bar.overlap(macd_kdj_line)

        return bar_macd_kdj_line

    def p_kdj_macd(self, echarts_data, ktype='d'):
        """
        p_kdj_macd的百分比图
        """
        bar = (
            Bar()
                .add_xaxis(xaxis_data=echarts_data['date'])
                .add_yaxis(
                series_name="P_MACD_KDJ",
                y_axis=echarts_data['p_kdj_macd_%s' % ktype],
                xaxis_index=2,
                yaxis_index=2,
                label_opts=opts.LabelOpts(is_show=False),
                itemstyle_opts=opts.ItemStyleOpts(
                    color=JsCode(
                        """
                            function(params) {
                                var colorList;
                                if (params.data >= 0) {
                                  colorList = '#ef232a';
                                } else {
                                  colorList = '#14b143';
                                }
                                return colorList;
                            }
                            """
                    )
                ),
            )
                .set_global_opts(
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    grid_index=2,
                    axislabel_opts=opts.LabelOpts(is_show=False),

                    # axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                    axistick_opts=opts.AxisTickOpts(is_show=False),  # 不显示刻度
                    # splitline_opts=opts.SplitLineOpts(is_show=False),   # 不显示刻度
                    # axislabel_opts=opts.LabelOpts(is_show=False),
                    # split_number=20,
                ),
                yaxis_opts=opts.AxisOpts(
                    grid_index=2,
                    split_number=4,
                    axisline_opts=opts.AxisLineOpts(is_on_zero=False),
                    axistick_opts=opts.AxisTickOpts(is_show=False),
                    splitline_opts=opts.SplitLineOpts(is_show=False),
                    axislabel_opts=opts.LabelOpts(is_show=True),
                ),
                legend_opts=opts.LegendOpts(is_show=False),
                # title_opts=opts.TitleOpts(subtitle="KDJ_MACD"),
                title_opts=opts.TitleOpts(subtitle="P_KDJ_M_%s" % ktype, pos_top="52%"),  # 标题
                # legend_opts=opts.LegendOpts(pos_top="45%"),  # 图例位置
            )
        )

        return bar

    def obv(self, echarts_data):
        line = (
            Line()
                .add_xaxis(xaxis_data=echarts_data['date'])
                .add_yaxis(
                series_name="obv",
                y_axis=echarts_data['obv'],
                is_smooth=True,
                is_hover_animation=False,
                label_opts=opts.LabelOpts(is_show=False),
                is_symbol_show=False,  # 去掉折线上的小圆点
            )
                .set_global_opts(
                yaxis_opts=opts.AxisOpts(
                    min_='dataMin'
                ),
                legend_opts=opts.LegendOpts(is_show=False),
                title_opts=opts.TitleOpts(subtitle="obv", pos_top="80%"),  # 标题
                # legend_opts=opts.LegendOpts(pos_top="78%"),  # 图例位置
            )

        )
        return line

    def draw_kline(self, df, filename):
        """
        """
        df = df.sort_index()  # 要正序才能计算KDJ
        df = df.dropna(axis=0, how='any', subset=["close",])
        df = self.SEE.kdj(df)
        df = self.SEE.kdj_macd(df)
        df = self.SEE.p_kdj_macd(df)
        df = self.SEE.macd(df)
        df = self.SEE.ma(df, 30)

        data = []
        for i, row in df.iterrows():
            data.append([row['open'], row['close'], row['low'], row['high']])
        echarts_data = {
            'data': data,
            'date': list(df.index),
            'volume': list(df['volume']),
            'ma5': list(df['ma5']),
            'ma20': list(df['ma20']),
            'ma30': list(df['ma30']),
            'macd': list(df['macd']),
            'kdj_k': list(df['kdj_k']),
            'kdj_d': list(df['kdj_d']),
            'kdj_j': list(df['kdj_j']),
            'macd_diff': list(df['macd_diff']),
            'macd_dea': list(df['macd_dea']),
            'kdj_macd_sum': list(df['kdj_macd_sum']),
            'kdj_macd_avg': list(df['kdj_macd_avg']),
            'kdj_macd_k': list(df['kdj_macd_k']),
            'kdj_macd_d': list(df['kdj_macd_d']),
            'kdj_macd_j': list(df['kdj_macd_j']),
            'kdj_macd_diff_sum': list(df['kdj_macd_diff_sum']),
            'kdj_macd_diff_avg': list(df['kdj_macd_diff_avg']),
            'kdj_macd_diff_k': list(df['kdj_macd_diff_k']),
            'kdj_macd_diff_d': list(df['kdj_macd_diff_d']),
            'kdj_macd_diff_j': list(df['kdj_macd_diff_j']),
            'kdj_macd_dea_sum': list(df['kdj_macd_dea_sum']),
            'kdj_macd_dea_avg': list(df['kdj_macd_dea_avg']),
            'kdj_macd_dea_k': list(df['kdj_macd_dea_k']),
            'kdj_macd_dea_d': list(df['kdj_macd_dea_d']),
            'kdj_macd_dea_j': list(df['kdj_macd_dea_j']),
        }

        # 动态设置只显示30天
        n = 60 / len(df)
        range_start = 0
        if n >= 1:
            range_start = 0
        elif n < 1:
            range_start = (1 - n)*100
        range_end = 100
        kline = self.kline(echarts_data, filename, range_start, range_end)

        macd = self.macd(echarts_data)
        kdj = self.kdj(echarts_data)
        kdj_macd_sum = self.kdj_macd(echarts_data, ktype='sum')
        kdj_macd_avg = self.kdj_macd(echarts_data, ktype='avg')
        kdj_macd_k = self.kdj_macd(echarts_data, ktype='k')
        kdj_macd_d = self.kdj_macd(echarts_data, ktype='d')
        kdj_macd_j = self.kdj_macd(echarts_data, ktype='j')

        # Grid Overlap + Bar
        grid_chart = self.grid_chart()

        # 这个是为了把 data.datas 这个数据写入到 html 中,还没想到怎么跨 series 传值
        # demo 中的代码也是用全局变量传的
        # 配合macd中的js代码变色
        grid_chart.add_js_funcs("var barData = {}".format(echarts_data['data']))

        grid_chart.add(
            kline,
            grid_opts=opts.GridOpts(pos_left="10%", pos_right="8%", height="30%"),
        )


        # 加上KDJ的kdj_macd_sum
        grid_chart.add(
            kdj_macd_sum,
            grid_opts=opts.GridOpts(
                pos_left="10%", pos_right="8%", pos_top="30%", height="10%",
            ),
        )

        # 加上KDJ的kdj_macd_avg
        grid_chart.add(
            kdj_macd_avg,
            grid_opts=opts.GridOpts(
                pos_left="10%", pos_right="8%", pos_top="40%", height="10%",
            ),
        )


        # 加上KDJ的kdj_macd_k
        grid_chart.add(
            kdj_macd_k,
            grid_opts=opts.GridOpts(
                pos_left="10%", pos_right="8%", pos_top="50%", height="10%",
            ),
        )

        # 加上KDJ的kdj_macd_d
        grid_chart.add(
            kdj_macd_d,
            grid_opts=opts.GridOpts(
                pos_left="10%", pos_right="8%", pos_top="60%", height="10%",
            ),
        )

        # 加上KDJ的kdj_macd_j
        grid_chart.add(
            kdj_macd_j,
            grid_opts=opts.GridOpts(
                pos_left="10%", pos_right="8%", pos_top="70%", height="10%",
            ),
        )
        # 加上KDJ
        grid_chart.add(
            kdj,
            grid_opts=opts.GridOpts(
                pos_left="10%", pos_right="8%", pos_top="80%", height="10%",
            ),
        )

        # 加上MACD
        grid_chart.add(
            macd,
            grid_opts=opts.GridOpts(
                pos_left="10%", pos_right="8%", pos_top="90%", height="10%",
            ),
        )


        filepath = self.data_dir + '/pyechart/%s.html' % filename
        grid_chart.render(filepath)

    def draw_charts(self, df, filename=None):
        if not filename:
            filename = df[self.stock_csv_columns_dict['股票代码']].values[0]
        self.draw_kline(df, filename)



def get_current_df(code, ktype='d'):
    """
    将昨日的d线数据和当前最新数据结合，为了得出当前的K图
    """
    df_yesterday = pd.read_csv(conf['options']['data_dir'] + '/stock_%s_csv/%s.csv' % (ktype, code), index_col=['date'],
                     dtype={'code': str})

    df = ts.get_realtime_quotes(code)  # Single stock symbol
    df.rename(
        columns={
            'price': 'close',
        }, inplace=True)
    df['code'] = code
    # str to float
    df[['open', 'high', 'low', 'close', 'volume', 'pre_close']] = df[['open', 'high', 'low', 'close', 'volume', 'pre_close']].astype("float64")
    df['price_change'] = df['close'] - df['pre_close']
    df['pct_change'] = df['price_change'] / df['pre_close'] * 100
    df = df.set_index("date")
    df = df[['code', 'open', 'high', 'low', 'close', 'price_change', 'volume', 'pct_change']]
    df = df.append(df_yesterday)
    return df

if __name__ == '__main__':
    import sys, os
    import json
    import pandas as pd
    import tushare as ts

    pd.set_option('display.width', 300)
    pd.set_option('display.max_columns', 300)
    pd.set_option('display.max_colwidth', 300)
    pd.set_option('display.max_row', 1000)

    config_path = r'C:/Users/HLXD-129/PycharmProjects/Django_Stock/stock/stock_code'
    with open(config_path + '/config.json', 'r', encoding='utf8')as fp:
        conf = json.load(fp)

    SPY = StockPyEchart(conf)
    # SPY = StockPyEchart_2(conf)

    code_list = [
    "000001",
    ]

    the_latest = False

    for code in code_list:
        ktype = 'd'
        if the_latest:
            df = get_current_df(code)   # 根据昨天的获取当前的数据
        else:
            df = pd.read_csv(conf['options']['data_dir'] + '/stock_%s_csv/%s.csv' % (ktype, code), index_col=['date'], dtype={'code':str})
        filename = '%s_d_kdj' % (code + '_' + ktype)
        df = df[:10]
        SPY.draw_charts(df, filename)