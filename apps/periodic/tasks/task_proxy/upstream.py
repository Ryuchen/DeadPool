#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2020/3/7-13:26
# @Author : Ryuchen
# @Site : https://ryuchen.github.io
# @File : freeip
# @Desc : 
# ==================================================
import os
import json
import random
import eventlet
import requests

from deadpool.celery import app
from celery.utils.log import get_task_logger

eventlet.import_patched('requests')

logger = get_task_logger(__name__)


@app.task
def freeip(**kwargs):
    upstream = "https://www.freeip.top/api/proxy_ips"
    greenpool = eventlet.GreenPool(size=5)

    template = {
        # "isp": "联通",  # 网络服务商
        # "country": "中国",  # IP address 所属国家
        "order_by": "created_at",  # speed:响应速度, validated_at:最新校验时间, created_at:存活时间
        "order_rule": "ASC"  # DESC:降序 ASC:升序
    }

    proxies = []

    def fetch(params):
        try:
            response = requests.get(upstream, params)
            return response.json()
        except json.decoder.JSONDecodeError:
            return {}

    results = greenpool.imap(fetch, [{**{"page": page}, **template} for page in range(1, 6)])
    greenpool.waitall()
    for message in results:
        try:
            for _ in message.get('data', {}).get("data", []):
                proxies.append({
                    "uid": _.get('unique_id', ''),
                    "proto": _.get('protocol', 'http'),
                    "host": _.get('ip', ''),
                    "port": _.get('port', 0),
                    "ping": _.get('speed', 8)
                })
            return proxies
        except (ValueError, TypeError):
            return []


@app.task
def xicidaili(**kwargs):
    proxies = []
    upstream = "https://www.xicidaili.com/wt/{}".format(str(random.randint(1, 10)))
    response = requests.get(upstream, timeout=0.5)
    content = response.text
    print(upstream)
    print(content)


@app.task
def kuaidaili(**kwargs):
    proxies = []
    upstream = "https://www.kuaidaili.com/free/inha/{}/".format(str(random.randint(1, 10)))
    response = requests.get(upstream, timeout=0.5)
    content = response.text
    print(upstream)
    print(content)
