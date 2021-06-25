#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-01-11 16:59:50
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: __init__.py


from flask import url_for
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user


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

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return url_for("admin.index")
