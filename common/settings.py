#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2019-04-09 14:56 
# @Author : ryuchen
# @Site :  
# @File : settings.py 
# @Desc : 
# ==================================================
import os
import yaml
import fcntl
import socket
import struct

_current_dir = os.path.abspath(os.path.dirname(__file__))
CONFIG_ROOT = os.path.normpath(os.path.join(_current_dir, "..", "config"))

settings = {
    "hostname": "default",
    "host_ip": "192.168.10.1",
    "version": "1.0.0",
    "connection": {
        "redis": {
            "host": "127.0.0.1",
            "port": 6379,
            "timeout": 60
        },
        "database": {
            "host": "127.0.0.1",
            "port": 3306,
            "dbname": "ATDKnowledge",
            "username": "root",
            "password": "12345678*",
            "timeout": 60
        },
        "elasticsearch": {
            "host": ["10.0.4.5:9200"],
            "timeout": 60
        }
    }
}


class Settings:
    """
    This function to protect the custom setting config does not influence the program successfully start up.
    """

    def __init__(self):
        self.default_path = os.path.join(CONFIG_ROOT, "config.yaml")
        self.default_config = {}

    def loading_default(self):
        """
        loading the settings of default.
        :return:
        """
        if os.path.exists(self.default_path):
            with open(self.default_path) as default_config:
                self.default_config = yaml.load(default_config, Loader=yaml.SafeLoader)

    def loading_settings(self):
        """
        To merge the settings into the main setting.
        :return:
        """
        self.loading_default()
        if self.default_config:
            settings.update(self.default_config)

        settings["hostname"] = socket.gethostname()

        try:
            manage_nic = os.environ["GEYE_MANAGENIC"]
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            host_ip = socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', manage_nic[:15]))[20:24])
        except:
            host_ip = settings["host_ip"]

        settings["host_ip"] = host_ip

    @staticmethod
    def get_settings():
        """
        To return the global settings
        :return:
        """
        return settings
