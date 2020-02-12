#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2020/2/11-14:04
# @Author : Ryuchen
# @Site : https://ryuchen.github.io
# @File : network
# @Desc : 
# ==================================================
import uuid
import socket


def mac():
    """
    获取本机mac地址
    :return:
    """
    return uuid.UUID(int=uuid.getnode()).hex[-12:]


def hostname():
    """
    获取本机主机名称
    :return:
    """
    return socket.getfqdn(socket.gethostname())


def hostaddr():
    """
    获取当前联网的IP地址
    :return:
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('114.114.114.114', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip