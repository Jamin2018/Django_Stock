import talib as ta
import pandas as pd
import numpy as np


class StockEigenvalueExtraction(object):
    """
    特征值处理
    """

    def __init__(self, config_dict):
        self.config = config_dict
        self.options = config_dict['options']
        self.data_dir = config_dict['options']['data_dir']
        self.stock_csv_columns_dict = config_dict['options']['stock_csv_columns_dict']

    def kdj(self, df, fastk_period=9, slowk_period=3, slowd_period=3):
        """
        Cn为第n日收盘价；Ln为n日内的最低价；Hn为n日内的最高价。RSV值始终在1—100间波动。
        RSV=（Cn－Ln）÷（Hn－Ln）×100
        K值=2/3×第8日K值＋1/3×第9日RSV
        D值=2/3×第8日D值＋1/3×第9日K值
        J值=3*第9日K值-2*第9日D值

        公式分析:
        跌涨主要看RSV
        跌涨额小，并且收盘价大于最低价，则KDJ往上走

        当昨日K等于30，RSV = 33.33则当日K不变，即
        Cn－Ln）÷（Hn－Ln）×100 = 33.33
        当昨日K等于80，RSV = 72则当日K不变，即
        Cn－Ln）÷（Hn－Ln）×100 = 72


        :param df:
        :param fastk_period:
        :param slowk_period:
        :param slowd_period:
        :return:
        """
        # 计算kd指标
        low_list = df[self.stock_csv_columns_dict['最低价']].rolling(9, min_periods=9).min()
        low_list.fillna(value=df[self.stock_csv_columns_dict['最低价']].expanding().min(), inplace=True)
        high_list = df[self.stock_csv_columns_dict['最高价']].rolling(9, min_periods=9).max()
        high_list.fillna(value=df[self.stock_csv_columns_dict['最高价']].expanding().max(), inplace=True)
        rsv = (df[self.stock_csv_columns_dict['收盘价']] - low_list) / (high_list - low_list) * 100

        df['kdj_k'] = pd.DataFrame(rsv).ewm(com=2).mean()
        df['kdj_d'] = df['kdj_k'].ewm(com=2).mean()
        df['kdj_j'] = 3 * df['kdj_k'] - 2 * df['kdj_d']
        return df

    def kdj_macd(self, df, type='single', column='kdj_j', fast=12, slow=26, signal=9):
        """
        kdj的macd
        type='single'则取单个值，type='sum'则取总和，type='avg'则取平均值
        """
        # if type == 'single' or not type:
        #     data = df[column]
        # elif type == 'sum':
        #     data = df['kdj_k'] + df['kdj_d'] + df['kdj_j']
        # elif type == 'avg':
        #     data = (df['kdj_k'] + df['kdj_d'] + df['kdj_j'])/3
        # j
        data = df['kdj_j']
        DIFF, DEA, macd = ta.MACD(data, fastperiod=fast, slowperiod=slow, signalperiod=signal)
        df['kdj_macd_j'] = macd * 2
        df['kdj_macd_diff_j'] = DIFF
        df['kdj_macd_dea_j'] = DEA
        # k
        data = df['kdj_k']
        DIFF, DEA, macd = ta.MACD(data, fastperiod=fast, slowperiod=slow, signalperiod=signal)
        df['kdj_macd_k'] = macd * 2
        df['kdj_macd_diff_k'] = DIFF
        df['kdj_macd_dea_k'] = DEA
        # d
        data = df['kdj_d']
        DIFF, DEA, macd = ta.MACD(data, fastperiod=fast, slowperiod=slow, signalperiod=signal)
        df['kdj_macd_d'] = macd * 2
        df['kdj_macd_diff_d'] = DIFF
        df['kdj_macd_dea_d'] = DEA
        # sum
        data = df['kdj_k'] + df['kdj_d'] + df['kdj_j']
        DIFF, DEA, macd = ta.MACD(data, fastperiod=fast, slowperiod=slow, signalperiod=signal)
        df['kdj_macd_sum'] = macd * 2
        df['kdj_macd_diff_sum'] = DIFF
        df['kdj_macd_dea_sum'] = DEA
        # avg
        data = (df['kdj_k'] + df['kdj_d'] + df['kdj_j'])/3
        DIFF, DEA, macd = ta.MACD(data, fastperiod=fast, slowperiod=slow, signalperiod=signal)
        df['kdj_macd_avg'] = macd * 2
        df['kdj_macd_diff_avg'] = DIFF
        df['kdj_macd_dea_avg'] = DEA

        return df

    def p_kdj_macd(self, df , ktype='d'):
        """
        获得kdj_de_macd的百分比，绿柱比例越小的越是买进
        计算kdj_de_macdd区间的百分值
        """

        max_value_list = []
        max_v = 0
        e = -1
        s = 0
        for i in df['kdj_macd_%s' % ktype]:
            # 初始化
            e += 1
            if e == 0:
                max_v = i
                max_value_list.append(max_v)
                continue
            # 1.i 大于0，且max_v大于0，则判断大小
            if i >= 0 and max_v >= 0:
                if i > max_v:
                    max_v = i
                max_value_list.append(max_v)
            # 2.i 小于0，且max_v小于0，则判断大小
            elif i < 0 and max_v < 0:
                if i < max_v:
                    max_v = i
                max_value_list.append(max_v)
            # 3.否则换新区间
            else:
                # 先把前一段的区间更新最大值
                if max_v < 0:  # 小于0的取正，让百分比为负数
                    max_v = - max_v
                max_value_list[s:] = [max_v] * (e - s)
                max_v = i
                max_value_list.append(max_v)
                if e != len(df['kdj_macd_%s' % ktype]):
                    s = e
        # 处理最后一段区间
        if max_v < 0:  # 小于0的取正，让百分比为负数
            max_v = - max_v
        max_value_list[s:] = [max_v] * (e - s + 1)

        p_macd_series = df['kdj_macd_%s' % ktype] / max_value_list

        df = df.join(p_macd_series.to_frame(name='p_kdj_macd_%s' % ktype))
        return df

    def kdj_jincha(self, df, j_k=100, j_d=100, j_j=30, d_k=0, d_d=0, d_j=80):
        """
        计算自定义金叉点
        :param df:
        :param j_k: 金叉买入点k
        :param j_d: 金叉买入点d
        :param j_j: 金叉买入点j
        :param d_k: 死叉卖出点k
        :param d_d: 死叉卖出点d
        :param d_j: 死叉卖出点j
        :return:
        """
        # 计算KDJ指标金叉、死叉情况

        df = df.dropna(axis=0, how='any', subset=["kdj_k", "kdj_d", "kdj_j"])

        if df.empty:
            return df
        # d['kdj_jd'] = ''  # KDJ金叉死叉，金叉j,死叉d
        d = df.copy()
        d.loc[d.index, 'kdj_jd'] = ''
        kdj_position = d['kdj_k'] > d['kdj_d']
        d.loc[kdj_position[(kdj_position == True) & (kdj_position.shift() == False)].index, 'kdj_jd'] = 'j'
        d.loc[kdj_position[(kdj_position == False) & (kdj_position.shift() == True)].index, 'kdj_jd'] = 'd'

        # df['KDJ_res'] = ''
        # df.loc[d[(d['KDJ_金叉死叉'] == '金叉') & (d['KDJ_K'] < j_k) & (d['KDJ_D'] < j_d) & (d['KDJ_J'] < j_j)].index, 'KDJ_res'] = True
        # df.loc[d[(d['KDJ_金叉死叉'] != '金叉') & (d['KDJ_K'] > d_k) & (d['KDJ_D'] > d_d) & (d['KDJ_J'] > d_j)].index, 'KDJ_res'] = False

        # d['kdj_res'] = ''
        d.loc[d.index, 'kdj_res'] = ''
        d.loc[d[(d['kdj_jd'] == 'j') &
                (d['kdj_k'] < j_k) &
                (d['kdj_d'] < j_d) &
                (d['kdj_j'] < j_j)].index, 'kdj_res'] = True  # 金叉买入点
        d.loc[d[(d['kdj_jd'] != 'j') &
                (d['kdj_k'] > d_k) &
                (d['kdj_d'] > d_d) &
                (d['kdj_j'] > d_j)].index, 'kdj_res'] = False  # KDJ过高卖出点
        d = d.dropna(axis=0, how='any', subset=["kdj_jd", "kdj_res", ])
        return d

    def ma(self, df, timeperiod):
        f = 'ma' + str(timeperiod)
        df[f] = ta.MA(df[self.stock_csv_columns_dict['收盘价']], timeperiod=timeperiod)
        return df

    def vma(self, df, timeperiod):
        f = 'v_ma' + str(timeperiod)
        df[f] = ta.MA(df[self.stock_csv_columns_dict['成交量']], timeperiod=timeperiod)
        return df

    def macd(self, df, fast=12, slow=26, signal=9):
        """
        hd_df['DIFF'],hd_df['DEA'],hd_df['MACD'] = ta.MACD(hd_df['close'],fastperiod=fast, slowperiod=slow, signalperiod=signal)
        一般教程都是 macd(DIFF), signal(DEA), hist(MACD柱)
        """
        DIFF, DEA, macd = ta.MACD(df[self.stock_csv_columns_dict['收盘价']], fastperiod=fast, slowperiod=slow, signalperiod=signal)
        df['macd'] = macd * 2
        df['macd_diff'] = DIFF
        df['macd_dea'] = DEA
        return df

    def p_macd(self, hd_df):
        """
        计算最近的macd区间的百分值
        """
        df = hd_df

        max_value_list = []
        max_v = 0
        e = -1
        s = 0
        for i in df['macd']:
            # 初始化
            e += 1
            if e == 0:
                max_v = i
                max_value_list.append(max_v)
                continue
            # 1.i 大于0，且max_v大于0，则判断大小
            if i >= 0 and max_v >= 0:
                if i > max_v:
                    max_v = i
                max_value_list.append(max_v)
            # 2.i 小于0，且max_v小于0，则判断大小
            elif i < 0 and max_v < 0:
                if i < max_v:
                    max_v = i
                max_value_list.append(max_v)
            # 3.否则换新区间
            else:
                # 先把前一段的区间更新最大值
                if max_v < 0:  # 小于0的取正，让百分比为负数
                    max_v = - max_v
                max_value_list[s:] = [max_v] * (e - s)
                max_v = i
                max_value_list.append(max_v)
                if e != len(df['macd']):
                    s = e
        # 处理最后一段区间
        if max_v < 0:  # 小于0的取正，让百分比为负数
            max_v = - max_v
        max_value_list[s:] = [max_v] * (e - s + 1)

        p_macd_series = df['macd'] / max_value_list

        hd_df = hd_df.join(p_macd_series.to_frame(name='p_macd'))
        return hd_df

    def kdj_p_macd(self, df):
        df['kdj_p_macd'] = df['kdj_j'] * df['p_macd']
        return df

    def ma5_kdj(self, df):
        """
        因为KDJ根据最高值做分母，如果某日暴涨，会影响到KDJ的准确度，故试用5日均线来做KDJ预测走势
        """
        low_list = df[self.stock_csv_columns_dict['最低价']].rolling(9, min_periods=9).min()
        low_list.fillna(value=df[self.stock_csv_columns_dict['最低价']].expanding().min(), inplace=True)
        high_list = df['ma5'].rolling(9, min_periods=9).max()
        high_list.fillna(value=df['ma5'].expanding().max(), inplace=True)
        rsv = (df[self.stock_csv_columns_dict['收盘价']] - low_list) / (high_list - low_list) * 100

        df['kdj_ma5_k'] = pd.DataFrame(rsv).ewm(com=2).mean()
        df['kdj_ma5_d'] = df['kdj_ma5_k'].ewm(com=2).mean()
        df['kdj_ma5_j'] = 3 * df['kdj_ma5_k'] - 2 * df['kdj_ma5_d']
        return df

    def obv(self, df):
        obv = ta.OBV(df[self.stock_csv_columns_dict['收盘价']], df[self.stock_csv_columns_dict['成交量']])
        df['obv'] = obv
        return df

if __name__ == '__main__':
    pd.set_option('display.width', 300)
    pd.set_option('display.max_columns', 300)
    pd.set_option('display.max_colwidth', 300)
    pd.set_option('display.max_row', 1000)

    import json
    config_path = r'C:\Users\HLXD-129\PycharmProjects\Django_Stock\stock\stock_tools'
    with open(config_path + '/config.json', 'r', encoding='utf8')as fp:
        conf = json.load(fp)
    code = '000001'
    df = pd.read_csv('./data/stock_d_csv/%s.csv' % (code), index_col=['date'])
    SEE = StockEigenvalueExtraction(conf)
    df = df.sort_index()  # 要正序才能计算KDJ
    df = SEE.kdj(df)
    df = SEE.ma(df, 5)
    df = SEE.ma5_kdj(df)
    df = SEE.obv(df)
    df = SEE.kdj_macd(df)
    df = SEE.p_kdj_macd(df, ktype='d')
    df = df.sort_index(ascending=False)  # 倒序
    df = df[['close_price', 'kdj_d', 'kdj_macd_d', 'p_kdj_macd_d']]
    print(df[:500])
