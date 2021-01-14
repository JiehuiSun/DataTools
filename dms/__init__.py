#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-01-11 15:01:08
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: __init__.py


import time
import pymysql
from openpyxl import Workbook
from flask import current_app

from .models import TasksModel

from utils import valdate_code, save_file, send_mail


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
        cursor.execute(sql_obj.content)
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


def execute_task(task_id, is_show=False, is_export=False):
    """
    执行任务
    """
    task_obj = TasksModel.query.filter_by(id=task_id,
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
                  user_mail_list=project.user_mail_list,
                  attachments=[file_name])
        return True
