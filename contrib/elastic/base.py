#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2019-04-09 14:54 
# @Author : ryuchen
# @Site :  
# @File : query.py
# @Desc : 
# ==================================================
import logging
import datetime

from elasticsearch import exceptions
from elasticsearch_dsl import connections

from common.settings import settings
from contrib.elastic.utils.agg_handler import AggResultHandler

log = logging.getLogger(__name__)


class ElasticBase(object):

    def __init__(self):
        try:
            self.es_client = connections.create_connection(
                hosts=settings.get("connection").get("elasticsearch").get("host"),
                timeout=settings.get("connection").get("elasticsearch").get("timeout"),
            )
        except exceptions.ElasticsearchException:
            self.es_client = None
        except exceptions.AuthenticationException:
            self.es_client = None
        except Exception:
            log.error("FIXME: An potential error occurred!", exc_info=True)
            self.es_client = None

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

    @staticmethod
    def result(search, fields, data_type="dicts"):
        """
        :param search:
        :param fields:
        :param data_type:
        :return: list[dict(), dict(), ...] or list[list[], list[], ...]
        """
        search_result = dict()
        if data_type == "lists":
            search_result = list()

        try:
            response = search.execute()
            if hasattr(response, "aggregations"):
                extraction = AggResultHandler(response.aggregations.to_dict(), fields)
                if data_type == "lists":
                    search_result = extraction.get_lists()
                else:
                    search_result = extraction.get_dicts()
        except AttributeError as attr:
            log.info("AttributeError: {0}".format(attr))
        except Exception:
            log.error("FIXME: An potential error occurred!", exc_info=True)
        return search_result
