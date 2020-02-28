#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2020/2/12-11:28
# @Author : Ryuchen
# @Site : https://ryuchen.github.io
# @File : __main__.py
# @Desc : 
# ==================================================
import ujson
import gevent
import requests

from gevent.pool import Pool

from apps.periodic.base import BaseTask
from contrib.mysql.tables.proxy import Proxy


class TaskProxy(BaseTask):

    name = "task_proxy"

    upstream = "https://www.freeip.top/api/proxy_ips"

    def __init__(self):
        # 50 is your pool size
        self.concurrent = int(self.options.get("concurrent", 5))
        self.geventpool = Pool(self.concurrent)

    def fetch(self, params):
        try:
            from gevent import monkey
            monkey.patch_socket()  # 引入猴子补丁
            response = requests.get(url=self.upstream, params=params, timeout=5.0)
            return response.content
        except requests.exceptions.ReadTimeout:
            return {}

    def run(self, *args, **kwargs):
        template = {
            "isp": "联通",  # 网络服务商
            "country": "中国",  # IP address 所属国家
            "order_by": "created_at",  # speed:响应速度, validated_at:最新校验时间, created_at:存活时间
            "order_rule": "ASC"  # DESC:降序 ASC:升序
        }
        tasks = [self.geventpool.spawn(self.fetch, {**{"page": page}, **template}) for page in range(1, self.concurrent + 1)]
        results = gevent.joinall(tasks)
        for _ in results:
            try:
                message = ujson.loads(_.value)
                for _ in message.get('data', {}).get("data", []):
                    uid = _.get('unique_id', '')
                    ping = _.get('speed', 8)
                    host = _.get('ip', '')
                    port = _.get('port', 0)
                    proto = _.get('protocol', 'http')
                    proxy = Proxy(uid, host, port, proto, ping)
                    self.db_session.add(proxy)
                    self.db_session.commit()
            except ValueError:
                pass
