import os
from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from .extensions import db
from .models import Member
login_manager = LoginManager()
csrf = CSRFProtect()
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Member, int(user_id))
def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(SECRET_KEY=os.getenv('SECRET_KEY', 'dev-only-change-me'), SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL', 'sqlite:///community.db'), SQLALCHEMY_TRACK_MODIFICATIONS=False, MAX_CONTENT_LENGTH=25*1024*1024, S3_BUCKET_NAME=os.getenv('S3_BUCKET_NAME',''), AWS_REGION=os.getenv('AWS_REGION','ap-south-1'), ALLOWED_EXTENSIONS={'pdf','doc','docx','png','jpg','jpeg','txt'}, SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax', SESSION_COOKIE_SECURE=os.getenv('SESSION_COOKIE_SECURE','false').lower()=='true')
    if test_config: app.config.update(test_config)
    db.init_app(app); login_manager.init_app(app); login_manager.login_view='auth.login'; csrf.init_app(app)
    from .routes import main_bp
    from .auth import auth_bp
    app.register_blueprint(main_bp); app.register_blueprint(auth_bp)
    with app.app_context(): db.create_all()
    return app
