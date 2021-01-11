#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-01-11 16:28:39
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: __init__.py


from dms.models import DatabaseModel

from .views.db_views import DBView


def model_admin(admin, db):
    admin.add_view(DBView(DatabaseModel, db.session, name="数据库"))
