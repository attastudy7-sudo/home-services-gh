from app.extensions import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import CheckConstraint
import uuid


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id                = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email             = db.Column(db.String(255), unique=True, nullable=False)
    phone             = db.Column(db.String(20), unique=True, nullable=False)
    password_hash     = db.Column(db.String(255), nullable=False)
    full_name         = db.Column(db.String(150), nullable=False)
    role              = db.Column(db.String(10), nullable=False, default='user')
    ghana_card_number = db.Column(db.String(20))
    is_verified       = db.Column(db.Boolean, default=False)
    is_active         = db.Column(db.Boolean, default=True)
    profile_photo_url = db.Column(db.Text)
    created_at        = db.Column(db.DateTime, server_default=db.func.now())
    updated_at        = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    __table_args__ = (
        CheckConstraint("role IN ('user', 'admin')", name='chk_user_role'),
    )

    locations       = db.relationship('UserLocation', backref='user', lazy='dynamic')
    pro_profile     = db.relationship('ProProfile', backref='user', uselist=False)
    service_requests = db.relationship('ServiceRequest', backref='customer', lazy='dynamic')
    reviews_written = db.relationship('Review', foreign_keys='Review.reviewer_id', backref='reviewer', lazy='dynamic')
    notifications   = db.relationship('Notification', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_pro(self):
        return self.pro_profile is not None

    @property
    def is_admin(self):
        return self.role == 'admin'


@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(uuid.UUID(user_id))
    except (ValueError, TypeError):
        return None
