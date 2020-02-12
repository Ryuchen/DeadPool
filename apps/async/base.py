#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2020/2/11-10:53
# @Author : Ryuchen
# @Site : https://ryuchen.github.io
# @File : base
# @Desc : 
# ==================================================
from celery.task import Task
from common.settings import Settings

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait


class BaseTask(Task):
    """Basic periodic task to store the common functions."""
    abstract = True  # This configuration to tell celery this is not the task.

    def __init__(self, username, password):
        self.username = username  # 登录账号
        self.password = password  # 登录密码

    def setup_browser(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 1})  # 2 不加载图片 | 1 加载图片
        options.add_experimental_option('excludeSwitches', ['enable-automation'])  # 设置为开发者模式，防止被各大网站识别出来使用了Selenium
        self.browser = webdriver.Chrome(executable_path=Settings.search_config("settings|driver"), options=options)  # 接收传入的 chromedriver地址 和设置好的 options
        self.browser.maximize_window()  # 设置窗口最大化
        self.wait = WebDriverWait(self.browser, 10)  # 设置一个智能等待为10秒

    def login(self):
        raise NotImplementedError

    # 获取总页面
    def getPageTotal(self):
        raise NotImplementedError

    # 切换页面进行数据加载
    def nextPage(self):
        raise NotImplementedError

    def prevPage(self):
        raise NotImplementedError

    # 爬取目标数据
    def crawlTargets(self):
        raise NotImplementedError

    def run(self, *args, **kwargs):
        pass
