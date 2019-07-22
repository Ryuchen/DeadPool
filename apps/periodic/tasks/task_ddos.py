#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2019-04-10 10:28 
# @Author : ryuchen
# @Site :  
# @File : task_ddos.py 
# @Desc : 
# ==================================================
from __future__ import print_function
from __future__ import absolute_import

from celery.schedules import crontab

from apps.periodic.bases.AggTaskBase import PeriodicTask


class TaskDDos(PeriodicTask):
    # The necessary task configurations
    name = "task_ddos"
    run_every = crontab(minute="*")
