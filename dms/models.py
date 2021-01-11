#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-01-11 15:10:03
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: models.py


from base import db
from utils import time_utils, valdate_code


class DatabaseModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    host = db.Column(db.String(128), nullable=False)
    username = db.Column(db.String(128), nullable=False)
    passeord = db.Column(db.String(128), nullable=False)
    port = db.Column(db.Integer, default=3306)
    name = db.Column(db.String(32), nullable=False)
    comments = db.Column(db.String(128), nullable=False)
    random_code = db.Column(db.String(8), default=valdate_code, nullable=False)
    is_deleted = db.Column(db.Boolean, default=False)
    dt_create = db.Column(db.DateTime, default=time_utils.now_dt)
    dt_update = db.Column(db.DateTime, default=time_utils.now_dt)

