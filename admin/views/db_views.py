#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-01-11 17:00:29
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: db_views.py


from . import AdminBaseView


class DBView(AdminBaseView):
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

    form_excluded_columns = (
        "is_deleted", "dt_update", "dt_create", "id", "random_code", "sql_model"
    )
