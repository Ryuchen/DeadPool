#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2020/2/11-13:57
# @Author : Ryuchen
# @Site : https://ryuchen.github.io
# @File : eastmoney
# @Desc : 
# ==================================================
import os

from bs4 import BeautifulSoup

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from apps.asynch.base import BaseTask

from .crawler import crawler
from .middleware import middleware
from .pipeline import pipeline


class TaskEastmoney(BaseTask):
    name = "task_eastmoney"

    login_url = ''  # 东方财富的登录地址
    target_url = 'http://so.eastmoney.com'  # 爬取的目标地址

    def __init__(self):
        super(TaskEastmoney, self).__init__()

    def login(self):
        pass

    def resume(self):
        pass

    def run(self, *args, **kwargs):
        # for setup website browser driver
        self.setup()
        # for whether login on this website
        if self.need_login:
            self.login()
        # navigate to the target url
        self.browser.get(self.target_url)

        for _ in self.targets:
            # in eastmoney the time search order is "sortfiled=4"
            self.browser.get(os.path.join(self.target_url, "news/s?keyword={}&sortfiled=4".format(_)))
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.module-news-list > .news-item')))

            # Get the selenium cookies and user-agent for later use
            # TODO: add the cookie into the task cookie pool as backend update scheduler
            # cookies = self.browser.get_cookies()
            # print(cookies)
            user_agent = self.browser.execute_script("return navigator.userAgent")

            news_items = BeautifulSoup(self.browser.page_source, 'html.parser').find_all("div", class_="news-item", limit=1)
            for item in news_items:
                item_news_href = item.find("div", class_="link").get_text()
                kwargs = {
                    "useragent": user_agent,
                    "target": item_news_href,
                }
                chain = crawler.s(**kwargs) | middleware.s() | pipeline.s(self.name, self.storage_opt)
                chain()
