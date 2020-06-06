#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2020/2/26-14:28
# @Author : Ryuchen
# @Site : https://ryuchen.github.io
# @File : crawler.py
# @Desc : 
# ==================================================
import requests

from bs4 import BeautifulSoup
from celery.utils.log import get_task_logger

from deadpool.celery import app


logger = get_task_logger(__name__)


@app.task
def crawler(**kwargs):
    # config options
    cookies = kwargs.get('cookies')
    proxy = kwargs.get('proxy', None)
    # passing options
    useragent = kwargs.get('useragent')
    doc_type = kwargs.get('doc_type')
    target = kwargs.get('target')

    if not target or not useragent:
        return False

    headers = {
        "User-Agent": useragent
    }

    if proxy:
        proxies = {"http": proxy, "https": proxy}
        req = requests.get(target, headers=headers, proxies=proxies, verify=False)
    else:
        req = requests.get(target, headers=headers, verify=False)

    req.encoding = 'utf-8'
    soup = BeautifulSoup(req.text, 'html.parser')
    body = soup.find("div", class_="newsContent")
    return str(body)
