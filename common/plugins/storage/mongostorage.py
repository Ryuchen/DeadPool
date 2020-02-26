#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2020/2/25-13:58
# @Author : Ryuchen
# @Site : https://ryuchen.github.io
# @File : mongostorage
# @Desc : 
# ==================================================


class MongoStorage:

    def __init__(self, task, collection):
        if not collection:
            self.storage = None
        else:
            self.storage = None
