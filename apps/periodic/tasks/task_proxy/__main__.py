#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2020/2/12-11:28
# @Author : Ryuchen
# @Site : https://ryuchen.github.io
# @File : __main__.py
# @Desc : 
# ==================================================
import json
import eventlet
import requests

from sqlalchemy import exc

from apps.periodic.base import BaseTask
from contrib.mysql.tables.proxy import Proxy

eventlet.import_patched('requests')


class TaskProxy(BaseTask):

    name = "task_proxy"

    upstream = "https://www.freeip.top/api/proxy_ips"

    def __init__(self):
        # 50 is your pool size
        self.concurrent = int(self.options.get("concurrent", 5))
        self.greenpool = eventlet.GreenPool(size=self.concurrent)

    def fetch(self, params):
        try:
            response = requests.get(self.upstream, params)
            return response.json()
        except json.decoder.JSONDecodeError:
            return {}

    def insert_proxy(self, proxy):
        try:
            self.db_session.add(proxy)
            self.db_session.commit()
        except exc.IntegrityError:
            self.db_session.rollback()

    def run(self, *args, **kwargs):
        template = {
            # "isp": "联通",  # 网络服务商
            "country": "中国",  # IP address 所属国家
            "order_by": "created_at",  # speed:响应速度, validated_at:最新校验时间, created_at:存活时间
            "order_rule": "ASC"  # DESC:降序 ASC:升序
        }
        results = self.greenpool.imap(self.fetch, [{**{"page": page}, **template} for page in range(1, self.concurrent + 1)])
        self.greenpool.waitall()
        for message in results:
            try:
                for _ in message.get('data', {}).get("data", []):
                    uid = _.get('unique_id', '')
                    ping = _.get('speed', 8)
                    host = _.get('ip', '')
                    port = _.get('port', 0)
                    proto = _.get('protocol', 'http')
                    self.insert_proxy(Proxy(uid, host, port, proto, ping))
            except (ValueError, TypeError):
                pass
