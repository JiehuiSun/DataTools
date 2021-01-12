# 这里将url进行统一的管理，每添加一个接口，只需要在urls中添加即可

from dms.views import DatabasesView


MODEL_NAME = "dms"

urls = ()

routing_dict = dict()
v1_routing_dict = dict()

# login
v1_routing_dict["databases"] = DatabasesView

for k, v in v1_routing_dict.items():
    routing_dict["/v1/{0}/".format(k)] = v
