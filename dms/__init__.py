#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-01-11 15:01:08
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: __init__.py


import time
import json
import pymysql
import asyncio
import aiomysql
import datetime
import collections
from openpyxl import Workbook
from flask import current_app

from base import apscheduler, db

from dms.models import TasksModel, TasksLogModel

from utils import valdate_code, save_file, send_mail, Phone, last_month, last_week, send_ding_errmsg


async def async_mysql(
        host, port, user, password, db, sql=""
):
    try:
        pool = await aiomysql.create_pool(
            minsize=5,
            maxsize=50,
            host=host,
            port=port,
            user=user,
            password=password,
            db=db,
            autocommit=False)
    except Exception as a:
        return False, f'连接池创建失败-->{a}'

    try:
        conn = await pool.acquire()
        cur = await conn.cursor()
        await cur.execute(sql)
        field_list = [i[0] for i in cur.description]
        data_list = await cur.fetchall()
    except Exception as a:
        return False, f'查询数据失败-->{a}'

    cur.close()
    pool.release(conn)

    return True, {
        'field_list': field_list,
        'data_list': data_list,
    }


class DMS(object):
    """
    DMS
    """

    @classmethod
    def default_value(cls):
        dt_now = datetime.datetime.now()
        yesterday = dt_now - datetime.timedelta(days=1)

        to_day = "{0}-{1}-{2}".format(dt_now.year,
                                      dt_now.month,
                                      dt_now.day)

        yesterday = "{0}-{1}-{2}".format(yesterday.year,
                                         yesterday.month,
                                         yesterday.day)

        last_week_start, last_week_end = last_week()
        last_month_start, last_month_end = last_month()

        # SQL里的变量, 需要再加
        """
        SELECT id AS ID, name AS 名称 FROM table WHERE dt_created > {today_start} AND dt_created < {today_end};
        """
        SQL_VARIABLE = {
            "today_start": f"{to_day} 00:00:00",
            "today_end": f"{to_day} 23:59:59",
            "yesterday_start": f"{yesterday} 00:00:00",
            "yesterday_end": f"{yesterday} 23:59:59",
            "last_week_start": f"{last_week_start} 00:00:00",
            "last_week_end": f"{last_week_end} 23:59:59",
            "last_month_start": f"{last_month_start} 00:00:00",
            "last_month_end": f"{last_month_end} 23:59:59",
        }
        return SQL_VARIABLE

    @classmethod
    def default_functions(cls):
        func_dict = {
            "encrypt_phone": Phone.encrypt,
            "decrypt_phone": Phone.decrypt,
            "encryption_phone": Phone.encryption_phone,
        }

        return func_dict

    @classmethod
    def handle_sql(cls, sql):
        """
        处理sql
        """
        for k, v in cls.default_value().items():
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

    # 返回异步任务
    try:
        res = asyncio.run(async_mysql(
            host=db_obj.host,
            port=db_obj.port,
            db=db_obj.name,
            password=db_obj.password,
            user=db_obj.username,
            sql=DMS.handle_sql(sql_obj.content)
        ))
        return res
    except Exception as e:
        return False, f"sql{db_obj.id}的SQL执行错误: {str(e)}"


def handle_o2o_sql(sql_list):
    """
    处理一对一的sql
    """
    if not sql_list:
        return False, "未查询到sql"

    field_list = list()
    data_dict = collections.OrderedDict()

    for sql_obj in sql_list:
        db_obj = sql_obj.database
        client = pymysql.connect(
            user=db_obj.username,
            password=db_obj.password,
            host=db_obj.host,
            port=db_obj.port,
            database=db_obj.name,
            read_default_file="/etc/my.cnf"
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


def handle_o2m_sql(sql_list):
    """
    处理一对多的sql
    """
    if not sql_list:
        return False, "未查询到sql"

    field_list = list()
    data_list = list()
    data_dict = collections.OrderedDict()
    parent_list = collections.OrderedDict()
    sub_list = collections.OrderedDict()
    """
    parent_list/sub_list: {sql_id: {
                                field_list: (ID, 名字, ...),
                                special_field: {
                                    1: (id, name, ...),
                                    }
                                }
                            }
    """

    # 提前将有/无父级分离
    parent_sql_list = list()
    sub_sql_list = list()
    for sql_obj in sql_list:
        if sql_obj.parent:
            sub_sql_list.append(sql_obj.id)
        if not sql_obj.parent:
            parent_sql_list.append(sql_obj.id)

    for sql_obj in sql_list:
        db_obj = sql_obj.database
        client = pymysql.connect(
            user=db_obj.username,
            password=db_obj.password,
            host=db_obj.host,
            port=db_obj.port,
            database=db_obj.name,
            read_default_file="/etc/my.cnf"
        )

        try:
            cursor = client.cursor()
            sql_content = sql_obj.content
            if sql_obj.id in sub_sql_list:
                if "{id_list}" in sql_content:
                    s_params = {
                        "id_list": ",".join([str(i) for i in parent_list[sql_obj.parent_id]["data_list"].keys()])
                    }
                    sql_content = sql_content.format(**s_params)
            cursor.execute(DMS.handle_sql(sql_content))
            cursor.close()
        except Exception as e:
            errmsg = "sql{0}的SQL执行错误: {1}".format(db_obj.id, e)
            return False, errmsg
        client.close()

        _field_list = [i[0] for i in cursor.description]
        _data_list = cursor.fetchall()
        special_field = sql_obj.special_field

        if special_field not in _field_list:
            errmsg = "sql{0}的SQL没有唯一特殊字段".format(db_obj.id)
            return False, errmsg

        # 封装数据
        parent_sql = sql_obj.parent
        special_field_index = _field_list.index(special_field)
        p_data_list = collections.OrderedDict()
        for i in _data_list:
            if i[special_field_index] in p_data_list:
                p_data_list[i[special_field_index]].append(i)
            else:
                p_data_list[i[special_field_index]] = [i]

        # 有父级跟无父级单独存
        if parent_sql:
            sub_list[sql_obj.id] = {
                "field_list": _field_list,
                "data_list": p_data_list,
                "parent_id": parent_sql.id,
                "special_field_index": special_field_index
            }
        else:
            parent_list[sql_obj.id] = {
                "field_list": _field_list,
                "data_list": p_data_list
            }

    # 整合数据
    use_handle_data = dict()
    for _, i in sub_list.items():
        field_list += parent_list[i["parent_id"]]["field_list"]
        field_list += i["field_list"]

        for _, d in i["data_list"].items():
            for x in d:
                try:
                    for y in parent_list[i["parent_id"]]["data_list"][x[i["special_field_index"]]]:
                        all_data = y + x
                        data_list.append(all_data)
                        if i["parent_id"] in use_handle_data:
                            use_handle_data[i["parent_id"]].append(x[i["special_field_index"]])
                        else:
                            use_handle_data[i["parent_id"]] = [x[i["special_field_index"]]]
                except Exception as e:
                    pass

    for k, v in use_handle_data.items():
        not_handle_data = list(set(parent_list[k]["data_list"].keys()) - set(v))
        for i in not_handle_data:
            data_list.append(parent_list[k]["data_list"][i][0])

    ret = {
        "field_list": field_list,
        "data_list": data_list
    }

    return True, ret


def write_task_log(ex_type, task_obj, status, return_info=None, dt_handled=None, recipient=None):
    """
    更新任务日志(可写异步)
    """
    data_params = {
        "task_no": task_obj.task_no,
        "task": task_obj,
        "ex_type": ex_type,
        "is_successful": status,
    }
    if return_info:
        data_params["return_info"] = return_info
    if dt_handled:
        data_params["dt_handled"] = dt_handled
    if recipient:
        data_params["recipient"] = recipient
    db.session.add(TasksLogModel(**data_params))
    db.session.commit()


def execute_task(task_id, is_show=False, is_export=False):
    """
    执行任务
    parasm: task_id: TasksModel.task_no
    """
    dt_now = datetime.datetime.now()
    if is_show:
        ex_type = 1
    elif is_export:
        ex_type = 2
    else:
        ex_type = 3
    from application import app
    with app.app_context():
        current_app.logger.info(f"TaskID: {task_id}正在执行..")
        task_obj = TasksModel.query.filter_by(task_no=task_id,
                                              is_deleted=False).first()
        if not task_obj:
            errmsg = "TaskID: {0} 执行失败, ID错误或已被删除".format(task_id)
            try:
                send_ding_errmsg(errmsg=errmsg, task_id=task_id)
            except:
                pass
            current_app.logger.error(errmsg)
            if is_show:
                return {"template": "db_err.html", "data": {"errmsg": str(errmsg)}}
            return

        project = task_obj.project

        sql_list = project.sql_model.all()

        task_type = project.task_type

        tag = None
        data = dict()
        # 根据不同任务类型处理
        if task_type.type_id == 1:
            tag, data = handle_one_sql(sql_list)
        elif task_type.type_id == 2:
            tag, data = handle_o2o_sql(sql_list)
        elif task_type.type_id == 3:
            tag, data = handle_o2m_sql(sql_list)

        if not tag:
            try:
                send_ding_errmsg(errmsg=str(data), task_id=task_id, params=sql_list)
            except:
                pass
            current_app.logger.error(data)
            # 日志
            write_task_log(ex_type, task_obj, False, str(data), dt_now)
            if is_show:
                return {"template": "db_err.html", "data": {"errmsg": str(data)}}
            return

        # 处理自定义函数的字段(目前根据字段名做处理)
        need_handle_dict = dict()
        field_list = data["field_list"]
        for k, v in DMS.default_functions().items():
            for i in field_list:
                if k in i:
                    i_index = field_list.index(i)
                    i = i.split(k)[1].strip(" ").strip(":").strip(" ")
                    data["field_list"][i_index] = i
                    need_handle_dict[i_index] = v

        data_list = list(data["data_list"])
        for i_i, i in enumerate(data_list):
            for k, v in need_handle_dict.items():
                i = list(i)
                try:
                    i[k] = v(i[k])
                except:
                    pass
                data_list[i_i] = i

        data["data_list"] = data_list

        current_app.logger.info(f"TaskID: {task_id}执行完成..")

        if is_show:
            write_task_log(ex_type, task_obj, True, "查询成功", dt_now)
            return {"template": "sql_ret.html", "data": data}
        elif is_export:
            ret_msg = "执行成功"
            status = True
            try:
                file_name = "{0}-{1}.xlsx".format(str(int(time.time())), valdate_code())
                file_name = save_file(1, data, file_name)

                ret_html = "<a href='{0}'>点击下载</a>".format(file_name)
            except Exception as e:
                ret_msg = str(e)
                status = False
            write_task_log(ex_type, task_obj, status, ret_msg, dt_now)
            return ret_html
        else:
            ret_msg = "发送成功"
            status = True
            current_app.logger.info("准备发送邮件..")
            # 发送邮件
            try:
                file_name = "{0}-{1}-{2}.xlsx".format(project.name, str(int(time.time())), valdate_code())
                file_name = save_file(1, data, file_name)

                send_mail(title=project.name,
                        content=project.comments,
                        user_mail_list=project.user_mail_list.split(","),
                        attachments=[file_name])
                current_app.logger.info("发送成功..")
            except Exception as e:
                ret_msg = str(e)
                status = False
            write_task_log(ex_type, task_obj, status, ret_msg, dt_now, project.user_mail_list.split(","))
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
    from application import app
    with app.app_context():
        current_app.logger.info(f"增加任务, {task_id}")
        try:
            apscheduler.add_job(task_id, func=execute_task, args=(task_id,), **kwargs, max_instances=20)
        except Exception as e:
            try:
                send_ding_errmsg(errmsg=str(e), task_id=task_id, params=kwargs)
            except:
                pass
            current_app.logger.error(f"注册任务失败: {e}")
            return
        current_app.logger.info("任务增加成功")
        jobs_list = apscheduler.get_jobs()
        for i in jobs_list:
            current_app.logger.info(f"增加后的任务有: {i}")
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
    from application import app
    with app.app_context():
        jobs_list = apscheduler.get_jobs()
        for i in jobs_list:
            current_app.logger.info(f"初始化时存在的任务: {i}")

        task_list = all_tasks()
        for task_id, params in task_list.items():
            ret = add_task(task_id, **params)
            if not ret:
                current_app.logger.info(f"{task_id}注册失败")
            else:
                current_app.logger.info(f"{task_id}注册成功")

        return
