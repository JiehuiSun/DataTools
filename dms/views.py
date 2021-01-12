#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-01-11 17:53:07
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: views.py


from api import Api
from dms.models import DatabaseModel


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
