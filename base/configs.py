from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from utils.flask_redis import FlaskRedis
from utils.session import Session
from flask_mail import Mail
from flask_apscheduler import APScheduler


db = SQLAlchemy()
redis = FlaskRedis()
session = Session()
lm = LoginManager()
mail = Mail()
apscheduler = APScheduler()


class DefaultConfig(object):

    DEBUG = True
    SECRET_KEY = '4e4y>;8i~O=+d8?8!1DTB)Vs9VJiX$<<Dt@~]R_,@Q;tIqk?csY(+YT;V)dU~j=.'
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://base:base@localhost/base?charset=utf8mb4'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///datatools.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URI = 'redis://:@localhost:6379/3'
    APP_LOGIN_AUTH_KEY = "mumway"

    MODULES = (
        "account",
        "dms",
        # "base"
    )

    BABEL_DEFAULT_LOCALE = "zh_CN"

    # 返回方式(templates/json)
    RESP_TYPE = "templates"

    # 邮件配置
    MAIL_USE_SSL = False
    MAIL_USE_TLS = True
    MAIL_SERVER = 'smtp.exmail.qq.com'
    MAIL_PORT = 587
    MAIL_USERNAME = '' # 帐号
    MAIL_PASSWORD = ''  # 密码
    MAIL_DEFAULT_SENDER = MAIL_USERNAME

# local_configs目的: 因为线上、测试、开发环境的配置不同，
# 所以每个环境可以有自己的local_configs来覆盖configs里的DefaultConfig
# 但是这里有一个问题


try:
    from .local_configs import *
except ModuleNotFoundError as e:
    pass
