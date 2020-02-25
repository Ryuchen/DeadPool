#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2020/2/18-15:34
# @Author : Ryuchen
# @Site : https://ryuchen.github.io
# @File : filestorage
# @Desc : 
# ==================================================
import os

from common.settings import RESULT_ROOT


class FileStorage:

    def __init__(self, task, path):
        if not path:
            self.storage = os.path.join(RESULT_ROOT, task)
        else:
            self.storage = path

        # 创建存储结果的路径
        if not os.path.exists(self.storage):
            os.makedirs(self.storage)

    def save(self):
        """
        保存
        :return:
        """
        pass

    def load(self):
        """
        加载
        :return:
        """
        pass

    def pack(self):
        """
        打包
        :return:
        """
        pass
