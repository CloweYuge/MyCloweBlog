from flask import url_for

from mycloweblog.extensions import db
from mycloweblog.models import Notification


def push_comment_notification(blog_id, receiver, page=1):
    message = '<a href="%s#comments">分享</a> 有了新的评论/回复.' % \
              (url_for('blog.show_blog', blog_id=blog_id, page=page))

    notification = Notification(message=message, receiver=receiver)
    db.session.add(notification)
    db.session.commit()

