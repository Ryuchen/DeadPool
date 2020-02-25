#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2020/2/18-16:37
# @Author : Ryuchen
# @Site : https://ryuchen.github.io
# @File : sqlite
# @Desc : 
# ==================================================

import sqlite3


class SQLiteDao:

    def __init__(self, path):
        self.conn = sqlite3.connect(path)

    def create(self, table_ddl):
        """
        创建表
        :param table_ddl:
        :return:
        """
        c = self.conn.cursor()
        c.execute(table_ddl)
        self.conn.commit()

    def insert_execute(self, insert_sql):
        """
        插入记录
        :param insert_sql:
        :return:
        """
        try:
            c = self.conn.cursor()
            c.execute(insert_sql)
        finally:
            self.conn.commit()

    def update_execute(self, update_sql):
        """
        更新记录
        :param update_sql:
        :return:
        """
        try:
            c = self.conn.cursor()
            c.execute(update_sql)
        finally:
            self.conn.commit()

    def select_execute(self, select_sql):
        """
        查询记录
        :param select_sql:
        :return:
        """
        try:
            c = self.conn.cursor()
            cursor = c.execute(select_sql)
            return cursor
        finally:
            self.conn.commit()

    def __del__(self):
        self.conn.close()