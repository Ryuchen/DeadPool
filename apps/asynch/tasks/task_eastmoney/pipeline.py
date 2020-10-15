#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2020/2/17-16:27
# @Author : Ryuchen
# @Site : https://ryuchen.github.io
# @File : pipline
# @Desc : 
# ==================================================
import os

from deadpool.celery import app

from common.sqlitedao import SQLiteDao
from common.settings import RESULT_ROOT


@app.task
def pipeline(infos, **kwargs):
    options = kwargs.get('storage')
    name = kwargs.get('name')

    sqlite = SQLiteDao(os.path.join(RESULT_ROOT, f"{name}.db3"))

    # 负责将抽取后的信息进行存储的模块
    if options.get("module", "FileStorage") == "FileStorage":
        # 按配置加载的存储模块实例
        from common.plugins.storage.filestorage import FileStorage
        # 存储的磁盘地址
        storage = FileStorage(name, options.get("path", ""))
    else:
        # 按配置加载的存储模块实例
        from common.plugins.storage.mongostorage import MongoStorage
        # 存储的Collection
        storage = MongoStorage(name, options.get("collection", ""))

    if infos:
        for info in infos:
            if storage.add_one(collection=info['type'], document=info):
                insert_sql = "insert into eastmoney(source) values ('" + os.path.basename(info['link']) + "')"
                sqlite.insert_execute(insert_sql)
