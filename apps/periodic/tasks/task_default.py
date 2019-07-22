#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2019-04-14 10:34 
# @Author : ryuchen
# @Site :  
# @File : task_default.py 
# @Desc : 
# ==================================================
from __future__ import print_function
from __future__ import absolute_import

from celery.schedules import crontab

from apps.periodic.bases.AggTaskBase import PeriodicTask


class TaskDefault(PeriodicTask):
    # The necessary task configurations
    name = "task_default"
    run_every = crontab(minute="*")
