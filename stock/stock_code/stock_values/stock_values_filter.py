import sys, os
import json
import pandas as pd


pd.set_option('display.width', 300)
pd.set_option('display.max_columns', 300)
pd.set_option('display.max_colwidth', 300)
pd.set_option('display.max_row', 1000)

config_path = 'C:\\Users\\HLXD-129\\PycharmProjects\\stock\\'
with open(config_path + '/config.json', 'r', encoding='utf8')as fp:
    conf = json.load(fp)


data_dir = conf['options']['data_dir']
df = pd.read_csv(data_dir + '/other/stock_info_20200821.csv')

##############################################################
# 清洗
def _transfer_code(x):
    x = x.replace('=', '')
    x = x.replace('"', '')
    return x

def peg(df):
    df['g3'] = ((df['净利润2020']/df['净利润2016']) ** (1/4)) - 1
    df['PEG'] = df['PE'] / (df['g3'] * 100)
    return df

def underestimate_price(df):
    """
    计算低估价位点

    #每股收益TTM 尽量最新才更准确
    pe = 股价/ 每股收益TTM
    peg = pe / (g*100)

    1 = 股价/ (每股收益TTM * g * 100)
    股价 = (每股收益TTM * g * 100)
    """
    df['underestimate_price'] = 100 * df['g3'] * df['每股收益2020TTM']
    return df

##############################################################

df['代码'] = df['代码'].map(_transfer_code)

df = peg(df)
df = underestimate_price(df)
##############################################################
# 筛选规则
def get_roe(df, k20=0.2, k19=0.2, k18=0.2, k17=0.2, k16=0.2, k15=0):
    df = df[(df['ROE_TTM_2020'] >= k20) & (df['ROE_TTM_2019'] >= k19) & (df['ROE_TTM_2018'] >= k18) &
            (df['ROE_TTM_2017'] >= k17) & (df['ROE_TTM_2016'] >= k16) & (df['ROE_TTM_2016'] >= k15)]
    return df

def get_average_5_roe(df, k=0.2):
    df['avg_5_ROE_TMM'] = (df['ROE_TTM_2020'] + df['ROE_TTM_2019'] + df['ROE_TTM_2018'] + df['ROE_TTM_2017'] + df['ROE_TTM_2016'])/5
    df = df[(df['avg_5_ROE_TMM'] >= k)]
    return df

def get_peg(df):
    df = df[(df['PEG'] <= 0.9) & (df['PEG'] > 0) & (df['g3'] > 0)]  # g3 大于0防止都是负数的ST股
    df = df[(df['净利润2020'] >= df['净利润2019']) & (df['净利润2019'] >= df['净利润2018']) & (df['净利润2018'] >= df['净利润2017']) & (df['净利润2017'] >= df['净利润2016'])]  # 每年递增
    return df
##############################################################
c = ['公司', 'ROE_TTM_2020', 'ROE_TTM_2019', 'ROE_TTM_2018', 'ROE_TTM_2017', 'ROE_TTM_2016']
roe_5_20 = get_roe(df,  k20=0.2, k19=0.2, k18=0.2, k17=0.2, k16=0.2,)   # 5年都大于20%
roe_5_15 = get_roe(df,  k20=0.15, k19=0.15, k18=0.15, k17=0.15, k16=0.15,)   # 5年都大于15%
roe_5_15_a = roe_5_15.drop(labels=roe_5_20.index, axis=0)  # 排除roe_5_20的

roe_5_10 = get_roe(df,  k20=0.10, k19=0.10, k18=0.10, k17=0.10, k16=0.10,)   # 5年都大于10%
roe_5_10_a = roe_5_10.drop(labels=roe_5_15.index, axis=0)  # 排除roe_5_15的

peg = get_peg(df)
peg_roe_5 = get_peg(roe_5_10)
peg_roe_5_15 = get_peg(roe_5_15)

writer = pd.ExcelWriter('test.xlsx')
roe_5_20.to_excel(writer, 'roe_5_20', index=None)
roe_5_15_a.to_excel(writer, 'roe_5_15', index=None)
roe_5_10_a.to_excel(writer, 'roe_5_10', index=None)

peg_roe_5.to_excel(writer, 'peg_roe_5', index=None)
peg_roe_5_15.to_excel(writer, 'peg_roe_5_15', index=None)
peg.to_excel(writer, 'peg', index=None)
df.to_excel(writer, 'df', index=None)

writer.save()
