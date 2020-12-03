import pickle
from flask import Blueprint, render_template, request, current_app, flash, redirect, \
    url_for, jsonify, Response, make_response
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
    category = Category.query.all()
    return render_template("blog/index.html", blogs=blogs, categorys=category)


@blog_bp.route("/blog_show")
def blog_show():
    print(request.args)
    blog = Blog.query.get(request.args.get("blog_id", 0, type=int))
    if blog:
        if current_user.is_authenticated is False:
            blog.look_count = blog.look_count + 1
            db.session.commit()
        return render_template("blog/show_blog.html", blog=blog)

    return render_template("errors/404.html", msg="未找到文章信息！")


@blog_bp.route("/plate_show")
def plate_show():
    plate = Plate.query.get(request.args.get("plate_id", 0, type=int))
    if plate:
        return render_template("blog/show_plate.html", plate=plate)

    return render_template("errors/404.html", msg="未找到板块信息！")


@blog_bp.route("/category_show")
def category_show():
    category = Category.query.get(request.args.get("category_id", 0, type=int))
    if category:
        return render_template("blog/show_category.html", category=category)

    return render_template("errors/404.html", msg="未找到板块信息！")


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
    print(request.form, request.cookies)
    msg = request.form

    # 用户内容
    name = msg.get("user_name")
    email = msg.get("user_email")
    site = msg.get("user_site")
    content = msg.get("content")
    blog = Blog.query.get(msg.get("blog_id", 0, type=int))

    # 生成储存数据
    ######
    # 关联信息
    position = msg.get("position", "left")
    re_comment = Comment.query.get(msg.get("reply", 0, type=int))
    if re_comment:
        if position == "left":
            po = "right"
        elif position == "right":
            po = "left"
        else:
            po = ''
        reply_id = str(re_comment.id)
        # 在此处调起回复通知，邮件or系统通知
    else:
        reply_id = ''
        po = "left"
    # 生成头像
    # avatar =
    comment = Comment(name=name, email=email, site=site, mark=content,
                      comment_yu=po, commented=re_comment, blog_comment=blog)
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as err:
        db.session.rollback()
        return jsonify(status=400, info={'msg': '发生错误：' + str(err)})
    else:
        print(type(comment.mark))
        html = "<div id=\"" + str(comment.id) + "\" replyid=\"" + reply_id + "\" " \
            "class=\"msg msg_" + comment.comment_yu + "\">\n" \
            "<img alt=\"" + comment.name + "\" src=\"/static/images/touxiangm.png\">\n" \
            "<div class=\"message\">" \
            "<span class=\"name\">" + comment.name + "</span>\n" \
            "<span class =\"time\">评论时间</span>" \
            "<a class =\"reply\" id=\"" + str(comment.id) + "\" " \
            "name=\"" + comment.name + "\" position=\"" + comment.comment_yu + "\">回复</a>" \
            "</div>" \
            "<div class=\"pneirong\"><i></i>" + comment.mark + "</div>\n" \
            "</div>"
        re = make_response(jsonify(status=200, msg='添加完成', html=html))
        re.set_cookie("comment_name", name)
        re.set_cookie('comment_email', email)
        re.set_cookie('comment_site', site)
        return re
