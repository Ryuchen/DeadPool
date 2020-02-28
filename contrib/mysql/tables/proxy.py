#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2020/2/28-15:28
# @Author : Ryuchen
# @Site : https://ryuchen.github.io
# @File : proxy
# @Desc : 
# ==================================================
import ujson

from sqlalchemy import String
from sqlalchemy import Column
from sqlalchemy import Integer

from .base import Base


class Proxy(Base):
    """Reputation file md5 tables"""
    __tablename__ = "proxy"

    uid = Column(String(64), primary_key=True, nullable=False, index=True)
    host = Column(String(24), index=True)
    port = Column(Integer, index=True)
    proto = Column(String(12), index=True)
    ping = Column(Integer, index=True)

    def __repr__(self):
        return "<Proxy('{0}://{1}:{2}')>".format(self.proto, self.host, self.port)

    def to_dict(self):
        """Converts object to dict.
        @return: dict
        """
        d = {}
        for column in self.__table__.columns:
            d[column.name] = getattr(self, column.name)
        return d

    def to_json(self):
        """Converts object to JSON.
        @return: JSON data
        """
        return ujson.dumps(self.to_dict())

    def __init__(self, uid, host, port, proto, ping):
        self.uid = uid
        self.host = host
        self.port = port
        self.proto = proto
        self.ping = ping
