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

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

from common.settings import Settings


class BaseTask(Task):
    """Basic asynchronous task to implement the common functions."""

    abstract = True  # This configuration to tell celery this is not the task.

    # This is the basic params for the crawler jobs.
    login_url = ""
    target_url = ""

    # 初始化
    def __init__(self):
        """
        read the default task configurations for common usage.
        """
        # Login section
        login_attr = self.options.get("login", {})
        self.need_login = login_attr.get("enable", False)  # 判断是否需要登录

        """#####  login params section ####"""
        self.nickname = login_attr.get("nickname", "nickname")  # 通过此判断是否登录成功
        self.username = login_attr.get("username", "username")
        self.password = login_attr.get("password", "password")
        """#####  login params section ####"""

        # Proxy section
        self.proxy = self.options.get("proxy", False)

        # Storage section
        self.storage_opt = self.options.get("storage", {"module": "FileStorage", "path": ""})

        # Keywords section
        self.targets = [x for x in self.options.get("keyword", [])]

        # Web browser default value
        self.browser, self.wait = None, None

    # 配置
    def setup(self):
        """
        setup the browser options for the crawling jobs preparation.
        :return: browser && wait
        """
        options = webdriver.ChromeOptions()
        # 2 不加载图片 | 1 加载图片
        options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 1})
        # 设置为开发者模式，防止被各大网站识别出来使用了Selenium
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_argument('--headless')  # 无窗口话
        self.browser = webdriver.Chrome(executable_path=Settings.search_config("settings|driver"), options=options)
        # self.browser.maximize_window()  # 设置窗口最大化
        self.wait = WebDriverWait(self.browser, 5)  # 设置一个智能等待为2秒

    # 登录
    def login(self):
        """
        make the login operation in the special website.
        :return:
        """
        raise NotImplementedError

    # 断点续爬
    def resume(self):
        """
        if the crawler jobs support to resume from break point, use this function to read last break point.
        :return:
        """
        raise NotImplementedError

    # 向前一页
    def prev(self):
        """
        load the browser to the prev page of the current page.
        :return:
        """
        raise NotImplementedError

    # 向后一页
    def next(self):
        """
        load the browser to the next page of the current page.
        :return:
        """
        raise NotImplementedError

    # 爬取目标数据
    def run(self, *args, **kwargs):
        """
        the main function to start crawler jobs.
        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError
