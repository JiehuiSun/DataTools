#!/usr/bin/env python
# mail: sunjiehuimail@foxmail.com
# author: huihui
# -*- coding: utf-8 -*-


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

        self.ver_params()

        if len(self.data["username"]) > 20 or len(self.data["password"]) > 20:
            return self.ret(12001, "用户名或密码不符合规范")

        flag, msg = APIUser.check_username_is_existed(self.data["username"])
        if flag:
            return self.ret(12001, "该用户名已存在")

        flag, user_dict = APIUser.register_user(self.data["username"],
                                             self.data["password"])
        if not flag:
            return self.ret(12001)

        ret = {
            "user_id": user_dict["id"]
        }

        return self.ret(data=ret)


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

        self.ver_params()

        flag, ret = APIUser.login(self.data["username"],
                                  self.data["password"])
        if not flag:
            return self.ret(12002, ret)
        return self.ret(data=ret)


class LogoutView(Api):
    """
    退出登录
    """
    def post(self):
        ret = {
            'errcode': 0,
            'errmsg': 'Logout ok',
        }
        return self.data(data=ret)

#
# instance.add_url_rule('/login', view_func=Login.as_view('login'), methods=['POST'])
# instance.add_url_rule('/logout', view_func=LogoutView.as_view('logout'), methods=['POST'])
