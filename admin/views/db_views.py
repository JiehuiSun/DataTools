#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-01-11 17:00:29
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: db_views.py


from flask_admin.contrib.sqla import ModelView


class DBView(ModelView):
    # can_delete = False
    # can_edit = False
    # can_create = False

    column_labels = {
        "name": "库名",
        "comments": "备注",
        "dt_create": "创建时间",
        "dt_update": "更新时间",
    }

    column_exclude_list = (
        "host", "username", "password", "port", "random_code", "is_deleted", "dt_update"
    )
