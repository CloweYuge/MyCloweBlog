from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for
from flask_login import login_required, current_user, login_user, logout_user
from mycloweblog.models import Admin
from mycloweblog.forms.auth import LoginForm
# from mycloweblog.extensions import db
# from mycloweblog.decorators import permission_required, admin_required
from mycloweblog.utils import redirect_back


auth_bp = Blueprint('auth', __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('blog.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Admin.query.filter_by(username=form.username.data).first()
        if user:
            if user is not None and user.validate_password(form.password.data):
                if login_user(user, form.remember.data):
                    flash('欢迎回来~，' + user.username + '大人~', 'info')
                    return redirect_back()
                else:
                    flash('你的账户已经被锁定', 'warning')
                    return redirect(url_for('blog.index'))
            flash('用户名与密码不匹配！', 'warning')
        else:
            flash('没有该账号！', 'warning')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('已退出登录.', 'info')
    return redirect(url_for('auth.login'))
