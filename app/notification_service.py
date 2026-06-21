from app.extensions import db
from app.models.financial import Notification


def create_notification(user_id, type, title, body, action_url=None,
                        related_entity_type=None, related_entity_id=None):
    notif = Notification(
        user_id=user_id,
        type=type,
        title=title,
        body=body,
        action_url=action_url,
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id,
    )
    db.session.add(notif)
    db.session.flush()
    return notif


def notify_new_quote(customer_user_id, request_title, request_id):
    return create_notification(
        user_id=customer_user_id,
        type='new_quote',
        title='New quote received',
        body=f'A pro submitted a quote for "{request_title}"',
        action_url=f'/customer/quotes/{request_id}',
        related_entity_type='service_request',
        related_entity_id=request_id,
    )


def notify_quote_accepted(pro_user_id, booking_id, request_title):
    return create_notification(
        user_id=pro_user_id,
        type='quote_accepted',
        title='Quote accepted!',
        body=f'Your quote for "{request_title}" was accepted',
        action_url=f'/pro/bookings/{booking_id}',
        related_entity_type='booking',
        related_entity_id=booking_id,
    )


def notify_booking_confirmed(customer_user_id, booking_id, request_title):
    return create_notification(
        user_id=customer_user_id,
        type='booking_confirmed',
        title='Booking confirmed',
        body=f'Your booking for "{request_title}" is confirmed',
        action_url=f'/customer/bookings/{booking_id}',
        related_entity_type='booking',
        related_entity_id=booking_id,
    )


def notify_booking_completed(customer_user_id, booking_id, pro_business_name):
    """
    Notifies the customer that their booking has been marked as complete.
    Uses type='booking_confirmed' as the closest available type until a
    'booking_completed' value is added to the CheckConstraint in a future migration.
    """
    return create_notification(
        user_id=customer_user_id,
        type='booking_confirmed',
        title='Job completed',
        body=f'{pro_business_name} marked your job as complete. Leave a review!',
        action_url=f'/customer/bookings/{booking_id}/review',
        related_entity_type='booking',
        related_entity_id=booking_id,
    )


def notify_pro_rejected(pro_user_id):
    """
    Notifies a pro that their profile was not approved.
    Uses type='pro_approved' as the closest available type until 'pro_rejected'
    is added to the CheckConstraint in a future migration.
    """
    return create_notification(
        user_id=pro_user_id,
        type='pro_approved',
        title='Profile not approved',
        body='Your professional profile was not approved. Contact support for details.',
        action_url='/pro/profile/edit',
        related_entity_type='pro_profile',
        related_entity_id=pro_user_id,
    )


def notify_review_received(pro_user_id, booking_id, pro_name):
    return create_notification(
        user_id=pro_user_id,
        type='review_received',
        title='New review received',
        body=f'{pro_name} left a review for your service',
        action_url=f'/pro/bookings/{booking_id}',
        related_entity_type='booking',
        related_entity_id=booking_id,
    )


def notify_pro_approved(pro_user_id):
    return create_notification(
        user_id=pro_user_id,
        type='pro_approved',
        title='Profile approved!',
        body='Your pro profile has been approved. You can now receive service requests.',
        action_url='/pro/dashboard',
        related_entity_type='pro_profile',
    )


def notify_booking_cancelled(pro_user_id, booking_id, request_title, reason=None):
    body = f'Booking for "{request_title}" was cancelled'
    if reason:
        body += f' — Reason: {reason}'
    return create_notification(
        user_id=pro_user_id,
        type='booking_cancelled',
        title='Booking cancelled',
        body=body,
        related_entity_type='booking',
        related_entity_id=booking_id,
    )


def notify_booking_cancelled_customer(customer_user_id, booking_id, request_title, reason=None):
    body = f'Booking for "{request_title}" was cancelled'
    if reason:
        body += f' — Reason: {reason}'
    return create_notification(
        user_id=customer_user_id,
        type='booking_cancelled',
        title='Booking cancelled',
        body=body,
        related_entity_type='booking',
        related_entity_id=booking_id,
    )


def notify_payment_received(pro_user_id, booking_id, amount, currency='GHS'):
    return create_notification(
        user_id=pro_user_id,
        type='payment_received',
        title='Payment received',
        body=f'A payment of {currency} {amount} has been received for booking',
        action_url=f'/pro/bookings/{booking_id}',
        related_entity_type='booking',
        related_entity_id=booking_id,
    )


def notify_payout_sent(pro_user_id, booking_id, amount):
    return create_notification(
        user_id=pro_user_id,
        type='payout_sent',
        title='Payout sent',
        body=f'Your payout of GHS {amount} has been disbursed',
        action_url=f'/pro/bookings/{booking_id}',
        related_entity_type='booking',
        related_entity_id=booking_id,
    )


def notify_booking_reminder(customer_user_id, booking_id, scheduled_date):
    return create_notification(
        user_id=customer_user_id,
        type='booking_reminder',
        title='Booking reminder',
        body=f'Reminder: You have a booking scheduled for {scheduled_date}',
        action_url=f'/customer/bookings/{booking_id}',
        related_entity_type='booking',
        related_entity_id=booking_id,
    )
