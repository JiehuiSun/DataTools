#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2020-11-06 23:57:59
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: tasks.py


from utils import tasks


@tasks(id='account.task_test', trigger='cron', hour=0, second=3, replace_existing=True)
def task_test():
    """
    定时任务测试示例

    注意事项:
        方法名必须已"task_"开头
        必须被utils.tasks装饰

    参数说明:
    注意: id以模块命名，避免模块间的冲突

        任务类型分cron/interval/date三种

        cron定时调度
        year (int|str) – 4位数年份
        month (int|str) – 月（1-12）
        day (int|str) – 日（1-31）
        week (int|str) – ISO week (1-53)
        day_of_week (int|str) – 工作日的编号或名称（0-6或周一、周二、周三、周四、周五、周六、周日）
        hour (int|str) – hour (0-23)
        minute (int|str) – minute (0-59)
        second (int|str) – second (0-59)
        start_date (datetime|str) – 最早可能触发的日期/时间（包括）
        end_date (datetime|str) – 最晚可能触发的日期/时间（包括）
        timezone (datetime.tzinfo|str) – 用于日期/时间计算的时区（默认为计划程序时区）

        interval间隔调度
        它的参数如下：
        weeks (int) – number of weeks to wait
        days (int) – number of days to wait
        hours (int) – number of hours to wait
        minutes (int) – number of minutes to wait
        seconds (int) – number of seconds to wait
        start_date (datetime|str) – 间隔计算的起点
        end_date (datetime|str) – 最晚可能触发的日期/时间
        timezone (datetime.tzinfo|str) – 用于日期/时间计算的时区

        date定时调度
        最基本的一种调度，作业只会执行一次。它的参数如下：
        run_date (datetime|str) – the date/time to run the job at
        timezone (datetime.tzinfo|str) – time zone for run_date if it doesn’t have one already

    """
    pass
