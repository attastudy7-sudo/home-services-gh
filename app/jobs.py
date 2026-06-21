from datetime import datetime


def expire_stale_requests(app):
    """Mark open ServiceRequests past their expires_at as expired."""
    with app.app_context():
        from app.extensions import db
        from app.models.marketplace import ServiceRequest
        now = datetime.utcnow()
        stale = ServiceRequest.query.filter(
            ServiceRequest.status == 'open',
            ServiceRequest.expires_at < now,
        ).all()
        for req in stale:
            req.status = 'expired'
        if stale:
            db.session.commit()
            print(f'[scheduler] Expired {len(stale)} stale service requests.')


def expire_stale_quotes(app):
    """Mark pending Quotes past their expires_at as expired."""
    with app.app_context():
        from app.extensions import db
        from app.models.marketplace import Quote
        now = datetime.utcnow()
        stale = Quote.query.filter(
            Quote.status == 'pending',
            Quote.expires_at < now,
        ).all()
        for q in stale:
            q.status = 'expired'
        if stale:
            db.session.commit()
            print(f'[scheduler] Expired {len(stale)} stale quotes.')
