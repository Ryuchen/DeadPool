#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2020/2/12-10:26
# @Author : Ryuchen
# @Site : https://ryuchen.github.io
# @File : test_settings
# @Desc : 
# ==================================================

from common.settings import Settings


if __name__ == '__main__':
    # Once, as part of application setup, during deploy/migrations:
    # We need to setup the global default settings
    Settings.loading_config()

    print(Settings.default_config)

    # Initialise the celery redis connection
    redis_host = Settings.search_config("connection|redis|host", "localhost")
    redis_port = Settings.search_config("connection|redis|port", 6379)

    redis_usr = Settings.search_config("connection|redis|username", "username")
    redis_pwd = Settings.search_config("connection|redis|password", "password")

    print(redis_host, redis_port)
    print(redis_usr, redis_pwd)