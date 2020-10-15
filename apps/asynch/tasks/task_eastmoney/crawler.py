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
from requests import adapters
from celery.utils.log import get_task_logger

from deadpool.celery import app


logger = get_task_logger(__name__)


@app.task
def crawler(jobs, **kwargs):
    # the requests targets
    # if not crawl targets drop this job
    if not jobs:
        return False

    cookies = kwargs.get('cookies')
    useragent = kwargs.get('useragent')

    # pass the selenium user-agent & cookies to request session
    s = requests.Session()
    # setup pool size due to
    # https://laike9m.com/blog/requests-secret-pool_connections-and-pool_maxsize,89/
    a = requests.adapters.HTTPAdapter(pool_connections=10, pool_maxsize=10, max_retries=3)
    s.mount('http://', a)
    s.mount('https://', a)
    s.headers.update({"user-agent": useragent})
    for cookie in cookies:
        s.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])

    # config options
    proxy = kwargs.get('proxy', None)

    proxies = {"http": proxy, "https": proxy} if proxy else {}

    results = []

    # due to aliyun server network limit so no use for aiohttp
    for _ in jobs:
        try:
            res = requests.get(_["target"], proxies=proxies, verify=False, timeout=3)
            res.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            logger.warning(f"{_['target']} Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            logger.warning(f"{_['target']} Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            logger.warning(f"{_['target']} Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            logger.warning(f"{_['target']} OOps: Something Else", err)
        else:
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, 'html.parser')
            _['body'] = str(soup.find("div", class_="newsContent"))
            results.append(_)

    return results
