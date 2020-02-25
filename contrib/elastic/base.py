#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2019-04-09 14:54 
# @Author : ryuchen
# @Site :  
# @File : query.py
# @Desc : 
# ==================================================
import datetime

from celery.utils.log import get_logger

from elasticsearch import exceptions
from elasticsearch_dsl import connections

from common.settings import Settings

log = get_logger(__name__)


class ElasticBase(object):

    def __init__(self):
        host = Settings.search_config("connection|elasticsearch|host", "127.0.0.1")
        port = Settings.search_config("connection|elasticsearch|port", 9200)

        try:
            self.Session = connections.create_connection(hosts=["{}:{}".format(host, port)])
        except exceptions.ElasticsearchException:
            self.Session = None
        except exceptions.AuthenticationException:
            self.Session = None
        except Exception:
            log.error("FIXME: An potential error occurred!", exc_info=True)
            self.Session = None

        self._prefix = ""
        self._indices = []

    @property
    def prefix(self):
        return self._prefix

    @prefix.setter
    def prefix(self, index_name):
        if '*' in index_name:
            self._prefix = index_name.replace('*', '-')
        else:
            self._prefix = index_name

    @property
    def indices(self):
        if not self._indices:
            return self.prefix + '*'
        return self._indices

    def gedices(self, start, end):
        """
        Generate indices depends on time range
        :param start: start time
        :param end: end time
        :return:
        """
        days = (end - start).days
        if days >= 365:
            for i in range(0, int(days / 365 + 1)):
                self._indices.append(self.prefix + "-" + (end - datetime.timedelta(days=365 * i)).strftime('%Y') + '*')
        elif days >= 31:
            for i in range(0, int(days / 31 + 1)):
                self._indices.append(self.prefix + "-" + (end - datetime.timedelta(days=31 * i)).strftime('%Y-%m') + '*')
        else:
            for i in range(0, days + 1):
                self._indices.append(self.prefix + "-" + (end - datetime.timedelta(days=i)).strftime('%Y-%m-%d') + '*')
