from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_ckeditor import CKEditor
from flask_moment import Moment
from flask_login import LoginManager, AnonymousUserMixin
from flask_wtf import CSRFProtect
from flask_dropzone import Dropzone
from flask_avatars import Avatars
from flask_migrate import Migrate
from flask_whooshee import Whooshee

bootstrap = Bootstrap()
db = SQLAlchemy()
moment = Moment()
ckeditor = CKEditor()
mail = Mail()
login_manager = LoginManager()
csrf = CSRFProtect()
dropzone = Dropzone()
avatars = Avatars()
migrate = Migrate()
whooshee = Whooshee()

login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'
login_manager.refresh_view = 'auth.re_authenticate'
login_manager.needs_refresh_message = u'为了保护你的账户安全，请重新登录认证'
login_manager.needs_refresh_message_category = 'warning'
login_manager.login_message = '请先登录'


@login_manager.user_loader
def load_user(aid):
    from mycloweblog.models import Admin
    user = Admin.query.get(int(aid))
    return user


class Guest(AnonymousUserMixin):    # 访客拥有的类与权限，默认全部为False
    @property
    def is_admin(self):
        return False


login_manager.anonymous_user = Guest