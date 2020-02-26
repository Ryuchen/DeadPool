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


class MongoStorage:

    def __init__(self, task, collection):
        host = Settings.search_config("connection|mongodb|host", "localhost")
        port = Settings.search_config("connection|mongodb|port", 27017)

        username = Settings.search_config("connection|mongodb|username", "username")
        password = Settings.search_config("connection|mongodb|password", "password")

        if {username, password} != {"username", "password"}:
            dsn_string = "mongodb://{0}:{1}@{2}:{3}".format(username, password, host, port)
        else:
            dsn_string = "mongodb://{0}:{1}".format(host, port)

        self.client = MongoClient(dsn_string)

        if not collection:
            # if not set the collection name we use the default task name as collection name
            self.db = self.client[task]
        else:
            self.db = self.client[collection]

    def add_one(self, document):
        """ 新增数据 """
        return self.db.students.insert_one(document)

    def add_many(self, documents):
        """ 新增多条数据 """
        return self.db.students.insert_many(documents)
