from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from mycloweblog.models import Blog, Category, Comment, Tag, Admin, Plate, Photo
# from mycloweblog.forms.admin import EditProfileAdminForm
from mycloweblog.extensions import db, csrf
from mycloweblog.decorators import permission_required, admin_required
from mycloweblog.utils import redirect_back


admin_bp = Blueprint('admin', __name__)


@admin_bp.route("/manage")
def manage_index():
    return render_template("")


@login_required
@admin_bp.route("/add_post", methods=['POST', 'GET'])
def add_post():
    # print(request.args, request.form)
    if request.method == 'GET':
        # mod = request.args.get("mod", 0, type=int)
        plates = Plate.query.all()
        categorys = Category.query.all()
        return render_template("admin/add_post.html", plates=plates, categorys=categorys)
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


@csrf.exempt
@admin_bp.route("/img_up", methods=["POST"])
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


@admin_bp.route("/add_plate", methods=['POST'])
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


@admin_bp.route("/add_category", methods=['POST'])
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


@admin_bp.route("/add_comment", methods=['POST'])
def add_comment():
    print(request.form)
    msg = request.form.get("content", "")

    html = "<div class='msg msg_left dropright'>" \
        "<img alt='暴躁少女' src='static/images/touxiangm.png'>" \
        "<span class='name'>暴躁少女</span>" \
        "<div class='dropdown-toggle' data-toggle='dropdown' aria-haspopup='true' aria-expanded='false'>" \
        "<i></i>" + msg + \
        "</div>" \
        "<div class='dropdown-menu'>" \
        "<button class='dropdown-item' type='button'>回复</button>" \
        "</div>" \
        "</div>"
    return jsonify(status=200, msg='添加完成', html=html)
