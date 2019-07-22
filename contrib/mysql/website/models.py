#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2019-04-14 10:00 
# @Author : ryuchen
# @Site :  
# @File : models.py 
# @Desc : 
# ==================================================

try:
    import ujson as json
except ImportError:
    import json

from datetime import datetime

from sqlalchemy import Text
from sqlalchemy import Float
from sqlalchemy import String
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class HostGroup(Base):

    __tablename__ = 'host_group'

    id = Column(Integer, primary_key=True, index=True)
    group_name = Column(String(255), nullable=True)
    group_cidr = Column(Text(), nullable=True)
    manager = Column(String(255), nullable=True)
    created = Column(DateTime, nullable=True, default=datetime.now)
    updated = Column(DateTime, nullable=True, default=datetime.now)

    def __repr__(self):
        return "<host_group ('{0}','{1}')>".format(self.id, self.group_name)

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


class HostType(Base):

    __tablename__ = 'host_type'

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(64), nullable=True)
    created = Column(DateTime, nullable=True, default=datetime.now)
    updated = Column(DateTime, nullable=True, default=datetime.now)

    def __repr__(self):
        return "<host_type ('{0}','{1}')>".format(self.id, self.type)

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


class DeviceType(Base):

    __tablename__ = 'device_type'

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(64), nullable=True)
    created = Column(DateTime, nullable=True, default=datetime.now)
    updated = Column(DateTime, nullable=True, default=datetime.now)
    parent_id = Column(Integer, nullable=False, default=0, index=True)

    def __repr__(self):
        return "<device_type ('{0}','{1}')>".format(self.id, self.type)

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


class Host(Base):

    __tablename__ = 'host'

    id = Column(Integer, primary_key=True, index=True)
    ip = Column(String(64), nullable=True)
    mac = Column(String(255), nullable=True)
    vendor = Column(String(255), nullable=True)
    hostname = Column(String(255), nullable=True)
    fqdns = Column(String(255), nullable=True)
    asset_value = Column(Integer, nullable=True)
    os = Column(String(255), nullable=True)
    group_id = Column(Integer, ForeignKey("host_group.id"))
    group = relationship("HostGroup")
    device_type_id = Column(Integer, ForeignKey("device_type.id"))
    device_type = relationship("DeviceType")
    asset_type_id = Column(Integer, ForeignKey("host_type.id"))
    asset_type = relationship("HostType")
    source_id = Column(String(16), nullable=True)
    come_from = Column(String(16), nullable=True)
    longitude = Column(Float, nullable=True)
    latitude = Column(Float, nullable=True)
    country = Column(String(64), nullable=True)
    country_code = Column(String(16), nullable=True)
    city = Column(String(64), nullable=True)
    owner = Column(String(64), nullable=True)
    descr = Column(String(255), nullable=True)
    created = Column(DateTime, nullable=True, default=datetime.now)
    updated = Column(DateTime, nullable=True, default=datetime.now)

    def __repr__(self):
        return "<host ('{0}','{1}', '{2}')>".format(self.id, self.ip, self.mac)

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


class BDEAssetsNetwork(Base):
    __tablename__ = "bde_assets_network"

    id = Column(Integer, primary_key=True, index=True)

    cidr = Column(String(172), nullable=True)
    device_type = Column(Integer, nullable=True)
    geo_location = Column(String(64), nullable=True)
    geo_city = Column(String(32), nullable=True)
    geo_country = Column(String(32), nullable=True)
    geo_country_code = Column(String(32), nullable=True)
    created = Column(DateTime, nullable=True, default=datetime.now)
    updated = Column(DateTime, nullable=True, default=datetime.now)

    def __repr__(self):
        return "<bde_assets_network ('{0}','{1}')>".format(self.id, self.cidr)

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
