#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2020/2/12-11:28
# @Author : Ryuchen
# @Site : https://ryuchen.github.io
# @File : __main__.py
# @Desc : 
# ==================================================
import eventlet
import datetime

from sqlalchemy import exc

from apps.periodic.base import BaseTask
from contrib.mysql.tables.proxy import Proxy

from .validator import validator
from .upstream import freeip, xicidaili, kuaidaili

eventlet.import_patched('requests')


class TaskProxy(BaseTask):

    name = "task_proxy"

    def __init__(self):
        self.expires = int(self.options.get("expire", 600))
        self.maximum = int(self.options.get("pool", {}).get("maximum", 60))
        self.minimum = int(self.options.get("pool", {}).get("minimum", 10))
        self.source = self.options.get("source", "freeip")

    def fetch_proxy(self):
        try:
            return self.db_session.query(Proxy).all()
        except:
            return []

    def delete_proxy(self, proxy):
        try:
            self.db_session.delete(proxy)
            self.db_session.commit()
        except:
            self.db_session.rollback()

    def insert_proxy(self, proxy):
        try:
            self.db_session.add(proxy)
            self.db_session.commit()
        except exc.IntegrityError:
            self.db_session.rollback()

    def run(self, *args, **kwargs):
        """
        先确定当前代理池里面的代理数量，然后逐个检测：
        1、使用过久进行删除
        2、无法使用的进行删除
        然后判断代理数量，当数量未到达最低阈值时，进行补充，补充到最大阈值时舍弃其余代理
        :param args:
        :param kwargs:
        :return:
        """
        if self.source == "freeip":
            task = freeip.apply_async((), retry=False)
        if self.source == "xicidaili":
            task = xicidaili.apply_async((), retry=False)
        if self.source == "kuaidaili":
            task = kuaidaili.apply_async((), retry=False)
        fresh_proxies = task.get()
        # available_proxy_count = 0
        # current_time = datetime.datetime.now()
        # current_proxies = self.fetch_proxy()
        # for item_proxy in current_proxies:
        #     insert_time = item_proxy.insert_at
        #     if (current_time - insert_time).seconds > self.expires:
        #         self.delete_proxy(item_proxy)
        #     else:
        #         task = validator.apply_async((item_proxy.proto, item_proxy.host, item_proxy.port), retry=False)
        #         valid_result = task.get()
        #         if not valid_result:
        #             self.delete_proxy(item_proxy)
        #         else:
        #             available_proxy_count += 1
        #
        # if available_proxy_count >= self.minimum:
        #     pass
        # else:
        #     lack_proxy_count = self.maximum - available_proxy_count
        #     if self.source == "freeip":
        #         task = freeip.apply_async((), retry=False)
        #     if self.source == "xicidaili":
        #         task = xicidaili.apply_async((), retry=False)
        #     if self.source == "kuaidaili":
        #         task = kuaidaili.apply_async((), retry=False)
        #     fresh_proxies = task.get()
        #     while lack_proxy_count >= 0:
        #         if fresh_proxies:
        #             new_proxy = fresh_proxies.pop()
        #             if new_proxy:
        #                 self.insert_proxy(Proxy(
        #                     new_proxy["uid"],
        #                     new_proxy["host"],
        #                     new_proxy["port"],
        #                     new_proxy["proto"],
        #                     new_proxy["ping"]
        #                 ))
        #                 lack_proxy_count -= 1
        #             else:
        #                 break
        #         else:
        #             break
