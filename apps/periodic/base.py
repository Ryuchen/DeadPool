#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2019-04-15 16:40 
# @Author : ryuchen
# @Site :  
# @File : base.py 
# @Desc : 
# ==================================================

from celery import Task
from celery.schedules import crontab


class BaseTask(Task):
    """Basic periodic task to store the common functions."""
    abstract = True  # This configuration to tell celery this is not the task.

    compat = True
    options = None
    relative = False
    ignore_result = True

    # maybe use in Periodic Task session
    _db_session = None
    _rc_session = None
    _es_session = None

    @classmethod
    def register(cls, app):
        cls.run_every = crontab(minute=cls.options.get("crontab", "10"))
        app.conf.beat_schedule[cls.__name__] = {
            'task': cls.name,
            'schedule': cls.run_every,
            'args': (),
            'kwargs': {},
            'options': cls.options or {},
            'relative': cls.relative,
        }

    @property
    def rc_session(self):
        if self._rc_session is None:
            self._rc_session = self.app._session_pool.get("redis")()
        return self._rc_session

    @property
    def db_session(self):
        if self._db_session is None:
            self._db_session = self.app._session_pool.get("mysql")()
        return self._db_session

    @property
    def es_session(self):
        if self._es_session is None:
            self._es_session = self.app._session_pool.get("elastic")()
        return self._es_session

    def run(self, *args, **kwargs):
        raise NotImplementedError

    def after_return(self, *args, **kwargs):
        if self.db_session is not None:
            self.db_session.close()
