#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-01-11 15:10:03
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: models.py


import time

from base import db
from utils import time_utils, valdate_code, gen_task_no


class DatabaseModel(db.Model):
    """
    数据库
    """
    __tablename__ = "database_model"

    id = db.Column(db.Integer, primary_key=True)
    host = db.Column(db.String(128), nullable=False, comment="主机名")
    username = db.Column(db.String(128), nullable=False, comment="用户名")
    password = db.Column(db.String(128), nullable=False, comment="密码")
    port = db.Column(db.Integer, default=3306, nullable=False, comment="端口号")
    name = db.Column(db.String(32), nullable=False, comment="库名")
    comments = db.Column(db.String(128), nullable=True, comment="备注")
    random_code = db.Column(db.String(8), default=valdate_code, nullable=False, comment="随机码")
    is_deleted = db.Column(db.Boolean, default=False)
    dt_create = db.Column(db.DateTime, default=time_utils.now_dt)
    dt_update = db.Column(db.DateTime, default=time_utils.now_dt)

    # def __init__(self, name):
        # self.name = name

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class TaskTypeModel(db.Model):
    """
    任务类型
    """
    __tablename__ = "task_type_model"

    type_dict = {
        1: "单sql",
        2: "多sql-o2o",
        3: "多sql-o2m",
        4: "多sql-m2m",
    }

    id = db.Column(db.Integer, primary_key=True)
    type_id = db.Column(db.Integer, nullable=False, default=1, comment="类型ID")
    name = db.Column(db.String(128), nullable=False, comment="类型名")
    comments = db.Column(db.String(128), nullable=True, comment="备注")
    is_deleted = db.Column(db.Boolean, default=False)
    dt_create = db.Column(db.DateTime, default=time_utils.now_dt)
    dt_update = db.Column(db.DateTime, default=time_utils.now_dt)

    def __str__(self):
        return self.name


class RequirementModel(db.Model):
    """
    需求
    """
    __tablename__ = "requirement_model"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, comment="项目名")
    comments = db.Column(db.String(128), nullable=True, comment="备注")
    user_mail_list = db.Column(db.Text, nullable=False, comment="用户邮箱")
    # sqls = db.relationship('SQLModel', backref='project', lazy='dynamic')
    # tasks = db.relationship('TasksModel', backref='project', lazy='dynamic')
    task_type_id = db.Column(db.ForeignKey("task_type_model.id"))
    task_type = db.relationship('TaskTypeModel', backref=db.backref('requirement_model', lazy='dynamic'))
    is_deleted = db.Column(db.Boolean, default=False)
    dt_create = db.Column(db.DateTime, default=time_utils.now_dt)
    dt_update = db.Column(db.DateTime, default=time_utils.now_dt)

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class SQLModel(db.Model):
    """
    sql
    """
    __tablename__ = "sql_model"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False, comment="SQL名")
    project_id = db.Column(db.ForeignKey("requirement_model.id"))
    project = db.relationship('RequirementModel', backref=db.backref('sql_model', lazy='dynamic'))
    database_id = db.Column(db.ForeignKey("database_model.id"))
    database = db.relationship('DatabaseModel', backref=db.backref('sql_model', lazy='dynamic'))
    content = db.Column(db.Text, nullable=False, comment="sql语句")
    special_field = db.Column(db.String(64), nullable=False, comment="特殊字段")
    parent_id = db.Column(db.Integer, db.ForeignKey("sql_model.id"))
    parent = db.relationship("SQLModel", remote_side=[id])
    parent_field = db.Column(db.String(64), nullable=False, comment="父字段")
    is_deleted = db.Column(db.Boolean, default=False)
    dt_create = db.Column(db.DateTime, default=time_utils.now_dt)
    dt_update = db.Column(db.DateTime, default=time_utils.now_dt)

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class TasksModel(db.Model):
    """
    任务
    """
    __tablename__ = "tasks_model"

    id = db.Column(db.Integer, primary_key=True)
    task_no = db.Column(db.String(128), nullable=False, default=gen_task_no, comment="备注")
    task_type = db.Column(db.Enum('cron', 'interval', 'date'), server_default='cron', nullable=False)
    name = db.Column(db.String(128), nullable=False, comment="任务名")
    project_id = db.Column(db.ForeignKey("requirement_model.id"))
    project = db.relationship('RequirementModel', backref=db.backref('tasks_model', lazy='dynamic'))
    comments = db.Column(db.String(256), nullable=True, comment="备注")
    year = db.Column(db.Integer, nullable=True, comment="年")
    month = db.Column(db.Integer, nullable=True, comment="月")
    day = db.Column(db.Integer, nullable=True, comment="日")
    week = db.Column(db.Integer, nullable=True, comment="周")
    day_of_week = db.Column(db.Integer, nullable=True, comment="周期")
    hour = db.Column(db.Integer, nullable=True, comment="时")
    minute = db.Column(db.Integer, nullable=True, comment="分")
    second = db.Column(db.Integer, nullable=True, comment="秒")
    status = db.Column(db.Boolean, default=False, comment="状态")
    is_deleted = db.Column(db.Boolean, default=False)
    dt_create = db.Column(db.DateTime, default=time_utils.now_dt)
    dt_update = db.Column(db.DateTime, default=time_utils.now_dt)

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class TasksLogModel(db.Model):
    """
    任务日志
    """
    __tablename__ = "tasks_log_model"

    id = db.Column(db.Integer, primary_key=True)
    ex_type = db.Column(db.Integer, comment="执行类型")
    task_no = db.Column(db.ForeignKey("tasks_model.id"))
    task = db.relationship('TasksModel', backref=db.backref('tasks_log_model', lazy='dynamic'))
    return_info = db.Column(db.Text, nullable=True, comment="返回信息")
    dt_handled = db.Column(db.DateTime, default=time_utils.now_dt, comment="处理时间")
    is_successful = db.Column(db.Boolean, default=True, comment="是否成功")
    recipient = db.Column(db.Text, nullable=True, comment="收信人")
    is_deleted = db.Column(db.Boolean, default=False)
    dt_create = db.Column(db.DateTime, default=time_utils.now_dt)
    dt_update = db.Column(db.DateTime, default=time_utils.now_dt)

    def __repr__(self):
        return str(self.task_no)

    def __str__(self):
        return str(self.task_no)
