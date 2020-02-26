#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2020/2/17-16:27
# @Author : Ryuchen
# @Site : https://ryuchen.github.io
# @File : pipline
# @Desc : 
# ==================================================

from deadpool.celery import app


@app.task
def pipeline(info, name, options):
    # 负责将抽取后的信息进行存储的模块
    if options.get("module", "FileStorage") == "FileStorage":
        # 按配置加载的存储模块实例
        from common.plugins.storage.filestorage import FileStorage
        # 存储的磁盘地址
        storage = FileStorage(name, options.get("path", "")).storage
    else:
        # 按配置加载的存储模块实例
        from common.plugins.storage.mongostorage import MongoStorage
        # 存储的Collection
        storage = MongoStorage(name, options.get("collection", "")).storage

    print(info)
