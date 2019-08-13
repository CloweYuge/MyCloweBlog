from flask import Blueprint, render_template, request, current_app, flash, redirect, url_for
from flask_login import login_required, current_user
from mycloweblog.models import Blog, Category, Comment, Tag, Admin
# from mycloweblog.forms.admin import EditProfileAdminForm
from mycloweblog.extensions import db
from mycloweblog.decorators import permission_required, admin_required
from mycloweblog.utils import redirect_back


auth_bp = Blueprint('auth', __name__)


@auth_bp.route("/login")
def login():
    pass
