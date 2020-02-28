#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2019-04-09 20:13 
# @Author : ryuchen
# @Site :  
# @File : query.py
# @Desc : 
# ==================================================
from celery.utils.log import get_logger

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from common.settings import Settings
from common.singleton import singleton
from common.exceptions import SetupException

from .tables.base import Base

log = get_logger(__name__)


@singleton
class MysqlBase(object):

    def __init__(self):
        dsn_string = "mysql+mysqlconnector://{0}:{1}@{2}:{3}/{4}?charset=utf8"

        host = Settings.search_config("connection|mysql|host", "localhost")
        port = Settings.search_config("connection|mysql|port", 3306)

        username = Settings.search_config("connection|mysql|username", "username")
        password = Settings.search_config("connection|mysql|password", "password")

        database = Settings.search_config("connection|mysql|database", "deadpool")

        if {username, password} != {"username", "password"}:
            dsn_string = dsn_string.format(username, password, host, port, database)
        else:
            raise SetupException("You must setup properly MySQL username && password!")

        self._connect_database(dsn_string)

        # Disable SQL loggings. Turn it on for debugging.
        self.engine.echo = False

        # Connection timeout.
        self.engine.pool_timeout = Settings.search_config("connection|mysql|timeout", 60)

        self.create_tables()

        # Get db session.
        self.Session = sessionmaker(bind=self.engine)

    def _connect_database(self, connection_string):
        """Connect to a Database.
        @param connection_string: Connection string specifying the database
        """
        try:
            self.engine = create_engine(connection_string)
        except ImportError as e:
            lib = e.message.split()[-1]
            raise ImportError("Missing database driver by import %s (install with 'pip install %s')" % (lib, lib))

    def create_tables(self):
        """ Create tables."""
        try:
            Base.metadata.create_all(self.engine)
        except SQLAlchemyError as e:
            raise SetupException("Unable to create database: {0}".format(e))
