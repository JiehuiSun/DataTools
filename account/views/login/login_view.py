#!/usr/bin/env python
# mail: sunjiehuimail@foxmail.com
# author: huihui
# -*- coding: utf-8 -*-


from flask_login import current_user
from api import Api
from account.services.user_service import APIUser


class RegisterView(Api):
    """
    注册
    """
    NEED_LOGIN = False

    def post(self):
        self.params_dict = {
            "username": "required str",
            "password": "required str"
        }
        if not self.data:
            return self.ret(template="register.html", data={"errmsg": "登录失败", "next_url": "base./account/v1/register/"})

        self.ver_params()

        if len(self.data["username"]) > 20 or len(self.data["password"]) > 20:
            return self.ret(12001, "用户名或密码不符合规范")

        flag, msg = APIUser.check_username_is_existed(self.data["username"])
        if not flag:
            return self.ret(12001, "该用户名已存在")

        flag, user_dict = APIUser.register_user(self.data["username"],
                                             self.data["password"])
        if not flag:
            return self.ret(12001)

        ret = {
            "user_id": user_dict["id"]
        }

        return self.ret(template="login.html", data={"errmsg": "注册成功", "next_url": "base./account/v1/login/"})

    def get(self):
        return self.post()


class LoginView(Api):
    """
    新登录
    """
    NEED_LOGIN = False

    def post(self):
        self.params_dict = {
            "username": "required str",
            "password": "required str"
        }
        if current_user.is_authenticated:
            return self.ret(template="index.html", data={"errmsg": "登录成功", "next_url": "/"})

        if not self.data:
            return self.ret(template="login.html", data={"errmsg": "登录失败", "next_url": "base./account/v1/login/"})


        self.ver_params()

        flag, ret = APIUser.login(self.data["username"],
                                  self.data["password"])
        if not flag:
            return self.ret(template="login.html", data={"errmsg": "登录失败", "next_url": "base./account/v1/login/"})
        return self.ret(template="200.html", data={"errmsg": "登录成功", "next_url": f"{self.next_url}"})
    def get(self):
        return self.post()

class LogoutView(Api):
    """
    退出登录
    """
    NEED_LOGIN = False
    def post(self):
        ret = {
            'errcode': 0,
            'errmsg': 'Logout ok',
        }
        flag, ret = APIUser.logout()
        return self.ret(template="200.html", data={"errmsg": "注销成功", "next_url": "base./account/v1/login/"})
    def get(self):
        return self.post()
#
# instance.add_url_rule('/login', view_func=Login.as_view('login'), methods=['POST'])
# instance.add_url_rule('/logout', view_func=LogoutView.as_view('logout'), methods=['POST'])
