from django.db import models

# Create your models here.

class TestData(models.Model):
    id = models.AutoField(primary_key=True)  #ID
    name = models.CharField(max_length=20)      #设备名称
    procurement_data = models.DateField(null=True)   # 采购时间
    production_data = models.DateField(null=True)   # 生产日期
    code = models.CharField(max_length=20)   # 设备编码
    department = models.CharField(max_length=20)     # 单位
    producers = models.CharField(max_length=50)  # 生产商
    speed = models.IntegerField()  # 速度

