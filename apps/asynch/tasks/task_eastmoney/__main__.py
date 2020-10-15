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
import time

from retry import retry
from urllib import parse
from bs4 import BeautifulSoup
from celery.utils.log import get_task_logger

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException

from apps.asynch.base import BaseTask
from common.sqlitedao import SQLiteDao
from common.settings import RESULT_ROOT


from .crawler import crawler
from .middleware import middleware
from .pipeline import pipeline

logger = get_task_logger(__name__)


class TaskEastmoney(BaseTask):

    name = "task_eastmoney"

    login_url = ''  # 东方财富的登录地址
    target_url = 'http://so.eastmoney.com'  # 爬取的目标地址

    def __init__(self):
        super(TaskEastmoney, self).__init__()
        self.current_page = 1
        # 目前已知的东方财富网的新闻类型
        # http://finance.eastmoney.com 财经新闻
        # http://futures.eastmoney.com 期货新闻
        # http://global.eastmoney.com 全球新闻
        # http://forex.eastmoney.com 外汇新闻
        # http://stock.eastmoney.com 股票新闻
        # http://fund.eastmoney.com 基金新闻
        self.types = {
            "finance.eastmoney.com": "finance",
            "futures.eastmoney.com": "futures",
            "global.eastmoney.com": "global",
            "forex.eastmoney.com": "forex",
            "stock.eastmoney.com": "stock",
            "fund.eastmoney.com": "fund"
        }
        self.sqlite = SQLiteDao(os.path.join(RESULT_ROOT, f"{self.name}.db3"))

    def login(self):
        pass

    def prev(self):
        prev_button = self.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'div.page-group > ul.clearflaot > li:first-child')
        ))
        prev_button.click()
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.module-news-list > .news-item')))
        return BeautifulSoup(self.browser.page_source, 'html.parser')

    @retry(TimeoutException, tries=3, delay=1, jitter=1)
    def next(self):
        next_button = self.wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'div.page-group > ul.clearflaot > li:last-child')
        ))
        next_button.click()
        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.module-news-list > .news-item')))
        return BeautifulSoup(self.browser.page_source, 'html.parser')

    def run(self, *args, **kwargs):
        try:
            # for setup website browser driver
            self.setup()
            # for whether login on this website
            if self.need_login:
                self.login()

            # for whether resume last crawl status
            if self.use_resume:
                self.resume(tname="eastmoney")
        except WebDriverException as e:
            self.notify(f"[{self.name}]", "**Spider task init failed~**")
            logger.error(f"爬取任务启动失败【WebDriverException】: {e.stacktrace}")

            # 结束任务，将不再继续执行下面的任务
            return

        for _ in self.targets:
            try:
                # in eastmoney the time search order is "sortfiled=4"
                uri = "news/s?keyword={0}&pageindex={1}&sortfiled=4".format(_, self.current_page)
                condition = (By.CSS_SELECTOR, '.module-news-list > .news-item')
                self.fetch(url=os.path.join(self.target_url, uri), condition=condition)
            except TimeoutException as e:
                self.notify(f"[{self.name}]", "**Spider task find no targets~**")
                logger.error(f"爬取任务搜寻失败【TimeoutException】: {e.stacktrace}")
            else:
                # Get the selenium cookies and user-agent for later use
                cookies = self.browser.get_cookies()
                useragent = self.browser.execute_script("return navigator.userAgent")

                bs4source = BeautifulSoup(self.browser.page_source, 'html.parser')

                # 查看是否存在下一页按钮
                while bs4source.find("li", string="下一页"):
                    # Each page we use one proxy address for our task: for example
                    # of course you can use proxy address for each target.
                    if self.use_proxy:
                        kwargs = {"proxy": self.proxy()}

                    # the common kwargs
                    kwargs.update({
                        "cookies": cookies,
                        "useragent": useragent,
                        "storage": self.storage_opt,
                        "name": self.name
                    })
                    # search all news item at current page
                    news_items = bs4source.find_all("div", class_="news-item")

                    jobs = []
                    for item in news_items:
                        item_news_href = item.find("div", class_="link").get_text()
                        job = {
                            "target": item_news_href,
                        }
                        if os.path.basename(item_news_href) not in self.bloomfilter:
                            parser_result = parse.urlparse(item_news_href)
                            job["doc_type"] = self.types[parser_result.netloc] if parser_result.netloc in self.types.keys() else "other"
                            jobs.append(job)
                        else:
                            logger.info(f"已经爬取过的URL: {item_news_href}")

                    if jobs:
                        chain = crawler.s(jobs, **kwargs) | middleware.s() | pipeline.s(**kwargs)
                        chain()

                    try:
                        # save all current page items goto next page (here to reduce the frequency because i'm using my laptop)
                        bs4source = self.next()
                    except TimeoutException as e:
                        self.notify(f"[{self.name}]", "**Spider task find no targets~**")
                        logger.error(f"爬取任务加载失败【TimeoutException】: {e.stacktrace}")
                        break
                    else:
                        time.sleep(10)
