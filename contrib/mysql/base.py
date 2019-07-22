#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2019-04-09 20:13 
# @Author : ryuchen
# @Site :  
# @File : query.py
# @Desc : 
# ==================================================
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from common.settings import settings
from common.singleton import singleton


@singleton
class MysqlBase(object):

    def __init__(self, dsn):
        self._connect_database(dsn)

        # Disable SQL loggings. Turn it on for debugging.
        self.engine.echo = False

        # Connection timeout.
        if settings.get("connection").get("database").get("timeout"):
            self.engine.pool_timeout = settings.get("connection").get("database").get("timeout")
        else:
            self.engine.pool_timeout = 60

        # Get db session.
        self.Session = scoped_session(sessionmaker(bind=self.engine))

    def __del__(self):
        """ Disconnects pool. """
        self.engine.dispose()

    def _connect_database(self, connection_string):
        """Connect to a Database.
        @param connection_string: Connection string specifying the database
        """
        try:
            self.engine = create_engine(connection_string)
        except ImportError as e:
            lib = e.message.split()[-1]
            raise ImportError("Missing database driver by import %s (install with 'pip install %s')" % (lib, lib))
