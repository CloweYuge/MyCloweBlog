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


@login_required
@blog_bp.route("/add_post", methods=['POST', 'GET'])
def add_post():
    # print(request.args, request.form)
    if request.method == 'GET':
        # mod = request.args.get("mod", 0, type=int)
        plates = Plate.query.all()
        categorys = Category.query.all()
        return render_template("blog/add_post.html", plates=plates, categorys=categorys)
    elif request.method == 'POST':
        print(request.form)
        title = request.form.get("title", '')
        plate_id = request.form.get("plate_id", 0, type=int)
        category_id = request.form.get("category_id", 0, type=int)
        md_doc = request.form.get("mdeditor-markdown-doc", '')
        taginput = request.form.get("tagsinput", '')
        h_content = request.form.get("h_content", '')
        if title == '' or plate_id == 0 or category_id == 0 or md_doc == '':
            if title == '':
                return jsonify(status=400, info={'msg': '请填写标题！'})
            elif plate_id == 0:
                return jsonify(status=400, info={'msg': '请选择板块！'})
            elif category_id == 0:
                return jsonify(status=400, info={'msg': '请选择分类！'})
            elif md_doc == '':
                return jsonify(status=400, info={'msg': '填写文章内容！'})
            else:
                return jsonify(status=400, info={'msg': '请填写完整！'})
        if taginput != '':
            tags = taginput.split(",")
        else:
            tags = []
        try:
            plate = Plate.query.get(plate_id)
            category = Category.query.get(category_id)
            # 建立新文章
            # 这特么还是游客账户，没法绑定，得先做登录
            blog = Blog(admin_blog=current_user, title=title, content=md_doc, h_content=h_content, plate_blog=plate,
                        category_blog=category)
            if len(tags) > 0:
                # 已存在的标签
                tags_db = Tag.query.filter(Tag.name.in_(tags)).all()
                # 已存在的标签名
                tags_name = [t.name for t in tags_db]
                # 生成不存在的标签
                tags_new = [Tag(name=t) for t in tags if t not in tags_name]
                [db.session.add(t) for t in tags_new]
                # 关联到blog
                blog.tags = tags_new + tags_db
                print(tags_db, tags_name, tags_new)
            db.session.add(blog)
        except Exception as err:
            return jsonify(status=400, info={'msg': '发生错误：' + str(err)})
        else:
            db.session.commit()
            # blog.get_photo()
            return jsonify(status=200, info={'url': url_for("blog.blog_show", blog_id=blog.id)})
    return redirect_back()


@blog_bp.route("/blog_show")
def blog_show():
    print(request.args)
    blog = Blog.query.get(request.args.get("blog_id", 0, type=int))
    if blog:
        return render_template("blog/show_blog.html", blog=blog)

    return render_template("errors/404.html", msg="未找到文章信息！")


@blog_bp.route("/add_plate", methods=['POST'])
def add_plate():
    print(request.form)
    name = request.form.get("name", '')
    if name == '':
        return jsonify(status=400, info={'msg': 'fack none content'})
    plate = Plate.query.filter_by(name=name).first()
    if plate:
        return jsonify(status=400, info={'msg': '已存在'})
    elif plate is None:
        plate = Plate(name=name, mark=name + '专栏')
    try:
        db.session.add(plate)
        db.session.commit()
    except Exception as err:
        db.session.rollback()
        return jsonify(status=400, info={'msg': '发生错误：' + str(err)})
    else:
        return jsonify(status=200, info={'name': plate.name, 'id': plate.id})
    # return jsonify(status=400, info={'msg': '测试'})


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


@blog_bp.route("/add_category", methods=['POST'])
def add_category():
    print(request.form)
    name = request.form.get("name", '')
    plate = Plate.query.get(request.form.get("plate_id"))
    if plate is None:
        return jsonify(status=400, info={'msg': 'fack none plate!'})
    if name == '':
        return jsonify(status=400, info={'msg': 'fack none content!'})
    category = Category.query.filter_by(name=name).first()
    if category:
        return jsonify(status=400, info={'msg': '已存在'})
    elif category is None:
        category = Category(name=name, mark=name + '分类', plate_category=plate)
    try:
        db.session.add(category)
        db.session.commit()
    except Exception as err:
        db.session.rollback()
        return jsonify(status=400, info={'msg': '发生错误：' + str(err)})
    else:
        return jsonify(status=200, info={'name': category.name, 'id': category.id})
    # return jsonify(status=200, info={'name': '测试', 'id': '6'})


@csrf.exempt
@blog_bp.route("/img_up", methods=["POST"])
def img_up():
    print(request.form, request.files)
    img = request.files.get("editormd-image-file", None)
    if img is None:
        return jsonify(success=3, message="上传失败，无图像数据！", url="")
    photo = Photo(photos=img.read())
    db.session.add(photo)
    db.session.commit()
    url = url_for("blog.blog_img", imgid=photo.id, _external=True)
    return jsonify(success=1, message="上传成功！", url=url)


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
