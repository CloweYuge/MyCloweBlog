from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from mycloweblog.models import Blog, Category, Comment, Tag, Admin, Photo, Plate
# from mycloweblog.forms.admin import EditProfileAdminForm
from mycloweblog.extensions import db
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
            return jsonify(status=400, info={'msg': '请填写完整！'})
        if taginput != '':
            tags = taginput.split(",")
        else:
            tags = []
        try:
            plate = Plate.query.get("plate_id")
            category = Category.query.get("category_id")

            blog = Blog(admin_blog=current_user, title=title, content=md_doc, plate_blog=plate, category_blog=category)
            if len(tags) > 0:
                # 已存在的标签
                tags_db = Tag.query.filter(Tag.name.in_(tags)).all()
                # 已存在的标签名
                tags_name = [t.name for t in tags_db]
                # 生成不存在的标签
                tags_new = [Tag(name=t) for t in tags if tags not in tags_name]
                [db.session.add(t) for t in tags_new]
                # 关联blog
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
    return jsonify(status=200, info={'name': '测试', 'id': '5'})
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
    return jsonify(status=200, info={'name': '测试', 'id': '6'})
