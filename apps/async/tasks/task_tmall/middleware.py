#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2020/2/17-16:25
# @Author : Ryuchen
# @Site : https://ryuchen.github.io
# @File : middleware
# @Desc : 
# ==================================================
from celery.task import Task

class TmallMiddleware(Task):

    # 负责对每个爬取的页面进行信息抽取和清理的模块
    def run(self, *args, **kwargs):
        pass