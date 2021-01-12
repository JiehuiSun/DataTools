#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2021-01-11 17:53:07
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: views.py


from api import Api


class DatabasesView(Api):
    NEED_LOGIN = False
    def get(self):
        return self.ret(template="databases.html")
