from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db
class Member(UserMixin, db.Model):
    __tablename__='members'
    id=db.Column(db.BigInteger().with_variant(db.Integer,'sqlite'), primary_key=True)
    full_name=db.Column(db.String(150), nullable=False)
    email=db.Column(db.String(254), nullable=False, unique=True, index=True)
    phone=db.Column(db.String(30)); city=db.Column(db.String(100)); skills=db.Column(db.Text)
    experience_years=db.Column(db.Numeric(4,1)); password_hash=db.Column(db.String(255), nullable=False)
    created_at=db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    files=db.relationship('UploadedFile', back_populates='member', cascade='all, delete-orphan')
    def set_password(self, password): self.password_hash=generate_password_hash(password)
    def check_password(self, password): return check_password_hash(self.password_hash, password)
class UploadedFile(db.Model):
    __tablename__='uploaded_files'
    id=db.Column(db.BigInteger().with_variant(db.Integer,'sqlite'), primary_key=True)
    member_id=db.Column(db.BigInteger, db.ForeignKey('members.id'), nullable=False, index=True)
    original_filename=db.Column(db.String(255), nullable=False); s3_key=db.Column(db.String(1024), nullable=False, unique=True)
    content_type=db.Column(db.String(150)); file_size=db.Column(db.BigInteger, nullable=False)
    created_at=db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    member=db.relationship('Member', back_populates='files')
