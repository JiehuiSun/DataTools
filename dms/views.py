#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-01-11 17:53:07
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: views.py


import json
import time
import pymysql
import asyncio
import aiomysql
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook
from flask import make_response, send_file, current_app

from base import db, apscheduler, redis
from api import Api
from dms import add_task, execute_task
from dms.models import DatabaseModel, TasksModel, TasksLogModel
from utils import valdate_code, save_file, send_ding_errmsg, send_mail


class DatabasesView(Api):
    """
    数据库
    """
    NEED_LOGIN = True

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
    NEED_LOGIN = True

    async def connect_mysql(self, query_obj, sql_cmd, loop):
        '''
        连接数据库
        '''

        client = await aiomysql.connect(
            host=query_obj.host,
            user=query_obj.username,
            password=query_obj.password,
            db=query_obj.name,
            charset='utf8',
            loop=loop,
            read_default_file="/etc/my.cnf")

        async with aiomysql.cursors.SSCursor(client) as cursor:
            await cursor.execute(sql_cmd)

            data_list = []
            while True:
                row = await cursor.fetchone()
                if not row:
                    break
                data_list.append(list(row))

        if cursor.description:
            field_list = [i[0] for i in cursor.description]
        else:
            field_list = ["ok"]

        self.datas = {
            "field_list": field_list,
            "data_list": data_list
        }

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

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.connect_mysql(query_obj, self.data['sql_cmd'], loop))
        loop.close()

        return self.ret(template="sql_ret.html", data=self.datas)


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
            database=query_obj.name,
            read_default_file="/etc/my.cnf"
        )
        try:
            cursor = client.cursor()
            cursor.execute(self.data["sql_cmd"])
            cursor.close()
        except Exception as e:
            try:
                send_ding_errmsg(errmsg=str(e), params=self.data["sql_cmd"])
            except:
                pass
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

        ret_html = "<a href='/dms/v1/down_file/{0}'>点击下载</a>".format(file_name)
        return ret_html

    def get(self):
        resp = make_response(send_file("../ex_file/{0}".format(self.key)))
        resp.headers["Content-Disposition"] = 'attachment; filename=export_sql.xlsx'
        resp.headers['Content-Type'] = 'application/x-xlsx'
        return resp


class TasksView(Api):
    """
    任务
    """
    NEED_LOGIN = True

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
    NEED_LOGIN = True

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
            return self.start_task(task_obj)
        else:
            return self.stop_task(task_obj)

    def start_task(self, task_obj):
        """
        启动
        """
        current_app.logger.info(f"正在启动任务-{self.task_no}")
        task_params = dict()
        for k, v in self.params.items():
            if v is not None:
                task_params[k] = v

        # 注册到任务APS
        ret = add_task(self.task_no, trigger=task_obj.task_type, **task_params)
        jobs_list = apscheduler.get_jobs()
        for i in jobs_list:
            current_app.logger.info(f"启动后的任务有: {i}")
        if not ret:
            current_app.logger.info(f"任务-{self.task_no}启动失败")
            return self.ret(template="db_err.html", data={"errmsg": "任务不存在或已被删除/关闭"})
        else:
            current_app.logger.info(f"任务-{self.task_no}启动成功")
            task_obj.status = True
            db.session.commit()
            return self.ret(template="200.html", data={"errmsg": "任务开启成功", "next_url": "base./dms/v1/tasks/"})
        return

    def stop_task(self, task_obj):
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
        task_obj.status = False
        current_app.logger.info(f"任务-{self.task_no}关闭成功")
        db.session.commit()
        return self.ret(template="200.html", data={"errmsg": "任务关闭成功", "next_url": "base./dms/v1/tasks/"})


class DataBaseInitView(Api):
    """
    sql初始化
    """
    NEED_LOGIN = True

    def connect_mysql(self, query_obj, sql_cmd):
        '''
        连接数据库
        '''
        client = pymysql.connect(
            user=query_obj.username,
            password=query_obj.password,
            host=query_obj.host,
            port=query_obj.port,
            database=query_obj.name,
            read_default_file="/etc/my.cnf"
        )
        try:
            cursor = client.cursor()
            cursor.execute(sql_cmd)
            cursor.close()
        except Exception as e:
            current_app.logger.info(f"初始化数据库错误 ：{str(e)}")
            return self.ret(template="db_err.html", data={"errmsg": str(e)})
        client.close()
        return cursor

    def create_table_sql(self, query_obj, query_obj2):
        '''
        获取创建表语句
        '''
        # 获取本地 所有表名称
        sql_cmd = "show tables;"
        cursor = self.connect_mysql(query_obj2, sql_cmd)
        main_tables_list = [i[0] for i in cursor.fetchall()]
        if not main_tables_list:
            return self.ret(template="db_err.html", data={"errmsg": "be not in tables"})

        # 获取所有表名称
        sql_cmd = "show tables;"
        cursor = self.connect_mysql(query_obj, sql_cmd)
        tables = cursor.fetchall()
        if not tables:
            return self.ret(template="db_err.html", data={"errmsg": "be not in tables"})

        # 通过表名获取此表的建表语句
        create_table_list = list()
        for i in tables:
            i = i[0]
            if "-" in query_obj.name:
                query_obj_name = query_obj.name.replace("-", "_")
                new_table_name = f"{query_obj_name}_{i}"
            else:
                new_table_name = f"{query_obj.name}_{i}"

            # 查询表是否存在
            if new_table_name in main_tables_list:
                continue

            sql_cmd = f"show create table {i};"
            cursor = self.connect_mysql(query_obj, sql_cmd)
            create_table_sql = cursor.fetchall()[0][1]
            if not create_table_sql:
                continue
            try:
                charset = create_table_sql.split("CHARSET=")[1].split(" ")[0]
            except:
                charset = "utf8mb4"
            try:
                comment = create_table_sql.split('COMMENT="')[1].split('"')[0]
            except:
                comment = i

            create_table_sql = create_table_sql.replace(i, new_table_name)

            # 修改字符
            create_table_sql = create_table_sql.replace("general_ci", "0900_ai_ci")
            if "utf8mb4" not in create_table_sql:
                create_table_sql = create_table_sql.replace("utf8", "utf8mb4")

            # 处理创建语句
            creat_table_collocation = f"ENGINE=FEDERATED DEFAULT CHARSET={charset} COMMENT='{comment}' \
            CONNECTION='mysql://{query_obj.username}:{query_obj.password}@{query_obj.host}:{query_obj.port}/{query_obj.name}/{i}';"

            create_table = f'{create_table_sql.split("ENGINE")[0]}{creat_table_collocation}'
            create_table_list.append(create_table)

        return create_table_list

    def get(self):
        self.params_dict = {
            "db_id": "required str"
        }
        self.ver_params()

        query_obj = DatabaseModel.query.filter_by(id=self.data["db_id"], is_deleted=False).first()

        if not query_obj:
            return self.ret(template="db_err.html")

        query_obj2 = DatabaseModel.query.filter_by(comments='本机', is_deleted=False).first()
        # 获取该库的所有建表语句
        create_table_all_list = self.create_table_sql(query_obj, query_obj2)
        # 创建表
        if not query_obj2:
            return self.ret(template="db_err.html")

        for item in create_table_all_list:
            res = self.connect_mysql(query_obj2, item)
        return self.ret(template="sql_ret.html", data="ok")


class TasksLogView(Api):
    """
    任务日志
    """
    NEED_LOGIN = True

    def get(self):
        """
        列表
        """
        self.params_dict = {
            "task_name": "optional str",
            "task_no": "optional str",
            "recipient": "optional str",
            "status": "optional str",
            "handle_type": "optional str",
            "page_num": "optional str",
            "page_size": "optional str",
        }
        self.ver_params()

        try:
            page_size = int(self.data.get("page_size", 10))
            page_num = int(self.data.get("page_num", 1))
        except Exception as e:
            ret = {
                "errmsg": "参数错误"
            }
            return self.ret(template="404.html", data=ret)

        db_list = TasksLogModel.query.filter_by(is_deleted=False) \
            .join(TasksModel, TasksModel.id==TasksLogModel.task_no)
        if self.data.get("status"):
            if self.data["status"] == "1":
                is_successful = True
            else:
                is_successful = False
            db_list = db_list.filter(TasksLogModel.is_successful==is_successful)
        if self.data.get("handle_type"):
            db_list = db_list.filter(TasksLogModel.ex_type==self.data["handle_type"])

        if self.data.get("task_name"):
            db_list = db_list.filter(TasksModel.name.contains(self.data['task_name']))
        if self.data.get("task_no"):
            db_list = db_list.filter(TasksModel.task_no.contains(self.data['task_no']))
        if self.data.get("recipient"):
            db_list = db_list.filter(TasksLogModel.recipient.contains(self.data["recipient"]))

        total_size = db_list.count()
        db_list = db_list.order_by(TasksLogModel.dt_create.desc()) \
                        .limit(page_size).offset((page_num-1) * page_size).all()

        data_list = list()
        for i in db_list:
            data_dict = {
                "id": i.id,
                "task_no": i.task.task_no,
                "task_name": i.task.name,
                "dt_handled": i.dt_handled,
                "is_successful": i.is_successful,
                "return_info": i.return_info,
                "recipient": i.recipient,
                "ex_type": i.ex_type,
                "file_name": i.file_name,
            }

            data_list.append(data_dict)

        ret = {
            "data_list": data_list,
            "total_size": total_size,
            "page_num": page_num,
            "page_size": page_size,
            "params": self.data
        }
        return self.ret(template="tasks_log.html", data=ret)


class SendFileView(Api):
    """
    发送文件(应该做全局视图)
    """
    NEED_LOGIN = True

    def get(self):
        """
        """
        self.params_dict = {
            "log_id": "required str",
        }
        self.ver_params()

        task_log_obj = TasksLogModel.query.filter_by(id=self.data["log_id"]).one_or_none()
        if not task_log_obj:
            ret = {
                "errmsg": "参数错误"
            }
            return self.ret(template="404.html", data=ret)

        down_url = "http://{0}/dms/v1/down_file/{1}".format(
            current_app.config['MAIL_DOWN_HOST'] or redis.client['ServerHost'].decode(),
            task_log_obj.file_name
        )
        project = task_log_obj.task.project
        mail_content = f"需求备注: {project.comments or '无'}\n下载地址: {down_url}"

        send_mail(title=project.name,
                  content=mail_content,
                  user_mail_list=project.user_mail_list.split(","))
        ret = {
            "errmsg": "发送成功",
            "next_url": "base./dms/v1/task_log/"
        }
        return self.ret(template="200.html", data=ret)
