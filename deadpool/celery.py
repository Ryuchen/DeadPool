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
import glob
import hanlp
import pkuseg
import logging
import importlib

from celery import Celery

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
    # Initialise storage session connection
    try:
        _session_pool = {
            "redis": RedisBase().Session,
            "mysql": MysqlBase().Session,
            "elastic": ElasticBase().Session
        }
        setattr(sender, "_session_pool", _session_pool)
        log.info("successes load backend session pool on deadpool app at on_configure.connect")
    except Exception as e:
        log.error(e)

    # Initialise HanLP process pipelines
    try:
        tokenizer = hanlp.load('CTB6_CONVSEG')
        tagger = hanlp.load('CTB5_POS_RNN_FASTTEXT_ZH')
        syntactic_parser = hanlp.load('CTB7_BIAFFINE_DEP_ZH')
        semantic_parser = hanlp.load('SEMEVAL16_TEXT_BIAFFINE_ZH')
        _hanlp_pipeline = hanlp.pipeline() \
            .append(hanlp.utils.rules.split_sentence, output_key='sentences') \
            .append(tokenizer, output_key='tokens') \
            .append(tagger, output_key='part_of_speech_tags') \
            .append(syntactic_parser, input_key=('tokens', 'part_of_speech_tags'), output_key='syntactic_dependencies', conll=False) \
            .append(semantic_parser, input_key=('tokens', 'part_of_speech_tags'), output_key='semantic_dependencies', conll=False)
        setattr(sender, "_hanlp_pipeline", _hanlp_pipeline)
        log.info("successes load hanlp process pipeline on deadpool app at on_configure.connect")
    except Exception as e:
        log.error(e)

    # Initialise HanLP NER recognizer model
    try:
        # 加载模型
        _hanlp_ner_recognizer = hanlp.load(hanlp.pretrained.ner.MSRA_NER_BERT_BASE_ZH)
        setattr(sender, "_hanlp_ner_recognizer", _hanlp_ner_recognizer)
        log.info("successes load hanlp NER recognizer model on deadpool app at on_configure.connect")
    except Exception as e:
        log.error(e)

    # Initialise pkuseg token segmentation toolkit
    try:
        # 加载模型
        _pkuseg_toolkit = pkuseg.pkuseg(user_dict=os.path.join(cur_dir, "data", "custom", 'pkuseg_user_dict.txt'), postag=True)
        setattr(sender, "_pkuseg_toolkit", _pkuseg_toolkit)
        log.info("successes load PKUseg token segmentation toolkit on deadpool app at on_configure.connect")
    except Exception as e:
        log.error(e)

    # Initialise stopwords for segmentation usage
    try:
        # cn_stopwords.txt    中文常用停用词
        # hit_stopwords.txt   哈工大停用词
        # scu_stopwords.txt   四川大学机器智能实验室停用词
        # baidu_stopwords.txt 百度停用词
        stopwords = []
        data_sets = glob.glob(os.path.join(cur_dir, 'data', 'stopwords', '*.txt'))
        for item in data_sets:
            with open(item, encoding="utf-8") as f:
                for line in f:
                    stopwords.append(line.strip())
        _stopwords = list(set(stopwords))
        setattr(sender, "_stopwords", _stopwords)
        log.info("successes load stopwords for segmentation usage on deadpool app at on_configure.connect")
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


if __name__ == '__main__':
    app.start()
