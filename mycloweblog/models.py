import os
from mycloweblog.extensions import db
from flask import current_app
from flask_login import UserMixin
from flask_avatars import Identicon
import time
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
# from myclowelog.extensions import whooshee


class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    lgoin_name = db.Column(db.String(20))
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))
    about = db.Column(db.Text)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class Plate(db.Model):
    """
    板块
    """


class Category(db.Model):
    """
    分类
    """


class Comment(db.Model):
    """
    评论
    """


class Blog(db.Model):
    """
    文章
    """


class Tag(db.Model):
    """
    标签
    """


class Notification(db.Model):
    """
    消息提醒
    """


class Link(db.Model):
    """
    友链
    """
