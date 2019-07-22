#!/usr/bin/python
# -*- coding: utf-8 -*-
# ==================================================
# File: task_risk_host
# Date: 2019/4/16
# Creator: chen
# Description: ...
# ==================================================
from __future__ import print_function
from __future__ import absolute_import

from celery.schedules import crontab

from apps.periodic.bases.AggRiskHostBase import PeriodicTask


class TaskRiskHost(PeriodicTask):
    # The necessary task configurations
    name = "task_risk_host"
    run_every = crontab(minute=[5, 15, 25, 35, 45, 55])
