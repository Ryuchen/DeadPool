#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2019-04-10 09:56 
# @Author : ryuchen
# @Site :  
# @File : rlogs.py
# @Desc : 
# ==================================================
import time

from elasticsearch_dsl import Document, Date, Keyword


class RawLogs(Document):
    task_name = Keyword()
    timestamp = Date(format="strict_date_optional_time||epoch_millis")
    start_time = Date(format="strict_date_optional_time||epoch_millis")
    end_time = Date(format="strict_date_optional_time||epoch_millis")

    class Index:
        name = "rlogs"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "refresh_interval": "5s"
        }


    def save(self, **kwargs):
        # assign now if no timestamp given
        if not self.timestamp:
            self.timestamp = int(time.time()*1000)
        return super(RawLogs, self).save(**kwargs)
