#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2020-08-21 15:25:52
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: user_backend.py


from flask import current_app
from account.models.UserModel import UserModel


class UserBKE:
    @classmethod
    def query_user_by_id(self, id):
        try:
            user_obj = UserModel.query.filter_by(id=id,
                                                 is_deleted=False).one_or_none()
        except Exception as e:
            current_app.logger.error("查询用户失败: {e}")
            return False, "查询用户失败"
        return True, user_obj

    @classmethod
    def check_username_is_existed(self, username):
        try:
            user_count = UserModel.query.filter_by(username=username,
                                                 is_deleted=False).count()
        except Exception as e:
            current_app.logger.error("查询用户失败: {e}")
            return False, "查询用户失败"
        if user_count:
            return True, True
        else:
            return True, False

    @classmethod
    def create_user(self, username, password):
        params = {
            "username": username,
            "password": password
        }
        try:
            user_obj = UserModel.register(**params)
        except Exception as e:
            current_app.logger.error(f"查询用户失败: {e}")
            return False, "查询用户失败"
        if not user_obj:
            return False, "创建用户失败"
        return True, user_obj

    @classmethod
    def login(self, username, password):
        params = {
            'username': username,
            'password': password,
        }
        flag, ret = UserModel.login(**params)
        return flag, ret
