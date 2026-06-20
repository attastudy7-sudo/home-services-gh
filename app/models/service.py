from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID
import uuid


class ServiceCategory(db.Model):
    __tablename__ = 'service_categories'

    id         = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name       = db.Column(db.String(100), nullable=False)
    slug       = db.Column(db.String(120), nullable=False, unique=True)
    icon_url   = db.Column(db.Text)
    is_active  = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)

    subcategories = db.relationship('ServiceSubcategory', backref='category', lazy='dynamic')


class ServiceSubcategory(db.Model):
    __tablename__ = 'service_subcategories'

    id          = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = db.Column(UUID(as_uuid=True), db.ForeignKey('service_categories.id', ondelete='CASCADE'))
    name        = db.Column(db.String(150), nullable=False)
    slug        = db.Column(db.String(200), nullable=False, unique=True)
    is_active   = db.Column(db.Boolean, default=True)
