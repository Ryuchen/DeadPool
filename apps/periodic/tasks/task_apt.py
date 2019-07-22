#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Time : 2019-04-10 10:27 
# @Author : ryuchen
# @Site :  
# @File : task_apt.py
# @Desc : 
# ==================================================
from __future__ import print_function
from __future__ import absolute_import

from apps.periodic.bases.AggTaskBase import PeriodicTask
from celery.schedules import crontab


class TaskAPT(PeriodicTask):

    name = "task_apt"
    run_every = crontab(minute="*")
