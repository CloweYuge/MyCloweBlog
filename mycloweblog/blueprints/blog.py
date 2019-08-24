from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from mycloweblog.models import Blog, Category, Comment, Tag, Admin, Photo, Plate
# from mycloweblog.forms.admin import EditProfileAdminForm
from mycloweblog.extensions import db, csrf
from mycloweblog.decorators import permission_required, admin_required
from mycloweblog.utils import redirect_back


blog_bp = Blueprint('blog', __name__)


@blog_bp.route("/")
def index():
    return render_template("blog/index.html")


@blog_bp.route("/add_post", methods=['POST', 'GET'])
def add_post():
    if request.method == 'GET':
        mod = request.args.get("mod", 0, type=int)
        return render_template("blog/add_post.html")
    elif request.method == 'POST':
        print(request.form)
        title = request.form.get("title", '')
        plate_id = request.form.get("plate_id", 0, type=int)
        category_id = request.form.get("category_id", 0, type=int)
        md_doc = request.form.get("mdeditor-markdown-doc", '')
        taginput = request.form.get("tagsinput", '')
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
            plate = Plate.query.get("plate_id")
            category = Category.query.get("category_id")
            # 建立新文章
            blog = Blog(admin_blog=current_user, title=title, content=md_doc, plate_blog=plate, category_blog=category)
            if len(tags) > 0:
                # 已存在的标签
                tags_db = Tag.query.filter(Tag.name.in_(tags)).all()
                # 已存在的标签名
                tags_name = [t.name for t in tags_db]
                # 生成不存在的标签
                tags_new = [Tag(name=t) for t in tags if tags not in tags_name]
                [db.session.add(t) for t in tags_new]
                # 关联到blog
                blog.tags = tags_new + tags_db
            db.session.add(blog)
        except Exception as err:
            return jsonify(status=400, info={'msg': '发生错误：' + str(err)})
        else:
            db.session.commit()
            return jsonify(status=200, info={'url': url_for("blog.blog_show", blog_id=blog.id)})
    return redirect_back()


@blog_bp.route("/blog_show")
def blog_show():
    print(request.args)
    blog = Blog.query.get(request.args.get("blog_id"))
    if blog:
        return render_template("blog/show_blog.html", blog=blog)
    return render_template("errors/404.html")


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

    return jsonify(success=1, message="上传成功！", url="https://timgsa.baidu.com/timg?image&quality=80&size=b9999_"
                                                   "10000&sec=1567219745&di=a04552af92d7766423ad06e73312c533&imgtype="
                                                   "jpg&er=1&src=http%3A%2F%2Fb-ssl.duitang.com%2Fuploads%2Fitem%2F2"
                                                   "01508%2F18%2F20150818195900_kvAjB.jpeg")
