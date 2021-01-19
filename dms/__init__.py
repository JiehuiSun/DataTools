#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-01-11 15:01:08
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: __init__.py


import time
import json
import pymysql
import datetime
import collections
from openpyxl import Workbook
from flask import current_app

from base import apscheduler

from dms.models import TasksModel

from utils import valdate_code, save_file, send_mail


class DMS(object):
    """
    DMS
    """
    dt_now = datetime.datetime.now()
    yesterday = dt_now - datetime.timedelta(days=1)

    to_day = "{0}-{1}-{2}".format(dt_now.year,
                                  dt_now.month,
                                  dt_now.day)

    yesterday = "{0}-{1}-{2}".format(yesterday.year,
                                     yesterday.month,
                                     yesterday.day)

    # SQL里的变量, 需要再加
    """
    SELECT id AS ID, name AS 名称 FROM table WHERE dt_created > {today_start} AND dt_created < {today_end};
    """
    SQL_VARIABLE = {
        "today_start": f"{to_day} 00:00:00",
        "today_end": f"{to_day} 23:59:59",
        "yesterday_start": f"{yesterday} 00:00:00",
        "yesterday_end": f"{yesterday} 23:59:59",
    }

    @classmethod
    def handle_sql(cls, sql):
        """
        处理sql
        """
        for k, v in cls.SQL_VARIABLE.items():
            r_k = "{" + k + "}"
            if r_k in sql:
                sql = sql.replace(r_k, v)

        return sql

    def fetch_all_to_dict(self, cursor):
        """
        sql结果集转dict
        """
        desc = [i[0] for i in cursor.description]
        result = [dict(zip(desc, col)) for col in cursor.fetchall()]
        return result


def handle_one_sql(sql_list):
    if not sql_list:
        return False, "未查询到sql"

    sql_obj = sql_list[0]
    db_obj = sql_obj.database
    client = pymysql.connect(
        user=db_obj.username,
        password=db_obj.password,
        host=db_obj.host,
        port=db_obj.port,
        database=db_obj.name
    )

    try:
        cursor = client.cursor()
        cursor.execute(DMS.handle_sql(sql_obj.content))
        cursor.close()
    except Exception as e:
        errmsg = "sql{0}的SQL执行错误: {1}".format(db_obj.id, e)
        return False, errmsg
    client.close()

    field_list = [i[0] for i in cursor.description]
    data_list = cursor.fetchall()

    ret = {
        "field_list": field_list,
        "data_list": data_list
    }

    return True, ret


def handle_O2O_sql(sql_list):
    """
    处理一对一的sql
    """
    if not sql_list:
        return False, "未查询到sql"

    field_list = list()
    data_list = list()
    data_dict = collections.OrderedDict()
    parent_id_list = list()

    for sql_obj in sql_list:
        db_obj = sql_obj.database
        client = pymysql.connect(
            user=db_obj.username,
            password=db_obj.password,
            host=db_obj.host,
            port=db_obj.port,
            database=db_obj.name
        )

        try:
            cursor = client.cursor()
            cursor.execute(DMS.handle_sql(sql_obj.content))
            cursor.close()
        except Exception as e:
            errmsg = "sql{0}的SQL执行错误: {1}".format(db_obj.id, e)
            return False, errmsg
        client.close()

        _field_list = [i[0] for i in cursor.description]
        _data_list = cursor.fetchall()
        special_field = sql_obj.special_field

        field_list += _field_list

        if special_field not in _field_list:
            errmsg = "sql{0}的SQL没有唯一特殊字段".format(db_obj.id)
            return False, errmsg

        special_field_index = _field_list.index(special_field)

        if not data_dict:
            for i in _data_list:
                data_dict[i[special_field_index]] = i
        else:
            for i in _data_list:
                # 一对一理论上讲，以主的记录为准
                try:
                    data_dict[i[special_field_index]] += i
                except:
                    pass

    ret = {
        "field_list": field_list,
        "data_list": data_dict.values()
    }

    return True, ret


def execute_task(task_id, is_show=False, is_export=False):
    """
    执行任务
    parasm: task_id: TasksModel.task_no
    """
    from application import app
    with app.app_context():
        print(f"TaskID: {task_id}正在执行..")
        task_obj = TasksModel.query.filter_by(task_no=task_id,
                                            is_deleted=False).first()
        if not task_obj:
            errmsg = "TaskID: {0} 执行失败, ID错误或已被删除".format(task_id)
            current_app.logger.error(errmsg)
            if is_show:
                return {"template": "db_err.html", "data": {"errmsg": str(errmsg)}}
            return

        project = task_obj.project

        sql_list = project.sql_model.all()

        task_type = project.task_type

        data = dict()
        # 根据不同任务类型处理
        if task_type.type_id == 1:
            tag, data = handle_one_sql(sql_list)
            if not tag:
                current_app.logger.error(data)
                if is_show:
                    return {"template": "db_err.html", "data": {"errmsg": str(data)}}
                return

        elif task_type.type_id == 2:
            tag, data = handle_O2O_sql(sql_list)
            if not tag:
                current_app.logger.error(data)
                if is_show:
                    return {"template": "db_err.html", "data": {"errmsg": str(data)}}
                return

        print(f"TaskID: {task_id}执行完成..")

        if is_show:
            return {"template": "sql_ret.html", "data": data}
        elif is_export:
            file_name = "{0}-{1}.xlsx".format(str(int(time.time())), valdate_code())
            file_name = save_file(1, data, file_name)

            ret_html = "<a href='{0}'>点击下载</a>".format(file_name)
            return ret_html
        else:
            # 发送邮件
            file_name = "{0}-{1}-{2}.xlsx".format(project.name,str(int(time.time())), valdate_code())
            file_name = save_file(1, data, file_name)

            send_mail(title=project.name,
                      content=project.comments,
                      user_mail_list=project.user_mail_list.split(","),
                      attachments=[file_name])
            return True


def del_task_job():
    """
    删除任务
    """
    pass


def add_task(task_id, **kwargs):
    """
    添加任务
    """
    try:
        apscheduler.add_job(task_id, func=execute_task, args=(task_id,), **kwargs)
    except Exception as e:
        current_app.logger.error(f"注册任务失败: {e}")
        return
    return True


def del_task(task_id, **kwargs):
    """
    删除任务
    """
    pass


def all_tasks():
    from application import app
    with app.app_context():
        task_obj_list = TasksModel.query.filter_by(is_deleted=False,
                                                   status=True).all()

        ret = dict()
        for task_obj in task_obj_list:
            _task_dict = {
                "year": task_obj.year,
                "month": task_obj.month,
                "day": task_obj.day,
                "week": task_obj.week,
                "day_of_week": task_obj.day_of_week,
                "hour": task_obj.hour,
                "minute": task_obj.minute,
                "second": task_obj.second,
            }

            task_dict = {
                "trigger": task_obj.task_type
            }
            for k, v in _task_dict.items():
                if v is not None:
                    task_dict[k] = v

            ret[task_obj.task_no] = task_dict

        return ret

def init_tasks():
    task_list = all_tasks()
    for task_id, params in task_list.items():
        ret = add_task(task_id, **params)
        if not ret:
            print(f"{task_id}注册失败")
        else:
            print(f"{task_id}注册成功")

    return
