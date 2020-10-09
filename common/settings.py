#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2019-04-09 14:56 
# @Author : ryuchen
# @Site : https://ryuchen.github.io
# @File : settings.py 
# @Desc : 
# ==================================================
import os
import yaml

from utils.loader import Loader
from utils.network import hostname
from utils.network import hostaddr
from utils.driver import loader_driver

_current_dir = os.path.abspath(os.path.dirname(__file__))
RESULT_ROOT = os.path.normpath(os.path.join(_current_dir, "..", "result"))
CONFIG_ROOT = os.path.normpath(os.path.join(_current_dir, "..", "config"))


class Settings:
    """
    This function to protect the custom setting config does not influence the program successfully start up.
    """
    default_path = os.path.join(CONFIG_ROOT, "config.yaml")
    default_config = {
        "hostname": "default",
        "hostaddr": "192.168.10.1",
        "version": "1.0.0",
        "connection": {
            "redis": {
                "host": "127.0.0.1",
                "port": 6379,
                "database": 0,
                "username": "username",
                "password": "password"
            },
            "mysql": {
                "host": "127.0.0.1",
                "port": 3306,
                "database": "deadpool",
                "username": "username",
                "password": "password",
                "timeout": 60
            },
            "mongodb": {
                "host": "127.0.0.1",
                "port": 27017,
                "username": "username",
                "password": "password",
            },
            "elasticsearch": {
                "host": "127.0.0.1",
                "port": 9200,
                "index": "rlogs",
                "username": "username",
                "password": "password"
            }
        },
        "settings": {
            "cluster": {
                "name": "deadpool",
                "node": {
                    "role": "master",
                    "name": "node-1"
                }
            },
            "storage": {
                "module": ["FileStorage", "MongoStorage"]
            },
            "serverchan": {
                "url": "",
                "key": ""
            }
        }
    }
    jobs_path = os.path.join(CONFIG_ROOT, "jobs.yaml")
    jobs_config = {
        # This will load up the config of jobs
    }

    @classmethod
    def loading_config(cls):
        """
        loading the settings of default.
        :return:
        """
        def merge_dict(target, source):
            for key, value in source.items():
                if isinstance(value, dict):
                    merge_dict(target.get(key, {}), value)
                else:
                    target[key] = value

        if os.path.exists(cls.default_path):
            with open(cls.default_path) as config:
                cls.settings_config = yaml.load(config, Loader=Loader)

        if cls.settings_config:
            merge_dict(cls.default_config, cls.settings_config)

        cls.default_config["hostname"] = hostname()

        try:
            cls.default_config["hostaddr"] = hostaddr()
        finally:
            cls.default_config["hostaddr"] = "127.0.0.1"

        cls.default_config["settings"]["driver"] = loader_driver()

        with open(cls.jobs_path) as config:
            cls.jobs_config = yaml.load(config, Loader=Loader)

    @classmethod
    def search_config(cls, pattern, default=""):
        """
        search the settings of default by pattern
        :param pattern:
        :param default:
        :return:
        """
        def search_pattern(target, section):
            section = target.get(section, {})
            return section

        try:
            settings = cls.default_config
            for _ in pattern.split("|"):
                settings = search_pattern(settings, _)
        except KeyError:
            settings = default

        return settings
