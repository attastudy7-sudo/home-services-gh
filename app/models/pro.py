from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import CheckConstraint
import uuid


class ProProfile(db.Model):
    __tablename__ = 'pro_profiles'

    id                  = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id             = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id', ondelete='CASCADE'), unique=True)
    business_name       = db.Column(db.String(200))
    slug                = db.Column(db.String(220), unique=True)
    bio                 = db.Column(db.Text)
    years_experience    = db.Column(db.Integer, default=0)
    certificate_url     = db.Column(db.Text)
    ghana_card_url      = db.Column(db.Text)
    verification_status = db.Column(db.String(30), nullable=False, default='pending')
    avg_rating          = db.Column(db.Float, default=0.0)
    total_reviews       = db.Column(db.Integer, default=0)
    total_jobs          = db.Column(db.Integer, default=0)
    is_available        = db.Column(db.Boolean, default=True)
    availability_note   = db.Column(db.String(255))
    base_hourly_rate    = db.Column(db.Numeric(10, 2))
    verified_at         = db.Column(db.DateTime)
    created_at          = db.Column(db.DateTime, server_default=db.func.now())
    updated_at          = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    __table_args__ = (
        CheckConstraint(
            "verification_status IN ('pending','approved','rejected','suspended')",
            name='chk_pro_verification_status'
        ),
    )

    categories    = db.relationship('ProCategory', backref='pro', lazy='dynamic')
    subcategories = db.relationship('ProSubcategory', backref='pro', lazy='dynamic')
    service_areas = db.relationship('ProServiceArea', backref='pro', lazy='dynamic')
    quotes        = db.relationship('Quote', backref='pro', lazy='dynamic')


class ProCategory(db.Model):
    __tablename__ = 'pro_categories'

    pro_id      = db.Column(UUID(as_uuid=True), db.ForeignKey('pro_profiles.id', ondelete='CASCADE'), primary_key=True)
    category_id = db.Column(UUID(as_uuid=True), db.ForeignKey('service_categories.id', ondelete='CASCADE'), primary_key=True)


class ProSubcategory(db.Model):
    __tablename__ = 'pro_subcategories'

    pro_id         = db.Column(UUID(as_uuid=True), db.ForeignKey('pro_profiles.id', ondelete='CASCADE'), primary_key=True)
    subcategory_id = db.Column(UUID(as_uuid=True), db.ForeignKey('service_subcategories.id', ondelete='CASCADE'), primary_key=True)


class ProServiceArea(db.Model):
    __tablename__ = 'pro_service_areas'

    id                = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pro_id            = db.Column(UUID(as_uuid=True), db.ForeignKey('pro_profiles.id', ondelete='CASCADE'))
    location_index_id = db.Column(UUID(as_uuid=True), db.ForeignKey('location_index.id', ondelete='CASCADE'))
    radius_km         = db.Column(db.Integer, default=5)
    latitude          = db.Column(db.Float)
    longitude         = db.Column(db.Float)

    location = db.relationship('LocationIndex')
