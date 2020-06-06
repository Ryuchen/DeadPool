#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2020/2/17-16:27
# @Author : Ryuchen
# @Site : https://ryuchen.github.io
# @File : middleware
# @Desc : 
# ==================================================
from bs4 import BeautifulSoup
from celery.utils.log import get_task_logger
from deadpool.celery import app

logger = get_task_logger(__name__)


@app.task
def middleware(context, **kwargs):

    doc_type = kwargs.get('doc_type')
    source_link = kwargs.get('target')

    info = {}
    # 负责对每个爬取的页面进行信息抽取和清理的模块
    soup = BeautifulSoup(context, 'html.parser')

    if soup:
        # parse the body context which information we need to store.
        news_title = soup.h1.string
        news_post_time = soup.find("div", class_="time").string
        news_post_source = soup.find("div", class_="source data-source").attrs.get("data-source")
        news_content = soup.find("div", id="ContentBody").get_text()

        info = {
            "type": doc_type,
            "link": source_link,
            "title": news_title,
            "post_time": news_post_time,
            "post_source": news_post_source,
            "content": news_content
        }

    return info
