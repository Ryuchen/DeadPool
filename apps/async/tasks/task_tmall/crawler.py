#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2020/2/17-16:37
# @Author : Ryuchen
# @Site : https://ryuchen.github.io
# @File : crawler
# @Desc : 
# ==================================================
from celery.task import Task

class TmallCrawler(Task):

    def __init__(self, target):
        self.target = target

    # 负责爬取每一个页面
    def run(self, *args, **kwargs):
        document = ""
        return document