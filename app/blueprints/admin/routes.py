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
    db.session.commit()
    flash(f'{pro.business_name or pro.user.full_name} approved.', 'success')
    return redirect(url_for('admin.pending_pros'))


@admin_bp.route('/pros/<uuid:pro_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject_pro(pro_id):
    pro = ProProfile.query.get_or_404(pro_id)
    pro.verification_status = 'rejected'
    log_action('reject_pro', 'pro_profile', pro.id, request.form.get('note', ''))
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


@admin_bp.route('/users')
@login_required
@admin_required
def list_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/list_users.html', users=users)


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
    bookings = Booking.query.order_by(Booking.created_at.desc()).limit(100).all()
    return render_template('admin/list_bookings.html', bookings=bookings)


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
    payments = Payment.query.order_by(Payment.initiated_at.desc()).limit(100).all()
    return render_template('admin/list_payments.html', payments=payments)


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
