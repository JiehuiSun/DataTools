#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-01-11 17:53:07
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: views.py


import time
import pymysql
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook
from flask import make_response, send_file

from api import Api
from dms.models import DatabaseModel
from utils import valdate_code


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

        wb = Workbook()
        ws_list = wb.worksheets
        if ws_list:
            ws = ws_list[0]
        else:
            ws = wb.create_sheet('Sheet')
        ws.append(field_list)

        for i in cursor.fetchall():
            ws.append(i)

        file_name = "{0}-{1}.xlsx".format(str(int(time.time())), valdate_code())
        wb.save(file_name)
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