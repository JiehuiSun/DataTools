#!/usr/bin/env python
# _*_ encoding: utf-8 _*_
# Create: 2020-08-20 15:56:16
# Author: huihui - sunjiehuimail@foxmail.com
# Filename: VerParams.py


import types
import datetime


class VerParams:
    """
    参数校验
    """
    def _ver_params(self, params_dict, data):
        data_keys = set(data.keys())
        max_keys = set(params_dict.keys())
        # mini keys 判断
        min_keys = set()
        for k in max_keys:
            check_method = params_dict[k]
            if isinstance(check_method, types.FunctionType):
                continue
            params_dict_list = params_dict[k].split(' ')
            if 'optional' not in params_dict_list:
                min_keys.add(k)
        overflow_keys = data_keys - max_keys
        lack_keys = min_keys - data_keys

        # 验证后端需要的key 传递情况
        flag_keys_not_match = False
        errmsg_keys_not_match = ''
        if overflow_keys:
            flag_keys_not_match = True
            errmsg_keys_not_match += '请求参数中, 多余的key包括: '
            errmsg_keys_not_match += ', '.join([str(k) for k in overflow_keys])
        if lack_keys:
            flag_keys_not_match = True
            errmsg_keys_not_match += '请求参数中, 缺少的key包括: '
            errmsg_keys_not_match += ', '.join([str(k) for k in lack_keys])
        if flag_keys_not_match:
            return errmsg_keys_not_match

        # 根据params_dict 逐条验证参数.
        errmsg_keys_valid = []
        for k, v in data.items():
            flag = False
            msg = ''
            check_method = params_dict[k]
            # 执行用户自定义验证方法
            if isinstance(check_method, types.FunctionType):
                flag, msg = check_method(v, k)
            elif isinstance(check_method, str):
                check_method_list = check_method.split(' ')
                for item_method in check_method_list:
                    if "|" in item_method:
                        item_method, params_format = item_method.split("|")
                        flag, msg = getattr(self, '_valid_'+item_method)(v, k, params_format)
                    else:
                        flag, msg = getattr(self, '_valid_'+item_method)(v, k)
                    if not flag:
                        break
                # 执行默认方法
            if not flag:
                errmsg_keys_valid.append(msg)
                continue
        if errmsg_keys_valid:
            errmsg = ' '.join(errmsg_keys_valid)
            return "参数错误: {0}".format(errmsg)
        return True

    def _valid_str(self, i, key_name=None):
        if isinstance(i, str):
            return True, 'OK'
        return False, key_name

    def _valid_required(self, i, key_name=None):
        '''
        该参数必须有值, 并且判断不能为 False
        '''
        if i or i == 0 or i == []:
            return True, key_name
        return False, key_name

    def _valid_optional(self, i, key_name=None):
        '''
        该参数可以不存在
        '''
        return True, 'OK'

    def _valid_pass(self, i, key_name=None):
        '''
        该参数必须存在, 但不需要验证
        '''
        return True, 'OK'

    def _valid_list(self, i, key_name=None):
        '''
        参数必须为list类型
        '''
        if isinstance(i, list):
            return True, 'OK'
        return False, '{0} 必须为list(array)类型, 谢谢配合!'.format(key_name)

    def _valid_int(self, i, key_name=None):
        '''
        参数必须为int类型
        '''
        if isinstance(i, int):
            return True, 'OK'
        return False, '{0} 必须为int(整型)类型, 谢谢配合!'.format(key_name)

    def _valid_date(self, i, key_name=None, dt_format='%Y-%m-%d %H:%M:%S'):
        '''
        参数必须为日期xxxx-xx-xx xx:xx:xx (以自定义为准)
        '''
        try:
            datetime.datetime.strptime(i, dt_format)
            return True, 'OK'
        except:
            return False, '{0} 日期格式错误, 如: "{1}", 谢谢配合!'.format(key_name, dt_format)
