
import json
import mimetypes
import requests
import pymysql
from flask import current_app
from flask_mail import Message


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
            from datacenter import redis
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
            with app.open_resource(f"../{i}") as fp:
                msg.attach(i.split("/")[-1], mimetypes.guess_type("aaa.txt")[0], fp.read())

    from datacenter import mail
    mail.send(msg)


def tasks(**params):
    def outter(func):
        def wrapper(*args,**kwargs):
            res = func
            from datacenter import apscheduler
            apscheduler.add_job(func=func, **params)
            return res
        return wrapper
    return outter
