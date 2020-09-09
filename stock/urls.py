"""django_stock URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from stock import views

urlpatterns = [
    path(r'kline', views.kline),
    path(r'api/v1/get_kline_chart', views.v1_get_kline_chart),
    path(r'api/v1/update/', views.v1_update),    # stock数据更新：/stock/api/v1/update/?vt_symbol=000001.SZ&interval=D
    path(r'api/v1/all_update/', views.v1_all_update),   # 所有数据更新/stock/api/v1/all_update/?s=0&e=5000
]
