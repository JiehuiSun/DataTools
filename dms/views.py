#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-01-11 17:53:07
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: views.py


import time
import pymysql
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook
from flask import make_response, send_file, current_app

from base import db, apscheduler
from api import Api
from dms import add_task, execute_task
from dms.models import DatabaseModel, TasksModel
from utils import valdate_code, save_file


class DatabasesView(Api):
    """
    数据库
    """
    NEED_LOGIN = False
    def get(self):
        """
        列表
        """
        db_list = DatabaseModel.query.filter_by(is_deleted=False) \
            .values("id", "name", "comments", "dt_create")

        data_list = list()
        for i in db_list:
            data_dict = {
                "id": i[0],
                "name": i[1],
                "comments": i[2],
                "dt_create": i[3],
            }

            data_list.append(data_dict)

        ret = {
            "data_list": data_list,
        }
        return self.ret(template="databases.html", data=ret)


class SQLWindowView(Api):
    """
    sql窗口
    """
    NEED_LOGIN = False
    def get(self):
        return self.ret(template="sql_window.html", data=self.data)

    def post(self):
        self.params_dict = {
            "sql_cmd": "required str",
            "db_id": "required str"
        }
        self.ver_params()

        query_obj = DatabaseModel.query.filter_by(id=self.data["db_id"],
                                                  is_deleted=False).first()

        if not query_obj:
            return self.ret(template="db_err.html")

        client = pymysql.connect(
            user=query_obj.username,
            password=query_obj.password,
            host=query_obj.host,
            port=query_obj.port,
            database=query_obj.name
        )
        try:
            cursor = client.cursor()
            cursor.execute(self.data["sql_cmd"])
            cursor.close()
        except Exception as e:
            client.close()
            return self.ret(template="db_err.html", data={"errmsg": str(e)})
        client.close()

        field_list = [i[0] for i in cursor.description]

        ret = {
            "field_list": field_list,
            "data_list": cursor.fetchall()
        }
        return self.ret(template="sql_ret.html", data=ret)


class ExportSQLView(Api):
    """
    导出
    """
    NEED_LOGIN = False
    def post(self):
        self.params_dict = {
            "sql_cmd": "required str",
            "db_id": "required str"
        }
        self.ver_params()

        query_obj = DatabaseModel.query.filter_by(id=self.data["db_id"],
                                                  is_deleted=False).first()

        if not query_obj:
            return self.ret(template="db_err.html")

        client = pymysql.connect(
            user=query_obj.username,
            password=query_obj.password,
            host=query_obj.host,
            port=query_obj.port,
            database=query_obj.name
        )
        try:
            cursor = client.cursor()
            cursor.execute(self.data["sql_cmd"])
            cursor.close()
        except Exception as e:
            return self.ret(template="db_err.html", data={"errmsg": str(e)})
        client.close()

        field_list = [i[0] for i in cursor.description]

        data = {
            "field_list": field_list,
            "data_list": cursor.fetchall()
        }

        file_name = "tmp-{0}-{1}.xlsx".format(str(int(time.time())), valdate_code())
        file_name = save_file(1, data, file_name)

        # content = save_virtual_workbook(wb)
        # resp = make_response(content)
        # resp.headers["Content-Disposition"] = 'attachment; filename=aaa.xlsx'
        # resp.headers['Content-Type'] = 'application/x-xlsx'

        ret_html = "<a href='{0}'>点击下载</a>".format(file_name)
        return ret_html

    def get(self):
        resp = make_response(send_file("../{0}".format(self.key)))
        resp.headers["Content-Disposition"] = 'attachment; filename=export_sql.xlsx'
        resp.headers['Content-Type'] = 'application/x-xlsx'
        return resp


class TasksView(Api):
    """
    任务
    """
    NEED_LOGIN = False
    def get(self):
        """
        列表
        """
        if self.data.get("id"):
            return self.query_task()
        if self.data.get("execute_id"):
            return execute_task(self.data["execute_id"], is_show=True)
        if self.data.get("export_id"):
            return execute_task(self.data["export_id"], is_export=True)

        task_list = TasksModel.query.filter_by(is_deleted=False) \
            .values("id", "task_no", "comments", "dt_create", "name")

        jobs = apscheduler.get_jobs()
        current_app.logger.info(f"当前任务有 ：{jobs}")
        job_id_list = [i.id for i in jobs]

        data_list = list()
        for i in task_list:
            data_dict = {
                "id": i[0],
                "task_no": i[1],
                "comments": i[2],
                "dt_create": i[3],
                "name": i[4],
            }

            if data_dict["task_no"] in job_id_list:
                data_dict["status"] = 1
            else:
                data_dict["status"] = 0

            data_list.append(data_dict)

        ret = {
            "data_list": data_list,
            "job_list": job_id_list
        }
        return self.ret(template="tasks.html", data=ret)

    def query_task(self):
        """
        详情
        """
        task_obj = TasksModel.query.filter_by(id=self.data["id"]).first()
        if not task_obj:
            return self.ret(template="db_err.html", data={"errmsg": "任务不存在或已被删除"})
        ret = {
            "id": task_obj.id,
            "task_no": task_obj.task_no,
            "name": task_obj.name,
            "project_id": task_obj.project_id,
            "project_name": task_obj.project,
            "comments": task_obj.comments,
            "year": task_obj.year,
            "month": task_obj.month,
            "day": task_obj.day,
            "week": task_obj.week,
            "day_of_week": task_obj.day_of_week,
            "hour": task_obj.hour,
            "minute": task_obj.minute,
            "second": task_obj.second
        }
        return self.ret(template="task.html", data={"task": ret})


class StartTaskView(Api):
    """
    启动关闭任务
    """
    NEED_LOGIN = False
    def get(self):
        """
        """
        current_app.logger.info("接口进入")
        jobs_list = apscheduler.get_jobs()
        for i in jobs_list:
            current_app.logger.info(f"当前存在的任务: {i}")
        self.params_dict = {
            "id": "required str",
            "status": "required str"
        }
        self.ver_params()

        task_obj = TasksModel.query.filter_by(task_no=self.data["id"]).first()
        if not task_obj:
            return self.ret(template="db_err.html", data={"errmsg": "任务不存在或已被删除"})

        self.task_no = task_obj.task_no
        self.task_obj = task_obj

        # TODO 任务设计类型(cron, interval, date) 目前只测试cron
        self.params = {
            "year": task_obj.year,
            "month": task_obj.month,
            "day": task_obj.day,
            "week": task_obj.week,
            "day_of_week": task_obj.day_of_week,
            "hour": task_obj.hour,
            "minute": task_obj.minute,
            "second": task_obj.second,
        }

        if self.data["status"] == "1":
            return self.start_task()
        else:
            return self.stop_task()

    def start_task(self):
        """
        启动
        """
        current_app.logger.info(f"正在启动任务-{self.task_no}")
        task_params = dict()
        for k, v in self.params.items():
            if v is not None:
                task_params[k] = v

        # 注册到任务APS
        ret = add_task(self.task_no, trigger=self.task_obj.task_type, **task_params)
        jobs_list = apscheduler.get_jobs()
        for i in jobs_list:
            current_app.logger.info(f"启动后的任务有: {i}")
        if not ret:
            current_app.logger.info(f"任务-{self.task_no}启动失败")
            return self.ret(template="db_err.html", data={"errmsg": "任务不存在或已被删除/关闭"})
        else:
            current_app.logger.info(f"任务-{self.task_no}启动成功")
            self.task_obj.status = True
            db.session.commit()
            return self.ret(template="200.html", data={"errmsg": "任务开启成功", "next_url": "base./dms/v1/tasks/"})
        return

    def stop_task(self):
        """
        关闭
        """
        current_app.logger.info(f"正在关闭任务-{self.task_no}")
        try:
            apscheduler.delete_job(self.task_no)
        except:
            current_app.logger.info(f"任务-{self.task_no}关闭失败")
            pass
        jobs_list = apscheduler.get_jobs()
        for i in jobs_list:
            current_app.logger.info(f"关闭后的任务有: {i}")
        self.task_obj.status = False
        current_app.logger.info(f"任务-{self.task_no}关闭成功")
        db.session.commit()
        return self.ret(template="200.html", data={"errmsg": "任务关闭成功", "next_url": "base./dms/v1/tasks/"})
