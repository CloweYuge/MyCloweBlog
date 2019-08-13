import os
from mycloweblog.extensions import db
from flask import current_app
from flask_login import UserMixin
from flask_avatars import Identicon
import time
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from mycloweblog.utils import shijc_type, shijc_now
# from myclowelog.extensions import whooshee


class Admin(db.Model, UserMixin):
    id = db.Column(db.SmallInteger, primary_key=True)

    login_name = db.Column(db.String(20))
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))

    email = db.Column(db.String(25))
    avatar = db.Column(db.LargeBinary)
    active = db.Column(db.Boolean, default=True)
    about = db.Column(db.Text)

    # 文章
    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'))
    admin_blogs = db.relationship('Blog', back_populates='admin_blog', foreign_keys=[blog_id])

    def __init__(self, **kwargs):
        super(Admin, self).__init__(**kwargs)

    @property
    def is_active(self):
        return self.active

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


class Plate(db.Model):
    """
    板块
    """
    id = db.Column(db.SmallInteger, primary_key=True)
    name = db.Column(db.String(15))
    mark = db.Column(db.Text)

    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'))
    plate_blogs = db.relationship('Blog', back_populates='plate_blog', foreign_keys=[blog_id])


class Category(db.Model):
    """
    分类
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15))
    mark = db.Column(db.Text)

    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'))
    category_blogs = db.relationship('Blog', back_populates='category_blog', foreign_keys=[blog_id])


# 文章与标签多对多表
blog_tag = db.Table('blog_tag', db.Column('blog_id', db.Integer, db.ForeignKey('blog.id')),
                    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')))


class Blog(db.Model):
    """
    文章
    """
    id = db.Column(db.Integer, primary_key=True)
    add_time = db.Column(db.Integer, default=shijc_now())
    up_time = db.Column(db.Integer, default=shijc_now())
    title = db.Column(db.String(100), nullable=False)
    photos = db.Column(db.LargeBinary(length=16777210))
    content = db.Column(db.Text)

    look_count = db.Column(db.Integer, default=0)

    # 发布人
    admin_blog = db.relationship('Admin', back_populates='admin_blogs')
    # 评论
    blog_comments = db.relationship('Comment', back_populates='blog_comment')
    # 板块
    plate_blog = db.relationship('Plate', back_populates='plate_blogs')
    # 分类
    category_blog = db.relationship('Blog', back_populates='category_blogs')
    # 标签
    tags = db.relationship('Tag', secondary=blog_tag, back_populates='blogs')


class Photo(db.Model):
    """
    临时配图
    """
    id = db.Column(db.SmallInteger, primary_key=True)
    photos = db.Column(db.LargeBinary(length=16777210))
    add_time = db.Column(db.Integer, default=shijc_now())
    status = db.Column(db.Boolean, default=False)


class Comment(db.Model):
    """
    评论
    """
    id = db.Column(db.Integer, primary_key=True)
    add_time = db.Column(db.Integer, default=shijc_now())
    mark = db.Column(db.Text)

    admin_id = db.Column(db.SmallInteger)
    name = db.Column(db.String(15))
    email = db.Column(db.String(15))
    site = db.Column(db.String(50))
    avatar = db.Column(db.LargeBinary)

    # 上级领导，自引用一对多关系
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    # 此为查询上级
    commented = db.relationship('Comment', back_populates='comments', remote_side=[id], foreign_keys=[comment_id])
    # 此为查询下级
    comments = db.relationship('Comment', back_populates='commented')

    # 评论域
    comment_yu = db.Column(db.Integer)
    # 文章
    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'))
    blog_comment = db.relationship('Blog', back_populates='blog_comment', foreign_keys=[blog_id])

    def __init__(self, **kwargs):
        super(Comment, self).__init__(**kwargs)
        self.generate_avatar()

    def generate_avatar(self):
        avatar = Identicon()
        filenames = avatar.generate(text=self.name)
        self.avatar = filenames[1]
        db.session.commit()


class Tag(db.Model):
    """
    标签
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15))

    # 文章
    blogs = db.relationship('Blog', secondary=blog_tag, back_populates='tags', lazy='dynamic')


class Notification(db.Model):
    """
    消息提醒
    """
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    time = db.Column(db.Integer, default=shijc_now())


class Link(db.Model):
    """
    友链
    """
    id = db.Column(db.SmallInteger, primary_key=True)
    name = db.Column(db.String(30))
    logo = db.Column(db.String(100))
    site = db.Column(db.String(100))

    # 被点击次数
    click_count = db.Column(db.Integer, default=0)
