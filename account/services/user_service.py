#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2020-08-21 15:25:23
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: user_service.py


import time

from account.backends.user_backend import UserBKE
from account.helpers import (algorithm_auth_login, make_random_str)


class APIUser:
    @classmethod
    def register_user(self, username: str, password: str) -> dict:
        flag, user_obj = UserBKE.create_user(username, password)
        if not flag:
            return flag, user_obj

        ret = {
            "id": user_obj.id,
            "username": user_obj.username
        }
        return True, ret

    @classmethod
    def check_username_is_existed(self, username: str) -> bool:
        return UserBKE.check_username_is_existed(username)

    @classmethod
    def login(self, username: str, password: str) -> dict:
        flag, user_or_msg = UserBKE.login(username, password)
        if not flag:
            return flag, user_or_msg

        if not user_or_msg.active:
            return False, "您的账号已被禁用"

        auth_code_params = {
            "user_id": user_or_msg.id,
            "random_str": make_random_str(),
            "timestamp": int(time.time())
        }

        ret_code = algorithm_auth_login(**auth_code_params)

        ret = {
            "user_id": user_or_msg.id,
            "username": user_or_msg.username,
            "token": str(ret_code)
        }

        return True, ret
