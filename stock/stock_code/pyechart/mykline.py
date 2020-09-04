from typing import List, Sequence, Union

from pyecharts import options as opts
from pyecharts.commons.utils import JsCode
from pyecharts.charts import Kline, Line, Bar, Grid

import pandas as pd


def df_to_echarts_data(df):
    data = []
    for i, row in df.iterrows():
        data.append([row['open'], row['close'], row['low'], row['high']])
    date = list(df.index)
    volume = list(df['volume'])
    ma5 = list(df['ma5'])
    ma20 = list(df['ma20'])
    macd = list(df['macd'])
    kdj_k = list(df['kdj_k'])
    kdj_d = list(df['kdj_d'])
    kdj_j = list(df['kdj_j'])
    macd_diff = list(df['macd_diff'])
    macd_dea = list(df['macd_dea'])
    kdj_macd = list(df['kdj_macd'])
    kdj_macd_diff = list(df['kdj_macd_diff'])
    kdj_macd_dea = list(df['kdj_macd_dea'])
    return {
        'data': data,
        'date': date,
        'volume': volume,
        'ma5': ma5,
        'ma20': ma20,
        'macd': macd,
        'kdj_k': kdj_k,
        'kdj_d': kdj_d,
        'kdj_j': kdj_j,
        'macd_diff': macd_diff,
        'macd_dea': macd_dea,
        'kdj_macd': kdj_macd,
        'kdj_macd_diff': kdj_macd_diff,
        'kdj_macd_dea': kdj_macd_dea,
    }


def draw_charts(echarts_data):
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
                    range_start=50,
                    range_end=100,
                ),
                opts.DataZoomOpts(
                    is_show=True,
                    xaxis_index=[0, 1, 2, 3, 4],
                    type_="slider",
                    range_start=50,
                    range_end=100,
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
            title_opts=opts.TitleOpts(title="my_echart"),
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
            series_name="MA20",
            y_axis=echarts_data['ma20'],
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


    bar = (
        Bar()
        .add_xaxis(xaxis_data=date)
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
        )
    )






    # Bar-2 (Overlap Bar + Line)
    bar_2 = (
        Bar()
            .add_xaxis(xaxis_data=date)
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
        )
    )



    macd_line = (
        Line()
        .add_xaxis(xaxis_data=date)
        .add_yaxis(
            series_name="DIFF",
            y_axis=echarts_data['macd_diff'],
            # xaxis_index=2,
            # yaxis_index=2,
            label_opts=opts.LabelOpts(is_show=False),
        )
        .add_yaxis(
            series_name="DEA",
            y_axis=echarts_data["macd_dea"],
            # xaxis_index=2,
            # yaxis_index=2,
            is_symbol_show=False,   # 去掉折线上的小圆点
            label_opts=opts.LabelOpts(is_show=False),
        )
        # .set_global_opts(legend_opts=opts.LegendOpts(is_show=False))
        # .set_global_opts(xaxis_opts=opts.AxisOpts(type_="category"))
    )
    # MACD BAR And MACD Line
    bar_macd_line = bar_2.overlap(macd_line)



    # KDJ
    kdj_line = (
        Line()
        .add_xaxis(xaxis_data=date)
        .add_yaxis(
            series_name="K",
            y_axis=echarts_data['kdj_k'],
            is_symbol_show=False,  # 去掉折线上的小圆点
            label_opts=opts.LabelOpts(is_show=False),
        )
        .add_yaxis(
            series_name="D",
            y_axis=echarts_data["kdj_d"],
            is_symbol_show=False,   # 去掉折线上的小圆点
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
        )
    )

    ######################
    ## kdj的macd

    # Bar-2 (Overlap Bar + Line)
    macd_kdj_bar = (
        Bar()
            .add_xaxis(xaxis_data=date)
            .add_yaxis(
            series_name="MACD_KDJ",
            y_axis=echarts_data['kdj_macd'],
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
        )
    )



    macd_kdj_line = (
        Line()
        .add_xaxis(xaxis_data=date)
        .add_yaxis(
            series_name="KDJ_DIFF",
            y_axis=echarts_data['kdj_macd_diff'],
            # xaxis_index=2,
            # yaxis_index=2,
            is_symbol_show=False,  # 去掉折线上的小圆点
            label_opts=opts.LabelOpts(is_show=False),
        )
        .add_yaxis(
            series_name="KDJ_DEA",
            y_axis=echarts_data["kdj_macd_dea"],
            # xaxis_index=2,
            # yaxis_index=2,
            is_symbol_show=False,   # 去掉折线上的小圆点
            label_opts=opts.LabelOpts(is_show=False),
        )
        # .set_global_opts(legend_opts=opts.LegendOpts(is_show=False))
        # .set_global_opts(xaxis_opts=opts.AxisOpts(type_="category"))
    )
    # MACD BAR And MACD Line
    bar_macd_kdj_line = macd_kdj_bar.overlap(macd_kdj_line)


    ######################







    # Grid Overlap + Bar
    grid_chart = Grid(
        init_opts=opts.InitOpts(
            width="1000px",
            height="800px",
            animation_opts=opts.AnimationOpts(animation=False),
        )
    )

    # 这个是为了把 data.datas 这个数据写入到 html 中,还没想到怎么跨 series 传值
    # demo 中的代码也是用全局变量传的
    grid_chart.add_js_funcs("var barData = {}".format(kline_data))

    grid_chart.add(
        overlap_kline_line,
        grid_opts=opts.GridOpts(pos_left="10%", pos_right="8%", height="30%"),
    )
    grid_chart.add(
        bar,
        grid_opts=opts.GridOpts(
            pos_left="10%", pos_right="8%", pos_top="35%", height="10%"
        ),
    )

    # 加上MACD
    grid_chart.add(
        bar_macd_line,
        grid_opts=opts.GridOpts(
            pos_left="10%", pos_right="8%", pos_top="45%", height="10%",
        ),
    )

    # 加上KDJ
    grid_chart.add(
        kdj_line,
        grid_opts=opts.GridOpts(
            pos_left="10%", pos_right="8%", pos_top="55%", height="10%",
        ),
    )

    # 加上KDJ的MACD
    grid_chart.add(
        bar_macd_kdj_line,
        grid_opts=opts.GridOpts(
            pos_left="10%", pos_right="8%", pos_top="65%", height="10%",
        ),
    )


    grid_chart.render("300368.html")


if __name__ == '__main__':
    from core.StockEigenvalueExtraction import StockEigenvalueExtraction
    SEE = StockEigenvalueExtraction()
    df = pd.read_csv('300368.csv', index_col=['date'])
    df = df.sort_index()  # 要正序才能计算KDJ

    df = SEE.kdj(df)
    df = SEE.kdj_de_macd(df)
    df = SEE.macd(df)

    # df = df[-100:]
    echarts_data = df_to_echarts_data(df)

    draw_charts(echarts_data)

