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

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

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
        self.current_page = 2020

    def login(self):
        pass

    def resume(self):
        pass

    def prev(self):
        prev_button = self.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'div.page-group > ul.clearflaot > li:first-child')
        ))
        prev_button.click()

    def next(self):
        next_button = self.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'div.page-group > ul.clearflaot > li:last-child')
        ))
        next_button.click()

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
            uri = "news/s?keyword={0}&pageindex={1}&sortfiled=4".format(_, self.current_page)
            self.browser.get(os.path.join(self.target_url, uri))
            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.module-news-list > .news-item')))

            # Get the selenium cookies and user-agent for later use
            # TODO: add the cookie into the task cookie pool as backend update scheduler
            # cookies = self.browser.get_cookies()
            # print(cookies)
            user_agent = self.browser.execute_script("return navigator.userAgent")

            bs4source = BeautifulSoup(self.browser.page_source, 'html.parser')

            # Get the pages total news count
            # 东方财富网的新闻统计不准确
            # total_count = bs4source.find("div", class_="search-result").find("div", class_="count").string
            # total_count = int(total_count.replace(",", "")[5:-1])

            # 查看是否存在下一页按钮
            while bs4source.find("li", string="下一页"):
                # search all news item at current page
                news_items = bs4source.find_all("div", class_="news-item")
                for item in news_items:
                    item_news_href = item.find("div", class_="link").get_text()
                    kwargs = {
                        "useragent": user_agent,
                        "target": item_news_href,
                    }
                    chain = crawler.s(**kwargs) | middleware.s() | pipeline.s(self.name, self.storage_opt)
                    chain()
                # save all current page items goto next page (here to reduce the frequency because i'm using my laptop)
                self.next()
                bs4source = BeautifulSoup(self.browser.page_source, 'html.parser')
