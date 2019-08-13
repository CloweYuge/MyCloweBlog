try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin
import os
import uuid
import PIL
import time
from datetime import datetime
from PIL import Image
from flask import current_app, request, url_for, redirect, flash
from itsdangerous import BadSignature, SignatureExpired
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from mycloweblog.extensions import db
from mycloweblog.settings import Operations


def shijc_now():
    """
    直接返回当前时间的UTC时间戳
    :return:
    """
    return shijc_type(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), 'all')


def shijc_type(styletime, method):
    """
    转换格式时间为时间戳，返回10位秒精度时间戳
    :param styletime: "%Y-%m-%d %H:%M:%S"，格式字符类型的时间
    :param method: all, date, datetime
    :return: 10位秒精度时间戳
    """
    if styletime:                                                           # 转为时间数组
        if method == 'all':
            time_array = time.strptime(styletime, "%Y-%m-%d %H:%M:%S")
        elif method == 'date':
            time_array = time.strptime(styletime + ' 00:00:00', "%Y-%m-%d %H:%M:%S")
        elif method == 'datetime':
            time_array = time.strptime(styletime + ':00', "%Y-%m-%d %H:%M:%S")           # 转为时间戳
        else:
            return None
        timestamp = int(time.mktime(time_array))
        return timestamp
    return None


def rename_image(old_filename):
    ext = os.path.splitext(old_filename)[1]
    new_filename = uuid.uuid4().hex + ext
    return new_filename


def resize_image(image, filename, base_width):
    filename, ext = os.path.splitext(filename)
    img = Image.open(image)
    if img.size[0] > img.size[1]:
        type = 'h'
    elif img.size[0] == img.size[1]:
        type = 'z'
    else:
        type = 's'
    if img.size[0] <= base_width:
        return filename + ext, type
    w_percent = (base_width / float(img.size[0]))
    h_size = int((float(img.size[1]) * float(w_percent)))
    img = img.resize((base_width, h_size), PIL.Image.ANTIALIAS)

    filename += current_app.config['CLOWELOG_PHOTO_SUFFIX'][base_width] + ext
    img.save(os.path.join(current_app.config['CLOWELOG_UPLOAD_PATH'], filename), optimize=True, quality=85)
    return filename, type


def type_photo(image):
    img = Image.open(image)


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def redirect_back(default='blog.index', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))


def generate_token(user, operation, expire_in=None, **kwargs):
    s = Serializer(current_app.config['SECRET_KEY'], expire_in)

    data = {'id': user.id, 'operation': operation}
    data.update(**kwargs)
    return s.dumps(data)


# def validate_token(user, token, operation, new_password=None):
#     s = Serializer(current_app.config['SECRET_KEY'])
#
#     try:
#         data = s.loads(token)
#     except (SignatureExpired, BadSignature):
#         return False
#
#     if operation != data.get('operation') or user.id != data.get('id'):
#         return False
#
#     if operation == Operations.CONFIRM:
#         user.confirmed = True
#     elif operation == Operations.RESET_PASSWORD:
#         user.set_password(new_password)
#     elif operation == Operations.CHANGE_EMAIL:
#         new_email = data.get('new_email')
#         if new_email is None:
#             return False
#         if User.query.filter_by(email=new_email).first() is not None:
#             return False
#         user.email = new_email
#     else:
#         return False
#
#     db.session.commit()
#     return True


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"错误发生于 %s 失败 - %s" % (
                getattr(form, field).label.text,
                error
            ))