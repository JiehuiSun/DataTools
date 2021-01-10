# 根据需求定义不同model
# username/email/phone没有做数据库级的唯一约束
# 因此需要在程序中进行限制, 为了解决用户删除后，再创建同样的用户问题

import bcrypt
from flask import current_app
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.exc import IntegrityError
from base import db
from base import errors
from utils import time_utils


class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    active = db.Column(db.Boolean, default=True)
    is_deleted = db.Column(db.Boolean, default=False)
    dt_create = db.Column(db.DateTime, default=time_utils.now_dt)
    dt_update = db.Column(db.DateTime, default=time_utils.now_dt)

    @classmethod
    def register(cls, username, password,
                 is_active=True, ):
        try:
            passhash = bcrypt.hashpw(password.encode('utf-8'),
                                     bcrypt.gensalt())
            user = cls(username=username,
                       password=passhash,
                       active=is_active)
            db.session.add(user)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            raise errors.InvalidArgsError("该登录账号已存在")
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"添加用户失败: {e}")
            raise errors.DBError()
        return user

    @classmethod
    def login(cls, username, password):
        try:
            user = cls.query.filter_by(username=username, is_deleted=False).one()
            if user.password.encode('utf-8') == bcrypt.hashpw(password.encode('utf-8'),
                                                              user.password.encode('utf-8')):
                return True, user
            else:
                return False, "密码错误"
        except NoResultFound as e:
            db.session.rollback()
            return False, "该用户不存在"
        except MultipleResultsFound as e:
            db.session.rollback()
            current_app.logger.error(f"用户登陆错误(重复数据): {e}")
            return False, "数据库错误"
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"用户登陆错误: {e}")
            return False, "数据库或其他错误"

    @classmethod
    def change_password(cls, username, password, new_password, force=False):
        passhash = bcrypt.hashpw(new_password.encode('utf-8'),
                                 bcrypt.gensalt())
        if force:
            try:
                user = cls.query.filter_by(username=username).one()
                user.passhash = passhash
                db.session.commit()
            except NoResultFound as e:
                ret = {
                    'errcode': 2,
                    'errmsg': 'user does not exist'
                }
            except MultipleResultsFound as e:
                ret = {
                    'errcode': 3,
                    'errmsg': 'duplicated user found, please check database'
                }
            except Exception as e:
                ret = {
                    'errcode': 500,
                    'errmsg': 'unknow database error occur',
                }
            return ret
        else:
            ret = cls.login(username, password)
            if ret['errcode'] == 0:
                user = ret['data']
                user.passhash = passhash
                db.session.commit()
            else:
                ret = {
                    'errmsg': '对不起，旧密码输入错误',
                    'errcode': 5,
                }
            return ret
