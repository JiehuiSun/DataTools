
import time
import json
import random
import mimetypes
import requests
import pymysql
from openpyxl import Workbook
from flask import current_app
from flask_mail import Message

from .time_utils import *
from .phone import Phone


class Requests(object):
    """
    封装requests模块
    """
    @classmethod
    def handle_req(self, method, url, **kwargs):
        req = getattr(requests, method)
        if not req:
            return json.dumps({"errcode": 10000, "errmsg": "不支持的请求"})
        headers_dict = kwargs.get("headers", dict())
        if not headers_dict.get("X-MUMWAY-TRACEID"):
            from base import redis
            headers_dict["X-MUMWAY-TRACEID"] = redis.client.get("X-MUMWAY-TRACEID")

        kwargs["headers"] = headers_dict
        return req(url, **kwargs)

    @classmethod
    def get(self, url, params=None, **kwargs):
        return self.handle_req("get", url, params=params, **kwargs)

    @classmethod
    def post(self, url, data=None, json=None, **kwargs):
        return self.handle_req("post", url, data=data, json=json, **kwargs)

    @classmethod
    def put(self, url, data=None, **kwargs):
        return self.handle_req("put", url, data=data, **kwargs)

    @classmethod
    def delete(self, url, **kwargs):
        return self.handle_req("delete", url, **kwargs)

    @classmethod
    def options(self, url, **kwargs):
        return self.handle_req("delete", url, **kwargs)


class DBSql(object):
    """
    数据库相关
    """
    def __init__(self, db_name, limit=1000):
        self.limit = limit
        try:
            self.project_name = db_name
            self.db_host = current_app.config[f"{self.project_name}_DB_HOST"]
            self.db_user = current_app.config[f"{self.project_name}_DB_USERNAME"]
            self.db_pwd = current_app.config[f"{self.project_name}_DB_PASSEORD"]
            self.db_port = current_app.config.get(f"{self.project_name}_DB_PORT", 3306)
            self.db_name = current_app.config[f"{self.project_name}_DB_NAME"]
            self.project_name = db_name
        except Exception as e:
            current_app.logger.error(f">> 项目数据库配置错误: {e}")
            raise KeyError("项目数据库配置错误.. 配置示例: PROJECT_HOST")

        # 连接(目前都不做长连接)
        self.client = pymysql.connect(
            user=self.db_user,
            password=self.db_pwd,
            host=self.db_host,
            port=self.db_port,
            database=self.db_name
        )

        # 游标对象
        self.cursor = self.client.cursor()
        return

    def execute_sql(self, sql_text):
        """
        执行SQL
        """
        # 调用原生sql语句
        # 设置返回条数
        if "limit" not in sql_text:
            sql_text += f" limit {self.limit}"

        try:
            self.cursor.execute(sql_text)
            data_dict = self.fetch_all_to_dict(self.cursor)
        except Exception as e:
            try:
                send_ding_errmsg(errmsg=str(e), task_id=task_id, params=sql_text)
            except:
                pass
            current_app.logger.error(f">> Sql错误: {sql_text} \n {e}")
            raise SyntaxError(f"Sql错误.. {sql_text} \n {e}")

        return data_dict

    def fetch_all_to_dict(self, cursor):
        """
        sql结果集转dict
        """
        # 返回每个字段的属性(('id', 3, None, 11, 11, 0, False), ('name', 253, None, 120, 120, 0, True),)
        # 提取出id、name等
        desc = [i[0] for i in cursor.description]
        # 将desc和对应的col组合多个字典
        # 返回[{'name': '金牌月嫂', 'id': 2}],
        result = [dict(zip(desc, col)) for col in cursor.fetchall()]
        return result

    @property
    def host(self):
        return self.db_host

    @property
    def name(self):
        return self.db_name


class ConnectDBMetaClass(type):

    @property
    def mysql(self):
        for i in current_app.config:
            if "_DB_NAME" in i:
                setattr(self, i.rstrip("_DB_NAME").lower(), DBSql(i.rstrip("_DB_NAME")))
        return self


class ConnectDB(metaclass=ConnectDBMetaClass):
    """
    连接数据库

    import ConnectDB
    data = ConnectDB.mysql.project.execute_sql("select * from table")
    """
    pass


def send_mail(title: str, content: str, user_mail_list: list, attachments: list = None,
              html_content: str = None, bcc: list = None, send_date: str = None):
    params = {
        "subject": title,
        "recipients": user_mail_list,
        "body": content,
        "html": html_content,
        "sender": current_app.config["MAIL_USERNAME"],
        "bcc": bcc,
        # "attachments": attachments,
        "date": send_date,
    }

    msg = Message(**params)
    from application import app
    if attachments:
        for i in attachments:
            with app.open_resource(f"../ex_file/{i}") as fp:
                msg.attach(i.split("/")[-1], mimetypes.guess_type("aaa.txt")[0], fp.read())

    from base import mail
    mail.send(msg)


def tasks(**params):
    def outter(func):
        def wrapper(*args,**kwargs):
            res = func
            from base import apscheduler
            apscheduler.add_job(func=func, **params)
            return res
        return wrapper
    return outter


def valdate_code(num=8, only_num=False):
    """
    随机码
    """
    ret = str()
    for _ in range(num):
        random_num = random.randint(0, 9)
        if not only_num:
            alfa = chr(random.randint(97, 122))
            alfa2 = chr(random.randint(65, 90))
            random_num = random.choice([str(random_num), alfa, alfa2])
        ret = ret + random_num
    return ret


def save_xlsx_file(data, file_name, sheet_name="Sheet"):
    """
    """
    wb = Workbook()
    ws_list = wb.worksheets
    if ws_list:
        ws = ws_list[0]
    else:
        ws = wb.create_sheet(sheet_name)
    ws.append(data["field_list"])

    for i in data["data_list"]:
        try:
            ws.append(i)
        except:
            print(f"content err: {i}")
    wb.save(file_name)
    return file_name


def save_file(file_type, data, file_name):
    """
    保存文件
    """
    if file_type == 1:
        save_xlsx_file(data, f"ex_file/{file_name}")
    return file_name


def gen_task_no():
    return f"task{valdate_code()}{str(int(time.time()))}"


def send_ding_errmsg(errmsg, task_id=None, params=None):
    """
    发送叮叮报警机器人
    """
    webhook_url = current_app.config["DING_MSG_URL"]
    headers = {"Content-Type": "application/json ;charset=utf-8"}

    msg = f"错误信息:\n"
    if task_id:
        msg += f"TaskID: {task_id}\n"
    if params:
        msg += f"Params: {params}\n"
    msg += f"Return: {errmsg}"

    data = {
        "msgtype": "text",
        "text": {
            "content": msg
        }
    }

    requests.post(webhook_url, headers=headers, data=json.dumps(data))
    return
