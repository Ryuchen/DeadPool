#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2019-04-15 16:40 
# @Author : ryuchen
# @Site :  
# @File : base.py 
# @Desc : 
# ==================================================
from __future__ import print_function
from __future__ import absolute_import

from celery.task import PeriodicTask
from contrib.elastic.base import ElasticBase


class BaseTask(PeriodicTask):
    """Basic periodic task to store the common functions."""
    abstract = True  # This configuration to tell celery this is not the task.

    _db_session = None
    _es_session = None

    @property
    def db_session(self):
        if self._db_session is None:
            self._db_session = self.app.databases_session_pool.get(self.options.get("database"))
        return self._db_session

    @property
    def es_session(self):
        if self._es_session is None:
            self._es_session = ElasticBase()
        return self._es_session

    def run(self, *args, **kwargs):
        raise NotImplementedError

    def after_return(self, *args, **kwargs):
        if self.db_session is not None:
            self.db_session.remove()
