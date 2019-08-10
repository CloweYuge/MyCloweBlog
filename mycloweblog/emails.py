from threading import Thread
from flask import render_template
from flask import url_for, current_app
from flask_mail import Message
from mycloweblog.error import EmailSendError

from mycloweblog.extensions import mail


def _send_async_mail(app, message):
    with app.app_context():
        try:
            mail.send(message)
        except Exception as err:
            raise EmailSendError(str(err))
        else:
            return True


def send_mail(to, subject, template, **kwargs):
    message = Message(current_app.config['JKANGWEB_MAIL_SUBJECT_PREFIX'] + subject, recipients=[to])
    message.body = render_template(template + '.txt', **kwargs)
    message.html = render_template(template + '.html', **kwargs)
    app = current_app._get_current_object()
    thr = Thread(target=_send_async_mail, args=[app, message])
    thr.start()
    return thr


def send_login_email(user, token, to=None):
    send_mail(subject='-登录验证码', to=to or user.email, template='emails/login', user=user, token=token)


def send_find_password_email(user, token, to=None):
    send_mail(subject='-找回密码验证码', to=to or user.email, template='emails/login', user=user, token=token)
#
# def send_confirm_email(user, token, to=None):
#     send_mail(subject='Email Confirm', to=to or user.email, template='emails/confirm', user=user, token=token)
#
#
# def send_reset_password_email(user, token):
#     send_mail(subject='Password Reset', to=user.email, template='emails/reset_password', user=user, token=token)
