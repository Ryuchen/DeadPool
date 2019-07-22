#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2019-04-10 10:57 
# @Author : ryuchen
# @Site :  
# @File : ATDKnowledge.py 
# @Desc : 
# ==================================================
try:
    import ujson as json
except ImportError:
    import json

from datetime import datetime

from sqlalchemy import Text
from sqlalchemy import String
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class AlarmAggRule(Base):

    __tablename__ = "alarm_agg_rule"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=False)
    name_en = Column(String(255), nullable=False)
    name_cn = Column(String(255), nullable=False)
    reliability = Column(Integer, nullable=False)
    severity = Column(Integer, nullable=False)
    desc_en = Column(String(1024), nullable=False)
    desc_cn = Column(String(1024), nullable=False)
    suggestion_en = Column(Text(), nullable=True)
    suggestion_cn = Column(Text(), nullable=True)
    kid = Column(Integer, nullable=False)
    attack_result = Column(String(64), nullable=False)
    com_reliability = Column(Integer, nullable=False)
    query = Column(Text(), nullable=True)
    agg_keys = Column(String(255), nullable=False)
    classtype_id = Column(Integer, nullable=False)
    category_id = Column(Integer, nullable=False)
    status = Column(Integer, nullable=False)
    time_count = Column(Integer, nullable=False, default=2)
    s_com_reliability = Column(Integer, nullable=False)
    d_com_reliability = Column(Integer, nullable=False)
    classification = Column(String(255), nullable=False)
    template = Column(String(255), nullable=False)
    type = Column(Integer, nullable=False)

    def __repr__(self):
        return "<alarm_agg_rule ('{0}','{1}', '{2}')>".format(self.id, self.name, self.time_count)

    def to_dict(self):
        """Converts object to dict.
        @return: dict
        """
        d = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                d[column.name] = value.strftime("%Y-%m-%d %H:%M:%S")
            else:
                d[column.name] = value
        return d

    def to_json(self):
        """Converts object to JSON.
        @return: JSON data
        """
        return json.dumps(self.to_dict())

    def __init__(self, task):
        for column in self.__table__.columns:
            try:
                value = getattr(task, column.name)
            except AttributeError:
                value = getattr(task.file, column.name)
            setattr(self, column.name, value)


class AlarmCategory(Base):

    __tablename__ = "alarm_category"

    category_id = Column(Integer, primary_key=True, index=True)
    classtype_id = Column(Integer, index=True)
    category_name = Column(String(256), index=False)

    category_name_en = Column(String(512), nullable=False)
    category_name_cn = Column(String(512), nullable=False)
    severity = Column(Integer, nullable=False)
    attacker = Column(String(32), nullable=True)
    victim = Column(String(32), nullable=True)
    malscoure = Column(String(32), nullable=True)
    desc = Text()
    suggestion = Text()
    reference = Text()

    def __repr__(self):
        return "<alarm_category ('{0}','{1}')>".format(self.category_id, self.category_name)

    def to_dict(self):
        """Converts object to dict.
        @return: dict
        """
        d = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                d[column.name] = value.strftime("%Y-%m-%d %H:%M:%S")
            else:
                d[column.name] = value
        return d

    def to_json(self):
        """Converts object to JSON.
        @return: JSON data
        """
        return json.dumps(self.to_dict())

    def __init__(self, task):
        for column in self.__table__.columns:
            try:
                value = getattr(task, column.name)
            except AttributeError:
                value = getattr(task.file, column.name)
            setattr(self, column.name, value)


class AlarmClasstype(Base):

    __tablename__ = "alarm_classtype"

    classtype_id = Column(Integer, primary_key=True, index=True)
    classtype_name = Column(String(256), index=False)
    classtype_name_en = Column(String(512), nullable=False)
    classtype_name_cn = Column(String(512), nullable=False)

    def __repr__(self):
        return "<alarm_classtype ('{0}','{1}')>".format(self.classtype_id, self.classtype_name)

    def to_dict(self):
        """Converts object to dict.
        @return: dict
        """
        d = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                d[column.name] = value.strftime("%Y-%m-%d %H:%M:%S")
            else:
                d[column.name] = value
        return d

    def to_json(self):
        """Converts object to JSON.
        @return: JSON data
        """
        return json.dumps(self.to_dict())

    def __init__(self, task):
        for column in self.__table__.columns:
            try:
                value = getattr(task, column.name)
            except AttributeError:
                value = getattr(task.file, column.name)
            setattr(self, column.name, value)


class KillChain(Base):

    __tablename__ = "kill_chain"

    kid = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), nullable=False)
    name_cn = Column(String(64), nullable=False)

    def __repr__(self):
        return "<kill_chain ('{0}','{1}')>".format(self.kid, self.name)

    def to_dict(self):
        """Converts object to dict.
        @return: dict
        """
        d = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                d[column.name] = value.strftime("%Y-%m-%d %H:%M:%S")
            else:
                d[column.name] = value
        return d

    def to_json(self):
        """Converts object to JSON.
        @return: JSON data
        """
        return json.dumps(self.to_dict())

    def __init__(self, task):
        for column in self.__table__.columns:
            try:
                value = getattr(task, column.name)
            except AttributeError:
                value = getattr(task.file, column.name)
            setattr(self, column.name, value)
