#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2019-04-09 17:51 
# @Author : ryuchen
# @Site :  
# @File : timetrans.py 
# @Desc : 
# ==================================================
import time
import calendar
import datetime

__all__ = ['get_now', 'get_utc_now',
           'datetime2string', 'string2datetime',
           'string2timestamp', 'timestamp2string','timestamp2datetime',
           'datetime2timestamp', 'today', 'get_month_days', 'get_first_day', 'get_last_day']


def get_now(time_zone=None):
    return datetime2string(datetime.datetime.now(tz=time_zone))


def get_utc_now():
    return datetime2string(datetime.datetime.utcnow())


# 把datetime转成字符串
def datetime2string(date2string, formation="%Y-%m-%d %H:%M:%S"):
    return date2string.strftime(formation)


# 把字符串转成datetime
def string2datetime(string2date, formation="%Y-%m-%d %H:%M:%S"):
    return datetime.datetime.strptime(string2date, formation)


# 把字符串转成时间戳形式
def string2timestamp(string2time):
    return time.mktime(string2datetime(string2time).timetuple())


# 把时间戳转成字符串形式
def timestamp2string(time2string, formation="%Y-%m-%d %H:%M:%S"):
    return time.strftime(formation, time.localtime(time2string))


# 把datetime类型转外时间戳形式
def datetime2timestamp(date2time):
    return time.mktime(date2time.timetuple())

def timestamp2datetime(timestamp_in_mill):
    return datetime.datetime.fromtimestamp(timestamp_in_mill/1000)

# 获取当天日期 2016-11-23
def today():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S").split(" ")[0]


# 获取当月的天数
def get_month_days(current_date):
    return calendar.monthrange(current_date.year, current_date.month)[1]


# 获取当月的第一天
def get_first_day(current_date):
    first_day = datetime.date(current_date.year, current_date.month, day=1)
    return datetime.datetime.combine(first_day, datetime.time.min)


# 获取当月的最后一天
def get_last_day(current_date):
    last_day = datetime.date(current_date.year, current_date.month, day=get_month_days(current_date))
    return datetime.datetime.combine(last_day, datetime.time.max)
