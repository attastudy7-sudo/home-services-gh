from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.blueprints.pro import pro_bp
from app.extensions import db
from app.models.pro import ProProfile, ProServiceArea, ProCategory, ProSubcategory
from app.models.marketplace import ServiceRequest, Quote, Booking
from app.models.financial import Review, Payment
from app.models.service import ServiceCategory, ServiceSubcategory
from app.models.location import LocationIndex
from app.helpers import coerce_uuid, coerce_date, coerce_money, coerce_int
from datetime import datetime
from functools import wraps
import re


def pro_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_pro:
            flash('You need a pro account to access this page.', 'danger')
            return redirect(url_for('customer.dashboard'))
        return f(*args, **kwargs)
    return decorated


@pro_bp.route('/dashboard')
@login_required
@pro_required
def dashboard():
    pro = current_user.pro_profile
    open_leads = (ServiceRequest.query
        .join(ProServiceArea, ProServiceArea.location_index_id == ServiceRequest.location_index_id)
        .join(ProCategory, ProCategory.pro_id == pro.id)
        .filter(
            ProServiceArea.pro_id == pro.id,
            ProCategory.category_id == ServiceRequest.category_id,
            ServiceRequest.status == 'open'
        ).count())
    active_bookings = Booking.query.filter_by(pro_id=pro.id, status='confirmed').count()
    pending_quotes = Quote.query.filter_by(pro_id=pro.id, status='pending').count()
    return render_template('pro/dashboard.html', pro=pro,
        open_leads=open_leads, active_bookings=active_bookings, pending_quotes=pending_quotes)


@pro_bp.route('/leads')
@login_required
@pro_required
def leads():
    pro = current_user.pro_profile
    leads = (ServiceRequest.query
        .join(ProServiceArea, ProServiceArea.location_index_id == ServiceRequest.location_index_id)
        .join(ProCategory, ProCategory.pro_id == pro.id)
        .filter(
            ProServiceArea.pro_id == pro.id,
            ProCategory.category_id == ServiceRequest.category_id,
            ServiceRequest.status == 'open'
        ).order_by(ServiceRequest.created_at.desc()).all())
    return render_template('pro/leads.html', leads=leads)


@pro_bp.route('/leads/<uuid:request_id>')
@login_required
@pro_required
def view_lead(request_id):
    req = ServiceRequest.query.get_or_404(request_id)
    existing_quote = Quote.query.filter_by(
        request_id=req.id, pro_id=current_user.pro_profile.id).first()
    return render_template('pro/view_lead.html', req=req, existing_quote=existing_quote)


@pro_bp.route('/leads/<uuid:request_id>/quote', methods=['GET', 'POST'])
@login_required
@pro_required
def submit_quote(request_id):
    req = ServiceRequest.query.get_or_404(request_id)
    if req.status != 'open':
        flash('This request is no longer accepting quotes.', 'danger')
        return redirect(url_for('pro.leads'))
    pro = current_user.pro_profile
    existing = Quote.query.filter_by(request_id=req.id, pro_id=pro.id).first()
    if existing:
        flash('You have already submitted a quote for this request.', 'info')
        return redirect(url_for('pro.view_lead', request_id=req.id))
    if request.method == 'POST':
        quote = Quote(
            request_id=req.id,
            pro_id=pro.id,
            amount=coerce_money(request.form.get('amount')),
            message=request.form.get('message', '').strip(),
            estimated_hours=coerce_int(request.form.get('estimated_hours')),
            available_date=coerce_date(request.form.get('available_date')),
        )
        req.quote_count += 1
        db.session.add(quote)
        db.session.commit()
        flash('Quote submitted successfully.', 'success')
        return redirect(url_for('pro.leads'))
    return render_template('pro/submit_quote.html', req=req)


@pro_bp.route('/quotes/<uuid:quote_id>/withdraw', methods=['POST'])
@login_required
@pro_required
def withdraw_quote(quote_id):
    quote = Quote.query.get_or_404(quote_id)
    if quote.pro_id != current_user.pro_profile.id:
        abort(403)
    if quote.status != 'pending':
        flash('Only pending quotes can be withdrawn.', 'danger')
        return redirect(url_for('pro.leads'))
    quote.status = 'withdrawn'
    db.session.commit()
    flash('Quote withdrawn.', 'info')
    return redirect(url_for('pro.leads'))


@pro_bp.route('/bookings')
@login_required
@pro_required
def my_bookings():
    bookings = Booking.query.filter_by(
        pro_id=current_user.pro_profile.id).order_by(Booking.created_at.desc()).all()
    return render_template('pro/my_bookings.html', bookings=bookings)


@pro_bp.route('/bookings/<uuid:booking_id>')
@login_required
@pro_required
def view_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.pro_id != current_user.pro_profile.id:
        abort(403)
    return render_template('pro/view_booking.html', booking=booking)


@pro_bp.route('/bookings/<uuid:booking_id>/complete', methods=['POST'])
@login_required
@pro_required
def mark_complete(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.pro_id != current_user.pro_profile.id:
        abort(403)
    if booking.status != 'in_progress':
        flash('Only in-progress bookings can be marked complete.', 'danger')
        return redirect(url_for('pro.view_booking', booking_id=booking.id))
    booking.status = 'completed'
    booking.completed_at = datetime.utcnow()
    booking.payout_status = 'pending'
    current_user.pro_profile.total_jobs += 1
    db.session.commit()
    flash('Booking marked as complete. Payout will be processed.', 'success')
    return redirect(url_for('pro.my_bookings'))


@pro_bp.route('/bookings/<uuid:booking_id>/cancel', methods=['POST'])
@login_required
@pro_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.pro_id != current_user.pro_profile.id:
        abort(403)
    if booking.status not in ('confirmed',):
        flash('This booking cannot be cancelled at this stage.', 'danger')
        return redirect(url_for('pro.view_booking', booking_id=booking.id))
    booking.status = 'cancelled'
    booking.cancellation_by = 'pro'
    booking.cancellation_reason = request.form.get('reason', '')
    db.session.commit()
    flash('Booking cancelled.', 'info')
    return redirect(url_for('pro.my_bookings'))


@pro_bp.route('/earnings')
@login_required
@pro_required
def earnings():
    pro = current_user.pro_profile
    completed = Booking.query.filter_by(pro_id=pro.id, status='completed').all()
    total_earned = sum(float(b.pro_payout_amount) for b in completed)
    disbursed = sum(float(b.pro_payout_amount) for b in completed if b.payout_status == 'disbursed')
    pending = sum(float(b.pro_payout_amount) for b in completed if b.payout_status == 'pending')
    return render_template('pro/earnings.html', pro=pro,
        completed=completed, total_earned=total_earned,
        disbursed=disbursed, pending=pending)


@pro_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@pro_required
def profile():
    pro = current_user.pro_profile
    if request.method == 'POST':
        pro.bio = request.form.get('bio', '').strip()
        pro.years_experience = int(request.form.get('years_experience', 0))
        pro.availability_note = request.form.get('availability_note', '').strip()
        pro.base_hourly_rate = coerce_money(request.form.get('base_hourly_rate'))
        db.session.commit()
        flash('Profile saved.', 'success')
        return redirect(url_for('pro.profile'))
    return render_template('pro/profile.html', pro=pro)


@pro_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
@pro_required
def edit_profile():
    pro = current_user.pro_profile
    if request.method == 'POST':
        pro.business_name = request.form.get('business_name', pro.business_name).strip()
        new_slug = re.sub(r'[^a-z0-9]+', '-', pro.business_name.lower()).strip('-')
        existing = ProProfile.query.filter(ProProfile.slug == new_slug, ProProfile.id != pro.id).first()
        if not existing:
            pro.slug = new_slug
        current_user.full_name = request.form.get('full_name', current_user.full_name).strip()
        current_user.phone = request.form.get('phone', current_user.phone).strip()
        db.session.commit()
        flash('Profile updated.', 'success')
        return redirect(url_for('pro.profile'))
    return render_template('pro/edit_profile.html', pro=pro)


@pro_bp.route('/<slug>')
def public_profile(slug):
    pro = ProProfile.query.filter_by(slug=slug, verification_status='approved').first_or_404()
    reviews = Review.query.filter_by(reviewee_id=pro.user_id).order_by(Review.created_at.desc()).limit(10).all()
    return render_template('pro/public_profile.html', pro=pro, reviews=reviews)
