#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2020/2/17-16:25
# @Author : Ryuchen
# @Site : https://ryuchen.github.io
# @File : pipline
# @Desc : 
# ==================================================
from celery.task import Task


class TmallPipeline(Task):

    # 负责将抽取后的信息进行存储的模块
    def run(self, *args, **kwargs):
        pass