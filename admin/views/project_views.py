#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-01-14 12:14:48
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: project_views.py


from flask_admin.contrib.sqla import ModelView


class ProjectView(ModelView):

    column_labels = {
        "name": "项目名",
        "comments": "备注",
        "user_mail_list": "用户邮箱",
        "dt_create": "创建时间",
        "dt_update": "更新时间",
    }

    column_exclude_list = (
        "is_deleted", "dt_update"
    )


class SQLView(ModelView):

    column_labels = {
        "project": "项目",
        "database": "数据库",
        "content": "SQL",
        "special_field": "特殊字段",
        "dt_create": "创建时间",
        "dt_update": "更新时间",
    }

    column_exclude_list = (
        "is_deleted", "dt_update"
    )


class TaskView(ModelView):

    column_labels = {
        "project": "项目",
        "database": "数据库",
        "comments": "备注",
        "dt_create": "创建时间",
        "dt_update": "更新时间",
    }

    column_exclude_list = (
        "is_deleted", "dt_update"
    )
