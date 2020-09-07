import configparser  # 引入模块
import sys, os
import json

curPath = os.path.abspath(os.path.dirname(__file__))


def run():
    data_dir = curPath + '\data'
    columns = {
        '股票代码': 'symbol',
        '交易时间': 'datetime',
        '开盘价': 'open_price',
        '最高价': 'high_price',
        '最低价': 'low_price',
        '收盘价': 'close_price',
        '昨收价': 'pre_close',
        '涨跌额': 'price_change',  # 收盘价 - 昨收价   也叫 '涨跌额': 'change',
        '涨跌幅': 'pct_change',
        '成交量': 'volume',
        '5日均价': 'ma5',
        '10日均价': 'ma10',
        '20日均价': 'ma20',
        '50日均价': 'ma50',
        '250日均价': 'ma250',
        '5日均量': 'v_ma5',
        '10日均量': 'v_ma10',
        '20日均量': 'v_ma20',
        '50日均量': 'v_ma50',
        '250日均量': 'v_ma250',
        '换手率': 'turnover_rate',
    }
    stock_csv_columns = ['symbol', 'open_price', 'high_price', 'low_price', 'close_price', 'price_change', 'volume']
    config_dic = {
        'options':
            {
                'data_dir': data_dir,
                'stock_csv_columns_dict': columns,
                'stock_csv_columns': stock_csv_columns,
                "ts_token": "659179990b6ea7c96f4d382a537006b8ffd75462cb251da2050c37dd",
            }
    }

    filename = 'config.json'
    with open(filename, 'w') as file_obj:
        json.dump(config_dic, file_obj)


if __name__ == '__main__':
    run()
