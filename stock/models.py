from django.db import models


# Create your models here.

class StockData(models.Model):
    """基于vn.py的数据库设计的字段"""
    id = models.AutoField(primary_key=True)  # ID
    symbol = models.CharField(max_length=20)  # 代码
    exchange = models.CharField(max_length=2)  # 交易所
    datetime = models.DateTimeField()  # 时间
    interval = models.CharField(max_length=20)  # 级别
    volume = models.FloatField()  # 成交量
    open_interest = models.FloatField()  # 期货的空盘量
    open_price = models.FloatField()  # 开盘价
    high_price = models.FloatField()  # 最高价
    low_price = models.FloatField()  # 最低价
    close_price = models.FloatField()  # 收盘价

    class Meta:
        db_table = 'stock_data'
