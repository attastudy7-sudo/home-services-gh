from datetime import datetime, timedelta

from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import CheckConstraint
import uuid


class ServiceRequest(db.Model):
    __tablename__ = 'service_requests'

    id                = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id       = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id', ondelete='SET NULL'))
    category_id       = db.Column(UUID(as_uuid=True), db.ForeignKey('service_categories.id'))
    subcategory_id    = db.Column(UUID(as_uuid=True), db.ForeignKey('service_subcategories.id'))
    location_index_id = db.Column(UUID(as_uuid=True), db.ForeignKey('location_index.id'))
    title             = db.Column(db.String(300), nullable=False)
    description       = db.Column(db.Text, nullable=False)
    location_lat      = db.Column(db.Float)
    location_lng      = db.Column(db.Float)
    location_from_gps = db.Column(db.Boolean, default=False)
    budget_min        = db.Column(db.Numeric(10, 2))
    budget_max        = db.Column(db.Numeric(10, 2))
    currency          = db.Column(db.String(5), default='GHS')
    preferred_date    = db.Column(db.Date)
    preferred_time_slot = db.Column(db.String(50))
    status            = db.Column(db.String(30), nullable=False, default='open')
    is_urgent         = db.Column(db.Boolean, default=False)
    quote_count       = db.Column(db.Integer, default=0)
    expires_at        = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=7))
    created_at        = db.Column(db.DateTime, server_default=db.func.now())
    updated_at        = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    __table_args__ = (
        CheckConstraint(
            "status IN ('open','matched','in_progress','completed','cancelled','expired')",
            name='chk_request_status'
        ),
        CheckConstraint(
            "preferred_time_slot IN ('morning','afternoon','evening','flexible')",
            name='chk_request_time_slot'
        ),
    )

    location = db.relationship('LocationIndex')
    category = db.relationship('ServiceCategory')
    quotes   = db.relationship('Quote', backref='request', lazy='dynamic')


class Quote(db.Model):
    __tablename__ = 'quotes'

    id              = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id      = db.Column(UUID(as_uuid=True), db.ForeignKey('service_requests.id', ondelete='CASCADE'))
    pro_id          = db.Column(UUID(as_uuid=True), db.ForeignKey('pro_profiles.id', ondelete='CASCADE'))
    amount          = db.Column(db.Numeric(10, 2), nullable=False)
    currency        = db.Column(db.String(5), default='GHS')
    message         = db.Column(db.Text, nullable=False)
    estimated_hours = db.Column(db.Integer)
    available_date  = db.Column(db.Date)
    status          = db.Column(db.String(30), nullable=False, default='pending')
    expires_at      = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=14))
    created_at      = db.Column(db.DateTime, server_default=db.func.now())
    updated_at      = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending','accepted','rejected','withdrawn','expired')",
            name='chk_quote_status'
        ),
        db.UniqueConstraint('request_id', 'pro_id', name='uq_one_quote_per_pro_per_request'),
    )

    booking = db.relationship('Booking', backref='quote', uselist=False)


class Booking(db.Model):
    __tablename__ = 'bookings'

    id                       = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id               = db.Column(UUID(as_uuid=True), db.ForeignKey('service_requests.id'))
    quote_id                 = db.Column(UUID(as_uuid=True), db.ForeignKey('quotes.id'), unique=True)
    customer_id              = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    pro_id                   = db.Column(UUID(as_uuid=True), db.ForeignKey('pro_profiles.id'))
    agreed_price             = db.Column(db.Numeric(10, 2), nullable=False)
    platform_commission_rate = db.Column(db.Numeric(5, 4), nullable=False, default=0.1500)
    platform_commission      = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    pro_payout_amount        = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    payout_status            = db.Column(db.String(30), nullable=False, default='pending')
    payment_method           = db.Column(db.String(30))
    payment_status           = db.Column(db.String(30), nullable=False, default='unpaid')
    payment_reference        = db.Column(db.String(255))
    scheduled_date           = db.Column(db.Date, nullable=False)
    scheduled_time_slot      = db.Column(db.String(50))
    status                   = db.Column(db.String(30), nullable=False, default='confirmed')
    cancellation_reason      = db.Column(db.Text)
    cancellation_by          = db.Column(db.String(20))
    completed_at             = db.Column(db.DateTime)
    started_at               = db.Column(db.DateTime)
    payout_disbursed_at      = db.Column(db.DateTime)
    created_at               = db.Column(db.DateTime, server_default=db.func.now())
    updated_at               = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    __table_args__ = (
        CheckConstraint(
            "payout_status IN ('pending','disbursed','held','refunded')",
            name='chk_booking_payout_status'
        ),
        CheckConstraint(
            "payment_method IN ('cash','momo','card')",
            name='chk_booking_payment_method'
        ),
        CheckConstraint(
            "payment_status IN ('unpaid','deposit_paid','paid','refunded','disputed')",
            name='chk_booking_payment_status'
        ),
        CheckConstraint(
            "status IN ('confirmed','in_progress','completed','cancelled','disputed')",
            name='chk_booking_status'
        ),
        CheckConstraint(
            "cancellation_by IN ('customer','pro','admin')",
            name='chk_booking_cancellation_by'
        ),
    )

    review   = db.relationship('Review', backref='booking', uselist=False)
    payments = db.relationship('Payment', backref='booking', lazy='dynamic')

    def calculate_financials(self, commission_rate=None):
        from flask import current_app
        rate = commission_rate or float(current_app.config['PLATFORM_COMMISSION_RATE'])
        self.platform_commission_rate = rate
        self.platform_commission = round(float(self.agreed_price) * rate, 2)
        self.pro_payout_amount = round(float(self.agreed_price) - self.platform_commission, 2)
