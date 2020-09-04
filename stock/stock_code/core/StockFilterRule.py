import time
from StockEigenvalueExtraction import StockEigenvalueExtraction


class StockFilterRule(object):
    """
    根据规则选择
    """

    def __init__(self, config_dict):
        self.data_dir = config_dict['options']['data_dir']
        self.SEE = StockEigenvalueExtraction()

    def kdj(self, df_stock_code, ktype):
        """
        获得金叉的code
        :param ktype:
        :param df_stock_code:
        :return:
        """
        df_kdj = []
        for code in df_stock_code:
            df = pd.read_csv(self.data_dir + '/stock_%s_csv/%s.csv' % (ktype, code), index_col=['date'])
            # =========================================================================================================
            # 特征处理
            df = df.sort_index()  # 要正序才能计算KDJ
            df = self.SEE.kdj(df)
            df = self.SEE.kdj_jincha(df)
            df = df.sort_index(ascending=False)  # 倒序
            # =========================================================================================================
            # # 超卖
            # if not df.empty and df[:1]['kdj_j'].values[0] < 0 and df[:1]['kdj_k'].values[0] < 15:
            #     df_kdj.append(code)
            # 金叉
            if not df.empty and True in df[:1]['kdj_res'].values and df[:1]['kdj_k'].values[0] < 20:
                df_kdj.append(code)
            # =========================================================================================================
            task_rate = round(((df_stock_code.index(code) + 1) / len(df_stock_code)) * 100, 2)
            print('\r KDJ %s task: ' % ktype + str(task_rate) + '%', end='', flush=True)
        d = pd.DataFrame(data=df_kdj, columns=['code'], dtype=None, copy=False)
        d.to_csv(
            self.data_dir + '/res/' + '%s_kdj_%s.csv' % (time.strftime('%Y_%m_%d', time.localtime(time.time())), ktype),
            index=None)
        print(df_kdj)
        return "[%s]KDJ：%s\n" % (ktype, df_kdj)

    def abnormal_trading_volume(self, df_stock_code, ktype):
        """
        交易量突然暴涨
        :param ktype:
        :param df_stock_code:
        :return:
        """
        division = 1
        day = 50

        stock_break_code = []
        for code in df_stock_code:
            df = pd.read_csv(self.data_dir + '/stock_%s_csv/%s.csv' % (ktype, code), index_col=['date'])
            # =========================================================================================================
            # 特征处理
            df = df.sort_index()  # 要正序才能计算KDJ
            df = self.SEE.vma(df, 250)
            # df = self.SEE.kdj_jincha(df)
            df = df.sort_index(ascending=False)  # 倒序
            # =========================================================================================================
            # 判断逻辑
            d1 = df[:division]
            d2 = df[division:day]
            position1 = d1['volume'] > (d1['v_ma250'] * 3)  # 当日成交量大于3倍的均20日量线，则为True
            position2 = (d2['volume']) < d2['v_ma250'] * 1.2

            # position1.sum() 统计True的个数，记录近期突破的天数，若不为0，则表示近期突破了均线
            # position2.sum() 统计True的个数，记录长期突破的天数，若为0，则表示长期处于均线以下
            if position1.sum() > 0 and position2.sum() > (day - division) * 0.8:
                stock_break_code.append(code)
            # =========================================================================================================
            task_rate = round(((df_stock_code.index(code) + 1) / len(df_stock_code)) * 100, 2)
            print('\r abnormal_trading_volume %s task: ' % ktype + str(task_rate) + '%', end='', flush=True)

        d = pd.DataFrame(data=stock_break_code, columns=['code'], dtype=None, copy=False)
        d.to_csv(self.data_dir + '/res/' + '%s_trading_volume_%s.csv' % (
        time.strftime('%Y_%m_%d', time.localtime(time.time())), ktype), index=None)
        print(stock_break_code)

        return "[%s]abnormal_trading_volume：%s\n" % (ktype, stock_break_code)

    def price_and_volume_down(self, df_stock_code, ktype):
        """
        价跌量缩
        找出最近3天都量缩的
        3天以前交易量大的
        :param df_stock_code:
        :param ktype:
        :return:
        """
        division = 4
        day = 30

        price_and_volume_down_code = []
        for code in df_stock_code:
            df = pd.read_csv(self.data_dir + '/stock_%s_csv/%s.csv' % (ktype, code), index_col=['date'])
            # =========================================================================================================
            # 特征处理
            df = df.sort_index()  # 要正序才能计算KDJ
            df = self.SEE.vma(df, 250)
            # df = self.SEE.kdj_jincha(df)
            df = df.sort_index(ascending=False)  # 倒序
            # =========================================================================================================
            # 判断逻辑
            d1 = df[:division]
            d2 = df[division:day]

            position1 = d1['volume'] < (d1['v_ma250'] * 0.8)  # 当日成交量大于3倍的均20日量线，则为True
            position2 = (d2['volume']) > d2['v_ma250'] * 1.2

            if position1.sum() > 3 and position2.sum() > (day - division) * 0.8:
                price_and_volume_down_code.append(code)
            # =========================================================================================================
            task_rate = round(((df_stock_code.index(code) + 1) / len(df_stock_code)) * 100, 2)
            print('\r price_and_volume_down %s task: ' % ktype + str(task_rate) + '%', end='', flush=True)

        d = pd.DataFrame(data=price_and_volume_down_code, columns=['code'], dtype=None, copy=False)
        d.to_csv(self.data_dir + '/res/' + '%s_volume_down_%s.csv' % (
            time.strftime('%Y_%m_%d', time.localtime(time.time())), ktype), index=None)
        print(price_and_volume_down_code)
        return "[%s]price_and_volume_down：%s\n" % (ktype, price_and_volume_down_code)

    def kdj_j_small(self, df_stock_code, ktype):
        """
        KDJ 的 J连续小于0
        """
        division = 4
        day = 30

        kdj_j_small = []
        for code in df_stock_code:
            df = pd.read_csv(self.data_dir + '/stock_%s_csv/%s.csv' % (ktype, code), index_col=['date'])
            # =========================================================================================================
            # 特征处理
            df = df.sort_index()  # 要正序才能计算KDJ
            df = self.SEE.kdj(df)
            df = df.sort_index(ascending=False)  # 倒序
            # =========================================================================================================
            # 判断逻辑
            v = df['kdj_j'][:2].values
            m = df['kdj_j'][2:3].values
            if all(j < 0 for j in v) and m and m > 0:
                kdj_j_small.append(code)
            # =========================================================================================================
            task_rate = round(((df_stock_code.index(code) + 1) / len(df_stock_code)) * 100, 2)
            print('\r kdj_j_small %s task: ' % ktype + str(task_rate) + '%', end='', flush=True)

        d = pd.DataFrame(data=kdj_j_small, columns=['code'], dtype=None, copy=False)
        d.to_csv(self.data_dir + '/res/' + '%s_kdj_j_small_%s.csv' % (
            time.strftime('%Y_%m_%d', time.localtime(time.time())), ktype), index=None)
        print(kdj_j_small)

        return "[%s]kdj_j_small：%s\n" % (ktype, kdj_j_small)

    def looking_for_potential_stock(self, df_stock_code, ktype):
        """
        找庄股，待完善
        """
        division = 250
        potential_stock = []
        for code in df_stock_code:
            df = pd.read_csv(self.data_dir + '/stock_%s_csv/%s.csv' % (ktype, code), index_col=['date'])
            # =========================================================================================================
            # 特征处理
            df = df.sort_index()  # 要正序才能计算KDJ
            df = self.SEE.vma(df, 250)
            # df = self.SEE.kdj_jincha(df)
            df = df.dropna(axis=0, how='any', subset=["v_ma250"])
            df = df.sort_index(ascending=False)  # 倒序
            # =========================================================================================================
            # 判断逻辑
            d1 = df[:division]
            position1 = d1['volume'] > (d1['v_ma250'] * 1.5)  # 当日成交量大于3倍的均20日量线，则为True
            if len(df) >= division and position1.sum() < 4:
                potential_stock.append(code)
            # =========================================================================================================
            task_rate = round(((df_stock_code.index(code) + 1) / len(df_stock_code)) * 100, 2)
            print('\r potential_stock %s task: ' % ktype + str(task_rate) + '%', end='', flush=True)

        d = pd.DataFrame(data=potential_stock, columns=['code'], dtype=None, copy=False)
        d.to_csv(self.data_dir + '/res/' + '%s_potential_stock_%s.csv' % (
            time.strftime('%Y_%m_%d', time.localtime(time.time())), ktype), index=None)
        print(potential_stock)

        return "[%s]kdj_j_small：%s\n" % (ktype, potential_stock)

    def kdj_and_macd(self, df_stock_code, ktype):
        """
        kdj小，且macd在 -0.25到0之间
        """
        division = 250
        kdj_and_macd = []

        scores = []
        for code in df_stock_code:
            df = pd.read_csv(self.data_dir + '/stock_%s_csv/%s.csv' % (ktype, code), index_col=['date'])
            # =========================================================================================================
            # 特征处理
            df = df.sort_index()  # 要正序才能计算KDJ
            df = self.SEE.vma(df, 250)
            df = self.SEE.kdj(df)
            df = self.SEE.kdj_jincha(df)
            df = self.SEE.macd(df)
            df = self.SEE.p_macd(df)
            df = df.sort_index(ascending=False)  # 倒序
            # =========================================================================================================
            # 判断逻辑
            p = df['p_macd'].values[0]
            kdj_j = df['kdj_j'].values[0]
            f = True
            if -0.25 < p < 0:
                for i in df['p_macd'].values[1:]:
                    if i > p > -1:  # 绿柱不能比前面的柱大
                        f = False
                    elif i == 1:
                        break
                if f and kdj_j < 50:
                    scores.append((code, kdj_j))
            # =========================================================================================================
            task_rate = round(((df_stock_code.index(code) + 1) / len(df_stock_code)) * 100, 2)
            print('\r kdj_and_macd %s task: ' % ktype + str(task_rate) + '%', end='', flush=True)

        # 根据kdj_k排序，然后选前4个
        def takeSecond(elem):
            return elem[1]
        scores.sort(key=takeSecond)
        print(scores)
        for s in scores[:4]:
            kdj_and_macd.append(s[0])

        d = pd.DataFrame(data=kdj_and_macd, columns=['code'], dtype=None, copy=False)
        d.to_csv(self.data_dir + '/res/' + '%s_kdj_and_macd_%s.csv' % (
            time.strftime('%Y_%m_%d', time.localtime(time.time())), ktype), index=None)
        print(kdj_and_macd)

        return "[%s]kdj_and_macd：%s\n" % (ktype, kdj_and_macd)

    def yuan_ge_trend_stock(self, df_stock_code, ktype):
        """
        知乎上远哥的选股模板，选出的股票很多，感觉不太好用
        怎么判断一只股票处于上升趋势？ - 阿远的回答 - 知乎
        https://www.zhihu.com/question/332916752/answer/735845974
        """
        division = 4
        day = 30

        yuan_ge_trend_stock = []
        for code in df_stock_code:
            df = pd.read_csv(self.data_dir + '/stock_%s_csv/%s.csv' % (ktype, code), index_col=['date'])
            # =========================================================================================================
            # 特征处理
            df = df.sort_index()  # 要正序才能计算KDJ
            df = self.SEE.ma(df, timeperiod=50)
            df = self.SEE.ma(df, timeperiod=150)
            df = self.SEE.ma(df, timeperiod=200)
            df = df.sort_index(ascending=False)  # 倒序
            # =========================================================================================================
            # 判断逻辑
            price = df['close'].values[0]
            ma50 = df['ma50'].values[0]
            ma150 = df['ma150'].values[0]
            ma200 = df['ma200'].values[0]
            # 最近一年最低股价
            min_price = min(df['close'].values[:250])
            # 最近一年最高股价
            max_price = max(df['close'].values[:250])
            df['k_ma200'] = df['ma200'] - df['ma200'].shift(periods=-1) # 减去前一天的ma200
            temp = df[:30]['k_ma200']   # 30日


            if len(df) > 250:
                if price > ma150 and price > ma200:  # 1.当前股价处于150日和200日均线上方
                    if ma150 > ma200 and ma50:  # 2.150日均线处于200日均线上方
                        if (temp >= 0).sum() == temp.size:  # 3.200日均线至少上涨了一个月（大多数情况下，上涨4-5个月更好）
                            if ma50 > ma150 and ma50 > ma200:  # 4.50日移动均线平均值高于150日及200日移动平均值
                                if price > ma50:  # 当前价格高于50日移动平均值
                                    if price >= min_price*1.3:  # 当前股价比最近一年在最低股价至少高30%
                                        if price >= max_price*0.75:  # 当前价格至少处在最近一年最高价的75%以内（距离最高价越近越好）
                                            yuan_ge_trend_stock.append(code)

                # =========================================================================================================
            task_rate = round(((df_stock_code.index(code) + 1) / len(df_stock_code)) * 100, 2)
            print('\r yuan_ge_trend_stock %s task: ' % ktype + str(task_rate) + '%', end='', flush=True)

        d = pd.DataFrame(data=yuan_ge_trend_stock, columns=['code'], dtype=None, copy=False)
        d.to_csv(self.data_dir + '/res/' + '%s_yuan_ge_trend_stock_%s.csv' % (
            time.strftime('%Y_%m_%d', time.localtime(time.time())), ktype), index=None)
        print(yuan_ge_trend_stock)

    def k300_upward_trend(self, df_stock_code, ktype, start="2015-09-01",):
        """300均线趋势向上，类似茅台，海天味业"""
        k300_upward_trend = []

        for code in df_stock_code:
            df = pd.read_csv(self.data_dir + '/stock_%s_csv/%s.csv' % (ktype, code), index_col=['date'])
            # =========================================================================================================
            # 特征处理
            df = df.sort_index()  # 要正序才能计算KDJ
            df = self.SEE.ma(df, 300)
            df = df.sort_index(ascending=False)  # 倒序
            # =========================================================================================================
            # 判断逻辑

            df['upward_trend'] = df['ma300'] > df['ma300'].shift(periods=-1)
            # 取2015年后的
            df = df.loc[start < df.index, :]

            if df['upward_trend'].sum() / len(df['upward_trend']) > 0.95:
                    k300_upward_trend.append(code)
            # =========================================================================================================
            task_rate = round(((df_stock_code.index(code) + 1) / len(df_stock_code)) * 100, 2)
            print('\r k300_upward_trend %s task: ' % ktype + str(task_rate) + '%', end='', flush=True)


        d = pd.DataFrame(data=k300_upward_trend, columns=['code'], dtype=None, copy=False)
        d.to_csv(self.data_dir + '/res/' + '%s_k300_upward_trend_%s.csv' % (
            time.strftime('%Y_%m_%d', time.localtime(time.time())), ktype), index=None)
        print(k300_upward_trend)

        return "[%s]k300_upward_trend：%s\n" % (ktype, k300_upward_trend)

    def run_60(self, msg, df_stock_code):
        ktype = '60'
        # 执行rule
        msg += self.kdj(df_stock_code, ktype=ktype)
        msg += self.abnormal_trading_volume(df_stock_code, ktype=ktype)
        msg += self.price_and_volume_down(df_stock_code, ktype=ktype)
        return msg

    def run_d(self, msg, df_stock_code):
        ktype = 'd'
        # msg += self.kdj(df_stock_code, ktype=ktype)
        # msg += self.abnormal_trading_volume(df_stock_code, ktype=ktype)
        # msg += self.price_and_volume_down(df_stock_code, ktype=ktype)
        # msg += self.kdj_j_small(df_stock_code, ktype=ktype)
        # msg += self.kdj_and_macd(df_stock_code, ktype=ktype)
        msg += self.k300_upward_trend(df_stock_code, ktype=ktype)
        return msg

    def all_df_stock_code(self, ktype='d'):
        #########################################
        # 所有股票监控
        df_stock_code = []
        path = self.data_dir + '/stock_%s_csv/' % ktype
        for root, dirs, files in os.walk(path):
            for i in files:
                    df_stock_code.append(i[:-4])
        ##########################################
        return df_stock_code

    def value_df_stock_code(self):
        df_stock_code = []
        return df_stock_code

    def run_all(self):
        """
        整合的最终选股策略
        1.周线P_MACD是1
        2.日线p_kdj_macd 在 -0.5 - 0之间
        """
        w_df_stock_code = self.all_df_stock_code(ktype='w')
        df_w_p_macd = []
        df_kdj = []

        # 判断周线的MACD是红的
        ktype = 'w'
        for code in w_df_stock_code:
            df = pd.read_csv(self.data_dir + '/stock_%s_csv/%s.csv' % (ktype, code), index_col=['date'])

            # 特征处理
            df = df.sort_index()  # 要正序才能计算KDJ
            df = self.SEE.macd(df)
            df = self.SEE.p_macd(df)
            df = df.sort_index(ascending=False)  # 倒序
            if not df.empty and df.p_macd[0] == 1:
                df_w_p_macd.append(code)
            task_rate = round(((w_df_stock_code.index(code) + 1) / len(w_df_stock_code)) * 100, 2)
            print('\r run_all_macd %s task: ' % ktype + str(task_rate) + '%', end='', flush=True)
        # 判断日线的p_kdj_macd
        print(len(df_w_p_macd))
        ktype = 'd'
        for code in df_w_p_macd:
            df = pd.read_csv(self.data_dir + '/stock_%s_csv/%s.csv' % (ktype, code), index_col=['date'])
            # =========================================================================================================
            # 特征处理
            df = df.sort_index()  # 要正序才能计算KDJ
            df = self.SEE.kdj(df)
            df = self.SEE.kdj_macd(df)
            df = self.SEE.p_kdj_macd(df)
            df = df.sort_index(ascending=False)  # 倒序
            # =========================================================================================================
            if not df.empty and -0.5 <= df.p_kdj_macd_d[0] <= 0 and df.kdj_k[0] < df.kdj_d[0]:
                df_kdj.append(code)
            task_rate = round(((df_w_p_macd.index(code) + 1) / len(df_w_p_macd)) * 100, 2)
            print('\r run_all_kdj %s task: ' % ktype + str(task_rate) + '%', end='', flush=True)
        d = pd.DataFrame(data=df_kdj, columns=['code'], dtype=None, copy=False)
        d.to_csv(
            self.data_dir + '/res/' + '%s_run_all_%s.csv' % (time.strftime('%Y_%m_%d', time.localtime(time.time())), ktype),
            index=None)
        print(len(df_kdj) )
        print(df_kdj)
        return "[%s]run_all：%s\n" % (ktype, df_kdj)


    def run(self):
        msg = ''
        # df_stock_code = self.all_df_stock_code(ktype='60')
        # # TODO 改成先通过基本面选择出来的股票进行监控
        # msg = self.run_60(msg, df_stock_code)
        # df_stock_code = self.all_df_stock_code(ktype='d')
        # msg = self.run_d(msg, df_stock_code)

        msg = self.run_all()
        return msg


if __name__ == '__main__':
    import sys, os
    import json
    import pandas as pd
    from sendMail import mail

    pd.set_option('display.width', 300)
    pd.set_option('display.max_columns', 300)
    pd.set_option('display.max_colwidth', 300)
    pd.set_option('display.max_row', 1000)

    config_path = 'C:\\Users\\HLXD-129\\PycharmProjects\\stock\\'
    with open(config_path + '/config.json', 'r', encoding='utf8')as fp:
        conf = json.load(fp)

    SFR = StockFilterRule(conf)
    msg = SFR.run()
    t = time.strftime('%Y_%m_%d', time.localtime(time.time()))
    mail(t, msg)
    print(msg)

    # SFR = StockFilterRule(conf)
    # ktype = 'd'
    # df_stock_code = SFR.all_df_stock_code()
    # # df_stock_code = ["002957"]
    # SFR.yuan_ge_trend_stock(df_stock_code, ktype=ktype)