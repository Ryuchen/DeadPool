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
def crawler(target, useragent):
    # cookies = kwargs.get('cookies')

    if not target or not useragent:
        return False

    headers = {
        "User-Agent": useragent
    }
    session = requests.session()
    req = session.get(target, headers=headers)
    # req = session.get(target, headers=headers, cookies=cookies)
    soup = BeautifulSoup(req.text, 'html.parser')
    body = soup.find("div", class_="newsContent")
    return str(body)
