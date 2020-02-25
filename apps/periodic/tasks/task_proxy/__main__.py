#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2020/2/12-11:28
# @Author : Ryuchen
# @Site : https://ryuchen.github.io
# @File : __main__.py
# @Desc : 
# ==================================================
from celery.schedules import crontab


from apps.periodic.base import BaseTask


class TaskProxy(BaseTask):

    name = "task_proxy"
    run_every = crontab(minute="*")

    def run(self, *args, **kwargs):
        pass