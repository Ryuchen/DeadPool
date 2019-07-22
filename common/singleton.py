#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2019-04-09 14:54 
# @Author : ryuchen
# @Site :  
# @File : singleton.py 
# @Desc : 
# ==================================================


def singleton(class_):
    instances = {}

    def _instance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return _instance
