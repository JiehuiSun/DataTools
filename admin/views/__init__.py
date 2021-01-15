#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-01-11 16:59:50
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: __init__.py


from flask_admin.contrib.sqla import ModelView


class AdminBaseView(ModelView):
    """
    后台基类
    """
    column_labels = {
        "dt_create": "创建时间",
        "dt_update": "更新时间",
    }

    column_exclude_list = (
        "is_deleted", "dt_update"
    )

    form_excluded_columns = (
        "is_deleted", "dt_update", "dt_create", "id"
    )
