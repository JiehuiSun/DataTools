# 这里写一个基础接口类，以后所以接口都需要继承此类
# __call__方法是为了使用此类可以直接像方法一样调用
# 异常处理时，先捕捉BaseError，我们将BaseError当成
# 正常的业务异常；之后捕捉Exception，就是系统异常，
# 需要进行日志记录等操作
from flask import request
from flask import jsonify
from flask import current_app
from flask.views import View

from base import errors
from base import session

from .req_framework import VerParams
from .resp_framework import Resp


class Api(VerParams, Resp, View):
    NEED_LOGIN = True

    def __init__(self):
        self.__name__ = self.__class__.__name__

    def _get_token(self):
        token = request.headers.get('HTTP-X-TOKEN')
        if not token:
            raise errors.NoTokenError
        return token

    def _identification(self):
        if self.NEED_LOGIN:
            self.token = self._get_token()
            self.user_id = session.get_session(self.token)
            if not self.user_id:
                raise errors.LoginExpiredError

    def _handle_params(self):
        """
        参数校验
        """
        if request.method.lower() == 'get':
            self.data = dict(request.args)
        else:
            self.data = request.json

    def ver_params(self):
        """
        参数校验
        """
        ret = self._ver_params(self.params_dict, self.data)
        if ret is not True:
            raise errors.ParamsError(ret)

    def _pre_handle(self):
        """
            调用具体业务方法之前，如果需要一些权限认证或者其它操作在这里实现
        """
        self._identification()

    def _after_handle(self):
        """
            调用具体业务方法后，如果需要一些结果处理等在这里实现
        """
        pass

    def dispatch_request(self, *args, **kwargs):
        data = ''
        errno = 0
        errmsg = ''
        try:
            self._handle_params()
            self.__dispatch()
            method = getattr(self, request.method.lower(), None)
            if not method:
                raise errors.MethodError
            self._pre_handle()
            result = method()
            self._after_handle()
        except errors.BaseError as e:
            current_app.logger.error(e)
            result = {
                "errcode": e.errno,
                "errmsg": e.errmsg,
                "data": {}
            }
        except Exception as e:
            current_app.logger.error(e)
            current_app.logger.exception(e)
            result = {
                "errcode": errors.BaseError.errno,
                "errmsg": errors.BaseError.errmsg,
                "data": {}
            }
        return jsonify(result)

    def __get_subpath(self, path):
        tail_slash = ''
        if path.endswith('/'):
            path = path[:-1]
            tail_slash = '/'
        path, key = path.rsplit('/', maxsplit=1)
        path += '/'
        return path, key, tail_slash

    def __dispatch(self):
        from base.urls import routing_dict
        path = request.path.replace('/api', '')
        if not path:
            raise errors.MethodError
        self.key = None
        path_dict = {}
        tail_slash = ''
        api_path = path
        upstream = ''
        if path in routing_dict:
            upstream = routing_dict[path]
        else:
            subpath, self.key, tail_slash = self.__get_subpath(path)
            if subpath in routing_dict:
                upstream = routing_dict[subpath]
                api_path = subpath
        if not upstream:
            raise errors.MethodError

        lpc = ''
        url = ''
        # 目前先不走url
        if isinstance(upstream, str):
            raise errors.MethodError("请求无效")

        lpc = upstream

        self.headers = {
            'Host': request.headers['HOST'],
            'User-Agent': request.headers['USER_AGENT'],
            'Path': api_path,
            'Dev-Platform': request.headers.get('HTTP_DEV_PLATFORM', None),
            'Dev-Model': request.headers.get('HTTP_DEV_MODEL', None),
            'Dev-Version': request.headers.get('HTTP_DEV_VERSION', None),
            'App-Version': request.headers.get('HTTP_APP_VERSION', None),
            'App-Client': request.headers.get('HTTP_APP_CLIENT', None),
            'App-Id': request.headers.get('HTTP_X_AUTH_APPID', None),
            'Path_Dict': path_dict,
            'open_id': request.headers.get('HTTP_AUTHORIZATION', None),

        }
        if 'HTTP_X_AUTH_USERTOKEN' in request.headers:
            self.headers['X-AUTH-USERTOKEN'] = request.headers['HTTP_X_AUTH_USERTOKEN']
        for k, v in request.files.items():
            request.data.pop(k)
        if request.content_type and request.content_type.lower() == 'application/json':
            self.headers['Content-Type'] = request.content_type

        if lpc:
            try:
                self.call_method = request.method.lower()
                if self.call_method == 'get' and not self.key:
                    self.call_method = 'list'
            except Exception as e:
                # logger.error(f'请求失败：\ncall_method {request.method.lower()}\n url {request.path} \n headers {headers} ;\n data {data} \n {e} ')
                raise errors.MethodError("请求无效")
            return
        if url:
            raise errors.MethodError("请求无效")
