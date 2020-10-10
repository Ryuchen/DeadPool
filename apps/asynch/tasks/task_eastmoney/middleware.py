#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2020/2/17-16:27
# @Author : Ryuchen
# @Site : https://ryuchen.github.io
# @File : middleware
# @Desc : 
# ==================================================
import re

from bs4 import BeautifulSoup
from collections import Counter
from celery.utils.log import get_task_logger
from deadpool.celery import app

logger = get_task_logger(__name__)


@app.task
def middleware(context, **kwargs):
    _stopwords = app.__getattribute__("_stopwords")
    _pkuseg_toolkit = app.__getattribute__("_pkuseg_toolkit")
    _hanlp_pipeline = app.__getattribute__("_hanlp_pipeline")
    _hanlp_ner_recognizer = app.__getattribute__("_hanlp_ner_recognizer")

    doc_type = kwargs.get('doc_type')
    source_link = kwargs.get('target')

    info = {}
    # 负责对每个爬取的页面进行信息抽取和清理的模块
    soup = BeautifulSoup(context, 'html.parser')

    if soup:
        # parse the body context which information we need to store.
        news_title = soup.h1.string
        news_post_time = soup.find("div", class_="time").string
        if soup.find("div", class_="source data-source"):
            news_post_source = soup.find("div", class_="source data-source").attrs.get("data-source")
        else:
            news_post_source = ""
        news_content = soup.find("div", id="ContentBody").get_text()

        # 存放分词结果
        segments = []

        # 存放实体抽取结果
        entities = []

        info = {
            "type": doc_type,
            "link": source_link,
            "title": news_title,
            "post_time": news_post_time,
            "post_source": news_post_source,
            "content": news_content,
        }

        # # 去掉首尾的换行符和空格符
        # content = news_content.strip()
        # regex = r"((?P<title>原标题：.*)|)(?P<content>[\s\S]*)\((?P<author>责任编辑：[a-zA-Z0-9]+)\)$"
        # matches = re.match(regex, content)
        # if matches:
        #     content = matches.group("content").strip()
        #     # 匹配换行符
        #     paragraphs = content.split("\u3000\u3000")
        #     for paragraph in paragraphs:
        #         paragraph = paragraph.strip()
        #         if paragraph:
        #             # extract the sentences by "。|！|？"
        #             sentences = re.split(r"(。|！|？)", paragraph)
        #             sentences.append("")
        #             sentences = ["".join(i) for i in zip(sentences[0::2], sentences[1::2])]
        #             ready_sentences = []
        #             for sentence in sentences:
        #                 sentence = sentence.strip()
        #                 if sentence:
        #                     # after check the sentence output, we should remove some sentence
        #                     if all(item not in sentence for item in ["文章来源", "作者单位"]):
        #                         ready_sentences.append(list(sentence))
        #                         phrases = _pkuseg_toolkit.cut(sentence)
        #                         # 过滤停用词
        #                         for segment in phrases:
        #                             text = segment[0][0]
        #                             if text not in _stopwords:
        #                                 segments.append(segment)
        #             for item in _hanlp_ner_recognizer(ready_sentences):
        #                 if item:
        #                     entities.extend(item)
        #     info["pipeline"] = _hanlp_pipeline(content)
        # info["segments"] = list(Counter(segments))
        # info["entities"] = entities

    return info
