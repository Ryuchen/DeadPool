#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2020/2/11-10:53
# @Author : Ryuchen
# @Site : https://ryuchen.github.io
# @File : base.py
# @Desc : 
# ==================================================
import datetime

from celery import Task

from sqlalchemy import exc
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

from common.settings import Settings
from common.plugins.human.notify import ServerChanNotify
from contrib.mysql.tables import Proxy


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
        self.use_proxy = self.options.get("proxy", False)

        # Resume section
        self.use_resume = self.options.get("resume", False)

        # Storage section
        self.storage_opt = self.options.get("storage", {"module": "FileStorage", "path": ""})

        # Keywords section
        self.targets = [x for x in self.options.get("keyword", [])]

        # Web browser default value
        self.browser, self.wait = None, None

    @classmethod
    def register(cls, app):
        cls.bind(app)

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
        options.add_argument('--no-sandbox')  # 让Chrome在root权限下跑
        options.add_argument('--disable-dev-shm-usage')
        self.browser = webdriver.Chrome(executable_path=Settings.search_config("settings|driver"), options=options)
        # self.browser.maximize_window()  # 设置窗口最大化
        self.wait = WebDriverWait(self.browser, 60)  # 设置一个智能等待为2秒

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

    # 获取代理
    def proxy(self):
        """
        By default it will use the author define proxy database, you can overwrite it in each task.
        get a valuable ip proxy address for crawler pages
        :return:
        """
        session = self._app._session_pool.get("mysql")()
        try:
            result = session.query(Proxy).order_by(Proxy.used_at.asc()).with_for_update().first()
            # this row is now locked
            result.used_at = datetime.datetime.utcnow()
            session.add(result)
            session.commit()
            # this row is now unlocked
            return "{0}://{1}:{2}".format(result.proto, result.host, result.port)
        except exc.ProgrammingError:
            session.rollback()
            return ""

    # 发送通知
    @staticmethod
    def notify(title, message):
        """
        :return:
        """
        notify = ServerChanNotify()
        res = notify.push_text(text=f"{title}", desp=message)
        return res

    # 爬取目标数据
    def run(self, *args, **kwargs):
        """
        the main function to start crawler jobs.
        :param args:
        :param kwargs:
        :return:
        """
        raise NotImplementedError
