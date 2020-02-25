#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2020/2/12-14:30
# @Author : Ryuchen
# @Site : https://ryuchen.github.io
# @File : base.py
# @Desc : 
# ==================================================

import redis
import socket

from common.settings import Settings
from common.singleton import singleton


@singleton
class RedisBase(object):

    def __init__(self):
        redis_setting = dict(
            host=Settings.search_config("connection|redis|host", "127.0.0.1"),
            port=Settings.search_config("connection|redis|port", 6379),
            db=Settings.search_config("connection|redis|database", 0),
            socket_keepalive=True,
            socket_keepalive_options={socket.TCP_KEEPIDLE: 60, socket.TCP_KEEPINTVL: 30, socket.TCP_KEEPCNT: 3}
        )
        redis_usr = Settings.search_config("connection|redis|username", "username")
        redis_pwd = Settings.search_config("connection|redis|password", "password")

        if { redis_usr, redis_pwd } != { "username", "password" }:
            redis_setting.update({
                "username": redis_usr,
                "password": redis_pwd
            })

        self.Session = redis.Redis(connection_pool=redis.ConnectionPool(**redis_setting))
