#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2020-11-06 23:08:40
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: tasks.py


import os
import importlib

from datacenter.configs import DefaultConfig


class InitTasks(object):
    def __init__(self):
        """
        初始化定时任务
        """
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        for module in DefaultConfig.MODULES:
            if os.path.exists(os.path.join(BASE_DIR, '{}/tasks.py'.format(module))):
                app_router = importlib.import_module('{}.tasks'.format(module))
                try:
                    for i in dir(app_router):
                        if i.startswith("task_"):
                            task_func = getattr(app_router, i)
                            task_func()
                except:
                    pass

