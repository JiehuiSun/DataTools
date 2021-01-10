# 这里将url进行统一的管理，每添加一个接口，只需要在urls中添加即可

from account.views.test.tests import Test
from account.views.login.login_view import RegisterView, LoginView


MODEL_NAME = "account"

urls = ()

routing_dict = dict()
v1_routing_dict = dict()

# test
v1_routing_dict["test"] = Test

# login
v1_routing_dict["register"] = RegisterView
v1_routing_dict["login"] = LoginView

for k, v in v1_routing_dict.items():
    routing_dict["/v1/{0}/".format(k)] = v
