#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-01-11 16:28:39
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: __init__.py


from dms.models import DatabaseModel, RequirementModel, SQLModel, TasksModel

from .views.db_views import DBView
from .views.project_views import ProjectView, SQLView, TaskView


def model_admin(admin, db):
    admin.add_view(DBView(DatabaseModel, db.session, name="数据库"))
    admin.add_view(ProjectView(RequirementModel, db.session, name="项目"))
    admin.add_view(SQLView(SQLModel, db.session, name="SQL语句"))
    admin.add_view(TaskView(TasksModel, db.session, name="任务"))
