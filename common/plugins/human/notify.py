# !/usr/bin/env python
# -*- coding: utf-8 -*-
# ========================================================
# @Author: Ryuchen
# @Time: 2020/10/09-22:01
# @Site: https://ryuchen.github.io
# @Contact: chenhaom1993@hotmail.com
# @Copyright: Copyright (C) 2019-2020 Deadpool.
# ========================================================
"""
...
DocString Here
...
"""
from urllib import request
from urllib.parse import urlencode

from common.settings import Settings


class ServerChanNotify:

    def __init__(self):
        self.URL = Settings.search_config("settings|serverchan|url", "http://sc.ftqq.com/")
        self.KEY = Settings.search_config("settings|serverchan|key", "")

    def push_text(self, text="", desp=""):
        data = {
            "text": text,
            "desp": desp
        }
        url = f"{self.URL}{self.KEY}.send?{urlencode(data)}"
        req = request.Request(url)
        response = request.urlopen(req)
        return response.read().decode('utf-8')
