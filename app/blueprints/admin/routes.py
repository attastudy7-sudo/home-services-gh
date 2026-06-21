from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.blueprints.admin import admin_bp
from app.extensions import db
from app.models.user import User
from app.models.pro import ProProfile
from app.models.marketplace import Booking
from app.models.financial import Payment
from app.models.service import ServiceCategory
from app.models.ops import AdminAction
from datetime import datetime, timedelta
from functools import wraps
from app.notification_service import notify_pro_approved, notify_pro_rejected, notify_payout_sent
import re


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated


def log_action(action_type, entity_type, entity_id, note=''):
    action = AdminAction(
        admin_id=current_user.id,
        action_type=action_type,
        entity_type=entity_type,
        entity_id=entity_id,
        note=note
    )
    db.session.add(action)


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    pending_pros = ProProfile.query.filter_by(verification_status='pending').count()
    total_users = User.query.count()
    active_bookings = Booking.query.filter_by(status='confirmed').count()
    stalled_payments = Payment.query.filter(
        Payment.gateway == 'paystack',
        Payment.callback_received == False,
        Payment.initiated_at < datetime.utcnow() - timedelta(hours=2),
        Payment.status == 'pending'
    ).count()
    return render_template('admin/dashboard.html',
        pending_pros=pending_pros, total_users=total_users,
        active_bookings=active_bookings, stalled_payments=stalled_payments)


@admin_bp.route('/pros/pending')
@login_required
@admin_required
def pending_pros():
    pros = ProProfile.query.filter_by(verification_status='pending').order_by(ProProfile.created_at).all()
    return render_template('admin/pending_pros.html', pros=pros)


@admin_bp.route('/pros/<uuid:pro_id>')
@login_required
@admin_required
def view_pro(pro_id):
    pro = ProProfile.query.get_or_404(pro_id)
    return render_template('admin/view_pro.html', pro=pro)


@admin_bp.route('/pros/<uuid:pro_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_pro(pro_id):
    pro = ProProfile.query.get_or_404(pro_id)
    pro.verification_status = 'approved'
    pro.verified_at = datetime.utcnow()
    log_action('approve_pro', 'pro_profile', pro.id, request.form.get('note', ''))
    notify_pro_approved(pro.user_id)
    db.session.commit()
    flash(f'{pro.business_name or pro.user.full_name} approved.', 'success')
    return redirect(url_for('admin.pending_pros'))


@admin_bp.route('/pros/<uuid:pro_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_pro(pro_id):
    pro = ProProfile.query.get_or_404(pro_id)
    pro.verification_status = 'rejected'
    pro.slug = f'rejected-{pro.id}'
    log_action('reject_pro', 'pro_profile', pro.id, request.form.get('note', ''))
    notify_pro_rejected(pro_user_id=pro.user_id)
    db.session.commit()
    flash('Pro rejected.', 'info')
    return redirect(url_for('admin.pending_pros'))


@admin_bp.route('/pros/<uuid:pro_id>/suspend', methods=['POST'])
@login_required
@admin_required
def suspend_pro(pro_id):
    pro = ProProfile.query.get_or_404(pro_id)
    pro.verification_status = 'suspended'
    log_action('suspend_user', 'pro_profile', pro.id, request.form.get('note', ''))
    db.session.commit()
    flash('Pro suspended.', 'warning')
    return redirect(url_for('admin.view_pro', pro_id=pro.id))


PAGE_SIZE = 50


@admin_bp.route('/users')
@login_required
@admin_required
def list_users():
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.created_at.desc()).paginate(page=page, per_page=PAGE_SIZE, error_out=False)
    users = pagination.items
    return render_template('admin/list_users.html', users=users, pagination=pagination)


@admin_bp.route('/users/<uuid:user_id>')
@login_required
@admin_required
def view_user(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('admin/view_user.html', user=user)


@admin_bp.route('/users/<uuid:user_id>/suspend', methods=['POST'])
@login_required
@admin_required
def suspend_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = False
    log_action('suspend_user', 'user', user.id, request.form.get('note', ''))
    db.session.commit()
    flash(f'User {user.email} suspended.', 'warning')
    return redirect(url_for('admin.list_users'))


@admin_bp.route('/bookings')
@login_required
@admin_required
def list_bookings():
    page = request.args.get('page', 1, type=int)
    pagination = Booking.query.order_by(Booking.created_at.desc()).paginate(page=page, per_page=PAGE_SIZE, error_out=False)
    bookings = pagination.items
    return render_template('admin/list_bookings.html', bookings=bookings, pagination=pagination)


@admin_bp.route('/bookings/<uuid:booking_id>')
@login_required
@admin_required
def view_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    return render_template('admin/view_booking.html', booking=booking)


@admin_bp.route('/bookings/<uuid:booking_id>/resolve-dispute', methods=['POST'])
@login_required
@admin_required
def resolve_dispute(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    resolution = request.form.get('resolution', 'completed')
    booking.status = resolution
    log_action('resolve_dispute', 'booking', booking.id, request.form.get('note', ''))
    db.session.commit()
    flash('Dispute resolved.', 'success')
    return redirect(url_for('admin.view_booking', booking_id=booking.id))


@admin_bp.route('/payments')
@login_required
@admin_required
def list_payments():
    page = request.args.get('page', 1, type=int)
    pagination = Payment.query.order_by(Payment.initiated_at.desc()).paginate(page=page, per_page=PAGE_SIZE, error_out=False)
    payments = pagination.items
    return render_template('admin/list_payments.html', payments=payments, pagination=pagination)


@admin_bp.route('/payments/stalled-momo')
@login_required
@admin_required
def stalled_momo():
    stalled = Payment.query.filter(
        Payment.gateway == 'paystack',
        Payment.callback_received == False,
        Payment.initiated_at < datetime.utcnow() - timedelta(hours=2),
        Payment.status == 'pending'
    ).order_by(Payment.initiated_at).all()
    return render_template('admin/stalled_momo.html', payments=stalled)


@admin_bp.route('/payouts')
@login_required
@admin_required
def list_pending_payouts():
    pending = Booking.query.filter(
        Booking.status == 'completed',
        Booking.payout_status == 'pending'
    ).order_by(Booking.completed_at).all()
    return render_template('admin/list_pending_payouts.html', bookings=pending)


@admin_bp.route('/payouts/<uuid:booking_id>/disburse', methods=['POST'])
@login_required
@admin_required
def disburse_payout(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.payout_status != 'pending':
        flash('Payout already processed for this booking.', 'warning')
        return redirect(url_for('admin.list_pending_payouts'))
    print(f'[PAYSTACK STUB] Disbursing GHS {booking.pro_payout_amount} to pro {booking.pro_id}')
    booking.payout_status = 'disbursed'
    booking.payout_disbursed_at = datetime.utcnow()
    log_action('override_status', 'booking', booking.id, 'Payout disbursed')
    notify_payout_sent(booking.quote.pro.user_id, booking.id, booking.pro_payout_amount)
    db.session.commit()
    flash(f'Payout of GHS {booking.pro_payout_amount} disbursed.', 'success')
    return redirect(url_for('admin.list_pending_payouts'))


@admin_bp.route('/categories')
@login_required
@admin_required
def list_categories():
    categories = ServiceCategory.query.order_by(ServiceCategory.sort_order).all()
    return render_template('admin/list_categories.html', categories=categories)


@admin_bp.route('/categories/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_category():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
        if ServiceCategory.query.filter_by(slug=slug).first():
            flash(f'A category with slug "{slug}" already exists.', 'danger')
            return redirect(url_for('admin.new_category'))
        if not slug:
            flash('Category name cannot be empty.', 'danger')
            return redirect(url_for('admin.new_category'))
        cat = ServiceCategory(name=name, slug=slug)
        db.session.add(cat)
        db.session.commit()
        flash(f'Category "{name}" created.', 'success')
        return redirect(url_for('admin.list_categories'))
    return render_template('admin/new_category.html')


@admin_bp.route('/categories/<uuid:category_id>/toggle', methods=['POST'])
@login_required
@admin_required
def toggle_category(category_id):
    cat = ServiceCategory.query.get_or_404(category_id)
    cat.is_active = not cat.is_active
    db.session.commit()
    state = 'activated' if cat.is_active else 'deactivated'
    flash(f'Category "{cat.name}" {state}.', 'info')
    return redirect(url_for('admin.list_categories'))
