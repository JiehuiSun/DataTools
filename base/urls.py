# 这里将url进行统一的管理
# 每个模块下的urls文件中必须有MODEL_NAME及routing_dict
import os
import sys
import importlib
from flask import Blueprint
from base.configs import DefaultConfig

instance = Blueprint('base', __name__, template_folder='web')

urls = ()

routing_dict = dict()
v1_routing_dict = dict()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

for module in DefaultConfig.MODULES:
    if os.path.exists(os.path.join(BASE_DIR, '{}/urls.py'.format(module))):
        app_router = importlib.import_module('{}.urls'.format(module))
        try:
            MODEL_NAME = app_router.MODEL_NAME
            model_routing_dict = app_router.routing_dict
        except:
            print("模块缺少路由配置routing_dict/MODEL_NAME")
            sys.exit()

        for k, v in model_routing_dict.items():
            routing_dict["/{0}{1}".format(MODEL_NAME, k)] = v

methods = ['GET', 'POST', 'PUT', 'DELETE']
for path, view in routing_dict.items():
    # instance.add_url_rule("{0}<re('.*'):key>".format(path),
    if "<" not in path:
        endpoint = path
    else:
        endpoint = path.split("<")[0]
    instance.add_url_rule("{0}".format(path),
                          view_func=view.as_view(endpoint),
                          methods=methods,
                          endpoint=endpoint)
