#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2020-08-20 21:40:01
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: tests.py


from api import Api


class Test(Api):
    """
    测试
    """

    # 默认需要登陆, 该标识为不需要登陆的API
    NEED_LOGIN = False

    def get(self):

        print(self.data)

        return self.ret(10101, "参数错误")

    def post(self):
        """
        说明:
            self.params_dict 是需要校验参数时增加
                optional 可选参数
                required 必填参数
                    pass/int/list/str/... 参数类型

            self.ver_params 需要校验参数, 不校验可不写

            self.ret 返回数据
                self.ret()  空数据为正确返回, 不需要其他数据使用
                self.ret(errcode) 返回错误码库定义的错误码, 如需自定义直接第二个传参即可
                self.ret(data={}) 返回正确数据, data接收dict类型数据
        """
        # 需要校验的参数
        self.params_dict = {
            "test1": "optional pass",   # test1参数为可选参数并不校验参数类型
            "test2": "required int"     # test2参数为必填参数并为整形类型
        }

        # 需要校验参数
        self.ver_params()

        print(self.data)

        return self.ret()
