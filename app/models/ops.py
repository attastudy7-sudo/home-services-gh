from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import CheckConstraint
import uuid


class AdminAction(db.Model):
    __tablename__ = 'admin_actions'

    id          = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    admin_id    = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    action_type = db.Column(db.String(80), nullable=False)
    entity_type = db.Column(db.String(50), nullable=False)
    entity_id   = db.Column(UUID(as_uuid=True), nullable=False)
    note        = db.Column(db.Text)
    created_at  = db.Column(db.DateTime, server_default=db.func.now())

    __table_args__ = (
        CheckConstraint(
            "action_type IN ('approve_pro','reject_pro','suspend_user',"
            "'resolve_dispute','refund_payment','override_status')",
            name='chk_admin_action_type'
        ),
    )
