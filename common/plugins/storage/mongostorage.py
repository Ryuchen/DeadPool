#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2020/2/25-13:58
# @Author : Ryuchen
# @Site : https://ryuchen.github.io
# @File : mongostorage
# @Desc : 
# ==================================================
from pymongo import MongoClient

from common.settings import Settings

from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


class MongoStorage:

    def __init__(self, task, collection):
        host = Settings.search_config("connection|mongodb|host", "localhost")
        port = Settings.search_config("connection|mongodb|port", 27017)

        username = Settings.search_config("connection|mongodb|username", "username")
        password = Settings.search_config("connection|mongodb|password", "password")

        if username != "username" and password != "password":
            dsn_string = "mongodb://{0}:{1}@{2}:{3}".format(username, password, host, port)
        else:
            dsn_string = "mongodb://{0}:{1}".format(host, port)

        self.client = MongoClient(dsn_string)

        if not collection:
            # if not set the collection name we use the default task name as collection name
            self.db = self.client[task]
        else:
            self.db = self.client[collection]

    def add_one(self, collection, document):
        """ 新增数据 """
        try:
            self.db[collection].insert_one(document)
            return True
        except Exception as e:
            logger.warning("An exception occurred ::", e)
            return False

    def add_many(self, collection, documents):
        """ 新增多条数据 """
        try:
            self.db[collection].insert_many(documents)
            return True
        except Exception as e:
            logger.warning("An exception occurred ::", e)
            return False
