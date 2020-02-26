#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2020/2/11-10:53
# @Author : Ryuchen
# @Site : https://ryuchen.github.io
# @File : base.py
# @Desc : 
# ==================================================

from celery import Task


class BaseTask(Task):
    """Basic periodic task to store the common functions."""
    abstract = True  # This configuration to tell celery this is not the task.

    login_url = ""
    target_url = ""

    # 配置
    def setup(self):
        raise NotImplementedError

    # 登录
    def login(self):
        raise NotImplementedError

    # 断点续爬
    def resume(self):
        raise NotImplementedError

    # 爬取目标数据
    def run(self, *args, **kwargs):
        pass
