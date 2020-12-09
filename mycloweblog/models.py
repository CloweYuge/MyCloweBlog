import os
# import pickle
from mycloweblog.extensions import db
# from flask import current_app, url_for
from flask_login import UserMixin
from flask_avatars import Identicon
# import time
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from mycloweblog.utils import shijc_type, shijc_now
from mycloweblog.settings import BaseConfig
# from myclowelog.extensions import whooshee


class Admin(db.Model, UserMixin):
    id = db.Column(db.SmallInteger, primary_key=True)

    login_name = db.Column(db.String(20))
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))

    email = db.Column(db.String(25))
    avatar = db.Column(db.String(64))
    active = db.Column(db.Boolean, default=True)
    about = db.Column(db.Text)

    # 文章
    admin_blogs = db.relationship('Blog', back_populates='admin_blog')

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

    # 文章
    plate_blogs = db.relationship('Blog', back_populates='plate_blog')
    # 分类
    plate_categorys = db.relationship('Category', back_populates='plate_category')


class Category(db.Model):
    """
    分类
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15))
    mark = db.Column(db.Text)
    fast = db.Column(db.Boolean, default=False)

    # 文章
    category_blogs = db.relationship('Blog', back_populates='category_blog')
    # 板块
    plate_id = db.Column(db.SmallInteger, db.ForeignKey('plate.id'))
    plate_category = db.relationship('Plate', back_populates='plate_categorys', foreign_keys=[plate_id])


# 文章与标签多对多表
blog_tag = db.Table('blog_tag', db.Column('blog_id', db.Integer, db.ForeignKey('blog.id')),
                    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')))


class Blog(db.Model):
    """
    文章
    """
    id = db.Column(db.Integer, primary_key=True)
    # 首次添加的时间
    add_time = db.Column(db.Integer, default=shijc_now())
    # 最近修改
    up_time = db.Column(db.Integer, default=0)
    title = db.Column(db.String(100), nullable=False)
    # photos = db.Column(db.LargeBinary(length=16777210))
    # 文章主体内容，依次为文本，html，md格式
    content = db.Column(db.Text)
    h_content = db.Column(db.Text)
    m_content = db.Column(db.Text)
    # 查看次数，仅记录非管理员
    look_count = db.Column(db.Integer, default=0)

    # 发布人
    admin_id = db.Column(db.SmallInteger, db.ForeignKey('admin.id'))
    admin_blog = db.relationship('Admin', back_populates='admin_blogs', foreign_keys=[admin_id])
    # 评论
    blog_comments = db.relationship('Comment', back_populates='blog_comment')
    # 板块
    plate_id = db.Column(db.SmallInteger, db.ForeignKey('plate.id'))
    plate_blog = db.relationship('Plate', back_populates='plate_blogs', foreign_keys=[plate_id])
    # 分类
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category_blog = db.relationship('Category', back_populates='category_blogs', foreign_keys=[category_id])
    # 标签
    tags = db.relationship('Tag', secondary=blog_tag, back_populates='blogs')

    @property
    def get_photo(self):
        content = self.content
        first = content.find('![')
        if first >= 0:
            # 取首图
            haide = content.find('(', first)
            end = content.find(')', first)
            url = content[haide + 1: end]
            print(first, end, url)
            return url
        else:
            # 可以在此设置随机的图片地址
            return "#"

    def get_add_time(self):
        return datetime.fromtimestamp(self.add_time)

    def get_up_time(self):
        return datetime.fromtimestamp(self.up_time)


class Photo(db.Model):
    """
    图片库，主要用作文章配图
    """
    id = db.Column(db.Integer, primary_key=True)
    # 最大支持15M
    photos = db.Column(db.LargeBinary(length=16777210))
    add_time = db.Column(db.Integer, default=shijc_now())
    use_count = db.Column(db.SmallInteger, default=0)
    look_count = db.Column(db.Integer, default=0)
    # 屏蔽状态
    status = db.Column(db.Boolean, default=False)

    # # @property
    # def get_photo(self):
    #     if self.photos:
    #         return pickle.loads(self.photos)
    #     else:
    #         return url_for('static', filename='images/upload.png')


class Tool(db.Model):
    """
    软件工具
    """
    id = db.Column(db.Integer, primary_key=True)
    ex_url = db.Column(db.String(250))
    local_url = db.Column(db.String(250))
    add_time = db.Column(db.Integer, default=shijc_now())
    use_count = db.Column(db.Integer, default=0)
    # 屏蔽状态
    status = db.Column(db.Boolean, default=False)


class Comment(db.Model):
    """
    评论
    """
    id = db.Column(db.Integer, primary_key=True)
    add_time = db.Column(db.Integer, default=shijc_now())
    mark = db.Column(db.Text)
    # 是否来自管理员
    from_admin = db.Column(db.Boolean, default=False)
    # 管理员是否已查阅
    reviewed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(15))
    email = db.Column(db.String(15))
    site = db.Column(db.String(50))
    avatar = db.Column(db.String(64))

    # 上级领导，自引用一对多关系
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))
    # 此为查询上级
    commented = db.relationship('Comment', back_populates='comments', remote_side=[id], foreign_keys=[comment_id])
    # 此为查询下级
    comments = db.relationship('Comment', back_populates='commented')

    # 评论域
    comment_yu = db.Column(db.String(10))
    # 文章
    blog_id = db.Column(db.Integer, db.ForeignKey('blog.id'))
    blog_comment = db.relationship('Blog', back_populates='blog_comments', foreign_keys=[blog_id])

    def __init__(self, **kwargs):
        super(Comment, self).__init__(**kwargs)
        self.generate_avatar()

    def generate_avatar(self):
        if self.from_admin:
            self.avatar = "admin.jpg"
        else:
            avatar = Identicon()
            filenames = avatar.generate(text=self.name)
            self.avatar = filenames[1]
            db.session.commit()

    def get_time(self):
        return datetime.fromtimestamp(self.add_time)


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
