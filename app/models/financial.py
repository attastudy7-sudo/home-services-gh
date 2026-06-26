from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import CheckConstraint
import uuid


class Review(db.Model):
    __tablename__ = 'reviews'

    id          = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id  = db.Column(UUID(as_uuid=True), db.ForeignKey('bookings.id'), unique=True)
    reviewer_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    reviewee_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    rating      = db.Column(db.Integer, nullable=False)
    comment     = db.Column(db.Text)
    created_at  = db.Column(db.DateTime, server_default=db.func.now())

    __table_args__ = (
        CheckConstraint('rating BETWEEN 1 AND 5', name='chk_review_rating'),
    )


class Payment(db.Model):
    __tablename__ = 'payments'

    id                = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id        = db.Column(UUID(as_uuid=True), db.ForeignKey('bookings.id'))
    payer_id          = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    amount            = db.Column(db.Numeric(10, 2), nullable=False)
    currency          = db.Column(db.String(5), default='GHS')
    gateway           = db.Column(db.String(30), default='paystack')
    gateway_ref       = db.Column(db.String(255))
    gateway_status    = db.Column(db.String(50))
    gateway_response  = db.Column(db.Text)
    type              = db.Column(db.String(30))
    status            = db.Column(db.String(30), nullable=False, default='pending')
    momo_network      = db.Column(db.String(10))
    payer_momo_number = db.Column(db.String(20))
    callback_received = db.Column(db.Boolean, default=False)
    callback_at       = db.Column(db.DateTime)
    initiated_at      = db.Column(db.DateTime, server_default=db.func.now())
    confirmed_at      = db.Column(db.DateTime)

    __table_args__ = (
        CheckConstraint("gateway IN ('paystack','cash')", name='chk_payment_gateway'),
        CheckConstraint("type IN ('deposit','full_payment','refund')", name='chk_payment_type'),
        CheckConstraint("status IN ('pending','success','failed','refunded')", name='chk_payment_status'),
        CheckConstraint("momo_network IN ('mtn','telecel','at')", name='chk_payment_momo_network'),
    )


class Notification(db.Model):
    __tablename__ = 'notifications'

    id                  = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id             = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id', ondelete='CASCADE'))
    type                = db.Column(db.String(50), nullable=False)
    title               = db.Column(db.String(255), nullable=False)
    body                = db.Column(db.Text, nullable=False)
    action_url          = db.Column(db.String(500))
    related_entity_type = db.Column(db.String(50))
    related_entity_id   = db.Column(UUID(as_uuid=True))
    is_read             = db.Column(db.Boolean, default=False)
    created_at          = db.Column(db.DateTime, server_default=db.func.now())

    __table_args__ = (
        CheckConstraint(
            "type IN ('new_quote','quote_accepted','booking_confirmed','booking_reminder',"
            "'review_received','pro_approved','booking_cancelled','payment_received','payout_sent',"
            "'booking_completed','pro_rejected')",
            name='chk_notification_type'
        ),
    )
