#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2020/2/28-15:28
# @Author : Ryuchen
# @Site : https://ryuchen.github.io
# @File : cookie
# @Desc :
# ==================================================
import ujson
import datetime

from sqlalchemy import String
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import DateTime

from .base import Base


class Cookie(Base):
    __tablename__ = "cookie"

    uid = Column(String(64), primary_key=True, nullable=False, index=True)
    jobs = Column(String(24), index=True)
    types = Column(Integer, index=True)
    valid = Column(Integer, index=True)
    used_at = Column(DateTime, index=True)
    insert_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)

    def __repr__(self):
        return "<Cookie('{0}://{1}:{2}')>".format(self.jobs, self.types, self.valid)

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

    def __init__(self, uid, jobs, types, valid):
        self.uid = uid
        self.jobs = jobs
        self.types = types
        self.valid = valid
