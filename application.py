import os
import atexit
import fcntl
import logging
from flask import Flask, render_template
from flask_admin import Admin, AdminIndexView
from flask_babelex import Babel
from werkzeug.routing import BaseConverter

from base import configs
from base import db
from base import redis
from base import session
from base import mail
from base import apscheduler
from base import tasks
from account.helpers import algorithm_auth_login
from admin import model_admin
from dms import init_tasks


APP_NAME = 'base'

class RegexConverter(BaseConverter):
    def __init__(self, url_map, *args):
        super(RegexConverter, self).__init__(url_map)
        # 将接受的第1个参数当作匹配规则进行保存
        self.regex = args[0]


def create_app():
    app = Flask(APP_NAME)
    admin = Admin(app, name="后台管理系统", index_view=AdminIndexView(
        name='导航栏',
        template='admin_index.html',
        url='/admin'
    ))
    model_admin(admin, db)
    babel = Babel(app)
    app.config.from_object(configs.DefaultConfig)
    app.url_map.converters['re'] = RegexConverter
    config_blueprint(app)
    config_logger(app)
    config_db(app)
    config_redis(app)
    config_session(app)
    config_login(app)
    config_mail(app)
    config_apscheduler(app)
    return app


def config_blueprint(app):
    from base.urls import instance
    app.register_blueprint(instance, url_prefix='/api' if configs.DefaultConfig.RESP_TYPE == "json" else "")


def config_logger(app):
    log_dir = './var/log/'
    log_filename = 'flask.log'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    config_dict = {
        'filename': log_dir + log_filename,
        'format': '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    }
    logging.basicConfig(**config_dict)


def config_db(app):
    db.init_app(app)


def config_redis(app):
    redis.init_app(app)


def config_session(app):
    session.init_app(app)


def config_login(app):
    configs.lm.init_app(app)

    from account.models.UserModel import UserModel

    @configs.lm.user_loader
    def load_user(userid):
        return UserModel.query.filter_by(id=userid).one_or_none()

    @configs.lm.request_loader
    def load_user_from_request(req):
        auth_token = req.headers.get('token')
        if not auth_token:
            return
        try:
            user_id, random_str, timestamp, auth_code = auth_token.split("|")
        except Exception as e:
            return
        auth_code_new = algorithm_auth_login(user_id, random_str, timestamp)
        if auth_code == auth_code_new.split("|")[-1]:
            ret = UserModel.query.filter_by(id=user_id).one_or_none()
            # user_session = {"user_id": user_id}
        else:
            return
        if not ret:
            return
        return ret


def config_mail(app):
    mail.init_app(app)


def config_apscheduler(app):
    try:
        apscheduler.shutdown()
    except:
        pass
    apscheduler.init_app(app)
    apscheduler.start()
    """
    f = open("scheduler.lock", "wb")
    try:
        fcntl.flock(f, fcntl.LOCK_SH)
        apscheduler.init_app(app)
        apscheduler.start()
    except Exception as e:
        print(f"Task Err : {e}")
        pass
    def unlock():
        fcntl.flock(f, fcntl.LOCK_UN)
        f.close()
    atexit.register(unlock)
    """



app = create_app()
tasks.InitTasks()
init_tasks()

@app.route("/", endpoint="index")
def index():
    return render_template("index.html")
