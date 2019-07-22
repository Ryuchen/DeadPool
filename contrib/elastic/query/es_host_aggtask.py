#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2019-04-10 17:26 
# @Author : ryuchen
# @Site :  
# @File : es_host_aggtask.py 
# @Desc : 
# ==================================================
from __future__ import absolute_import
from elasticsearch_dsl import Search, UpdateByQuery

from contrib.elastic.base import ElasticBase
from contrib.elastic.indices.host_aggtask import AggTaskLog


class ESHostAggTask(ElasticBase):

    def __init__(self):
        """
        @comment: 事件追溯
        """
        super(ESHostAggTask, self).__init__()
        self.prefix = AggTaskLog.Index.name

    def exist(self):
        return self.es_client.indices.exist(index=self.indices)

    def delete(self):
        self.es_client.indices.delete(index=self.indices, ignore=[400, 404])

    def search(self, params):
        s = Search(using=self.es_client, index=self.indices)
        s = s.from_dict({
            "query": params.get("query") if params.get("query") else {},
            "aggs": params.get("aggs") if params.get("aggs") else {},
            "sort": params.get("sort") if params.get("sort") else []
        })
        if params.get("source"):
            s = s.source(
                include=params.get("source", {}).get("include") if params.get("source", {}).get("include") else ['*'],
                exclude=params.get("source", {}).get("exclude") if params.get("source", {}).get("exclude") else ['*']
            )
        if params.get("size"):
            s = s[0:params.get("size")]
        response = s.execute()
        return response

    def update(self, params):
        ubq = UpdateByQuery(using=self.es_client, index=self.indices)

        update_dict = {
            "query": params.get("query") if params.get("query") else {},
            "script": params.get("script") if params.get("script") else {},
        }

        for key, value in params.get("update", {}).items():
            update_dict[key] = value

        ubq = ubq.update_from_dict(update_dict)
        response = ubq.execute()
        return response.to_dict()
