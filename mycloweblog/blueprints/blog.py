import pickle
from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for, jsonify, Response
from flask_login import login_required, current_user
from mycloweblog.models import Blog, Category, Comment, Tag, Admin, Photo, Plate
# from mycloweblog.forms.admin import EditProfileAdminForm
from mycloweblog.extensions import db, csrf
from mycloweblog.decorators import permission_required, admin_required
from mycloweblog.utils import redirect_back


blog_bp = Blueprint('blog', __name__)


@blog_bp.route("/")
def index():
    blogs = Blog.query.all()
    return render_template("blog/index.html", blogs=blogs)


@blog_bp.route("/blog_show")
def blog_show():
    print(request.args)
    blog = Blog.query.get(request.args.get("blog_id", 0, type=int))
    if blog:
        return render_template("blog/show_blog.html", blog=blog)

    return render_template("errors/404.html", msg="未找到文章信息！")


@blog_bp.route("/get_plate_category")
def get_plate_category():
    print(request.args)
    plate = Plate.query.get(request.args.get("pid"))
    if plate:
        ids = [c.id for c in plate.plate_categorys]
        names = [c.name for c in plate.plate_categorys]
        return jsonify(status='ok', info={'ids': ids, 'names': names})
    else:
        return jsonify(status='ok', info={'msg': '未找到板块信息！'})


@blog_bp.route("/blog_img")
def blog_img():
    print(request.args)
    img_id = request.args.get("imgid", None)
    if img_id:
        photo = Photo.query.get(img_id)
        if photo:
            img = photo.photos
            # byte_io = BytesIO()
            # img.save(byte_io, 'PNG')
            # byte_io.seek(0)

            return Response(img, mimetype="image/jpeg")
            # return img
        return url_for('static', filename='images/upload.png')
    return url_for('static', filename='images/upload.png')


@blog_bp.route("/add_comment", methods=['POST'])
def add_comment():
    print(request.form)
    msg = request.form

    # 用户内容
    name = msg.get("user_name")
    email = msg.get("user_email")
    site = msg.get("user_site")
    content = msg.get("content")
    # 生成储存数据
    ######
    # 关联信息
    position = msg.get("position", "left")
    drop = msg.get("drop", "right")
    if msg.get("reply") == "true":
        reply = True
        # 回复对象
        reply_user = msg.get("reply_user")
        number = msg.get("number")
        # 调起回复通知，邮件or系统通知
    elif msg.get("reply") == "false":
        reply = False

    return jsonify(status=200, msg='添加完成', info={"content": content, "name": name}, position=position, drop=drop)
