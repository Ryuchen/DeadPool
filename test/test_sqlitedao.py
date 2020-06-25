#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2020/6/11-09:03
# @Author : Ryuchen
# @Site : https://ryuchen.github.io
# @File : test_sqlitedao
# @Desc :
# ==================================================
import sqlite3

if __name__ == '__main__':
    conn = sqlite3.connect("./test.db3")

    # 创建表结构
    create_sql = "create table if not exists eastmoney(id integer primary key autoincrement, source varchar(512))"
    c = conn.cursor()
    c.execute(create_sql)
    conn.commit()

    # 插入数据
    select_sql = "select source from eastmoney"
    c = conn.cursor()
    rows = c.execute(select_sql)
    for row in rows:
        print(row["source"])
    conn.commit()

    # 选取数据
    insert_sql = "insert into eastmoney(source) values ()"
    c = conn.cursor()
    c.execute(insert_sql)
    conn.commit()