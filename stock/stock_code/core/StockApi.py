import tushare as ts
from multiprocessing import Process
import os
import time

class StockApi(object):
    """
    从Tushare接口获取数据
    """

    def __init__(self, config_dict):
        self.config = config_dict
        self.options = config_dict['options']
        self.data_dir = config_dict['options']['data_dir']
        self.stock_csv_columns_dict = config_dict['options']['stock_csv_columns_dict']
        self.stock_csv_columns = config_dict['options']['stock_csv_columns']
        ts.set_token(config_dict['options']['ts_token'])
        self.ts = ts
        self.pro = ts.pro_api()

    def get_hist_data(self, stock_code, ktype='D', end=None):
        df = self.ts.get_hist_data(stock_code, ktype=ktype, end=end)
        if df is not None:
            # 新增code列
            df['code'] = stock_code

            # 改列名
            df.rename(
                columns={
                    'p_change': self.stock_csv_columns_dict['涨跌幅'],
                }, inplace=True)

            df = df[self.stock_csv_columns]
        return df

    def get_hist_data_of_ts_pro(self, ts_code, adj='qfq', ma=[5, 20, 50, 250]):
        def _transfer_time(x):
            res = x[:4] + '-' + x[4:6] + '-' + x[6:]
            return res
        def _transfer_code(x):
            res = x.split('.')[0]
            return res
        df = self.ts.pro_bar(ts_code=ts_code, adj=adj, ma=ma)
        # 改列名
        if df is not None:
            df.rename(
                columns={'ts_code': self.stock_csv_columns_dict['股票代码'],
                         'trade_date': self.stock_csv_columns_dict['交易时间'],
                         'change': self.stock_csv_columns_dict['涨跌额'],
                         'pct_chg': self.stock_csv_columns_dict['涨跌幅'],
                         'vol': self.stock_csv_columns_dict['成交量'],
                         'ma_v_5': self.stock_csv_columns_dict['5日均量'],
                         'ma_v_20': self.stock_csv_columns_dict['20日均量'],
                         'ma_v_50': self.stock_csv_columns_dict['50日均量'],
                         'ma_v_250': self.stock_csv_columns_dict['250日均量'],
                         }, inplace=True)

            # 修改时间的格式
            df[self.stock_csv_columns_dict['交易时间']] = df[self.stock_csv_columns_dict['交易时间']].map(_transfer_time)
            df[self.stock_csv_columns_dict['股票代码']] = df[self.stock_csv_columns_dict['股票代码']].map(_transfer_code)
            # 把时间作为索引
            df.index = df[self.stock_csv_columns_dict['交易时间']]
            df = df[self.stock_csv_columns]
        return df

    def update_stock_csv(self, df_stock_code, ktype='D', pro=True):
        """

        :param df_stock_code:
        :param ktype:
        :param pro: IF True使用PRO接口的数据
        :return:
        """
        for code in df_stock_code:
            old_code = code  # 用于打印计数
            if pro:
                if ktype == 'D' or ktype == 'W':
                    try:
                        df = self.get_hist_data_of_ts_pro(code, ma=[5, 20])
                    except Exception as e:
                        print("error:", e)
                        time.sleep(60)
                    code = code.split('.')[0]   # 修改用于下面储存文件名
                elif ktype == "60":
                    code = code.split('.')[0]
                    df = self.get_hist_data(code, ktype=ktype)
            else:
                code = code.split('.')[0]
                df = self.get_hist_data(code, ktype=ktype)

            if df is not None and not df.empty:
                stock_file_name = code + '.csv'
                df.to_csv(self.data_dir + '/stock_%s_csv/' % ktype + stock_file_name)
                print(self.data_dir + '/stock_%s_csv/' % ktype + stock_file_name, df_stock_code.index(old_code))
            else:
                print('没获取到：', code)

    def run(self):
        # =======================================
        # 先下载大盘行情，因为pro接口没有，不使用pro
        df_stock_code = ['sh', 'sz', 'cyb']
        for i in ['60', 'D']:
            self.update_stock_csv(df_stock_code, ktype=i, pro=False)
        # =======================================
        df_stock_code = self.pro.stock_basic(exchange='', list_status='L',
                                        fields='ts_code,symbol,name,area,industry,list_date')
        df_stock_code.to_csv(self.data_dir + '/code_list.csv')
        df_stock_code = list(df_stock_code['ts_code'])
        for i in ['60', 'D']:
            self.update_stock_csv(df_stock_code, ktype=i,)

