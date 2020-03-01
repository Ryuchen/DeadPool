#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2019-04-08 20:07 
# @Author : ryuchen
# @Site :  
# @File : settings.py 
# @Desc : 
# ==================================================
import os
import sys
import logging
import datetime
import importlib

from celery import Celery
from celery.signals import task_prerun
from celery.signals import task_success
from celery.signals import task_failure

from common.settings import Settings
from contrib.redis.base import RedisBase
from contrib.mysql.base import MysqlBase
from contrib.elastic.base import ElasticBase

log = logging.getLogger(__name__)

# We should append the current dir into our running path
# So that we can use find out tasks and register it
cur_dir = os.getcwd()
sys.path.append(cur_dir)
# Than our application will running in full mode

# Once, as part of application setup, during deploy/migrations:
# We need to setup the global default settings
Settings.loading_config()

# Initialise the celery redis connection
redis_host = Settings.search_config("connection|redis|host", "localhost")
redis_port = Settings.search_config("connection|redis|port", 6379)

redis_usr = Settings.search_config("connection|redis|username", "username")
redis_pwd = Settings.search_config("connection|redis|password", "password")

if {redis_usr, redis_pwd} == {"username", "password"}:
    broker = 'redis://{0}:{1}/3'.format(redis_host, redis_port)
    backend = 'redis://{0}:{1}/4'.format(redis_host, redis_port)
else:
    broker = 'redis://{0}:{1}@{2}:{3}/3'.format(redis_usr, redis_pwd, redis_host, redis_port)
    backend = 'redis://{0}:{1}@{2}:{3}/4'.format(redis_usr, redis_pwd, redis_host, redis_port)

app = Celery(main='deadpool', broker=broker, backend=backend)

# Optional configuration, see the application user guide.
# See more: https://docs.celeryproject.org/en/latest/userguide/configuration.html
app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=['json'],
    result_expires=3600,
    worker_concurrency=4
)


# When celery start to initialise need to load multiple database session to context.
@app.on_configure.connect
def setup_initialise(sender, **kwargs):
    try:
        # Initialise share session connection
        _session_pool = {
            "redis": RedisBase().Session,
            "mysql": MysqlBase().Session,
            "elastic": ElasticBase().Session
        }
        setattr(sender, "_session_pool", _session_pool)
        log.info("successes load backend session pool on deadpool app at on_configure.connect")
    except Exception as e:
        log.error(e)


# When celery after initialise we register our task into the celery.
@app.on_after_configure.connect
def setup_celery_tasks(sender, **kwargs):
    for task_name, task_option in Settings.jobs_config.get("jobs", {}).items():
        module_path = 'apps.{0}.tasks.{1}'.format(task_option.get("module"), task_name)
        try:
            ip_module = importlib.import_module(module_path)
            ip_module_class = getattr(ip_module, task_option.get("class"))
            ip_module_class.options = task_option.get("options")
            ip_module_class.register(app)
            task_instance = ip_module_class()
            sender.register_task(task_instance)
            log.info("successes load job task on deadpool app at on_after_configure.connect")
        except Exception as e:
            log.exception(e)


# When celery start the task, we need to tell it the last time running status.
# @task_prerun.connect
# def search_agg_task_log(signal, sender, *args, **kwargs):
#     # This is to set this time running clock(super precision)
#     running_time = datetime.datetime.now().replace(second=0, microsecond=0)
#     sender.request.kwargs = {
#         "datetime": running_time
#     }
#
#
# @task_success.connect
# def insert_agg_task_log(signal, sender, result, *args, **kwargs):
#     # Get last running time
#     log.info("signals received: %s" % sender.name)
#
#
# @task_failure.connect
# def record_agg_task_log(signal, sender, **kwargs):
#     # Get last running time
#     log.info("signals received: %s" % sender.name)


if __name__ == '__main__':
    app.start()
