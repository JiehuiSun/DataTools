#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-01-14 12:14:48
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: project_views.py


from . import AdminBaseView


class ProjectView(AdminBaseView):

    column_labels = {
        "name": "项目名",
        "comments": "备注",
        "user_mail_list": "用户邮箱",
        "task_type": "项目关系类型",
        "dt_create": "创建时间",
        "dt_update": "更新时间",
    }


class SQLView(AdminBaseView):

    column_labels = {
        "project": "项目",
        "database": "数据库",
        "content": "SQL",
        "special_field": "特殊字段",
        "dt_create": "创建时间",
        "dt_update": "更新时间",
    }


class TaskView(AdminBaseView):

    column_labels = {
        "task_no": "任务号",
        "name": "任务名称",
        "project": "项目",
        "database": "数据库",
        "comments": "备注",
        "dt_create": "创建时间",
        "dt_update": "更新时间",
    }
