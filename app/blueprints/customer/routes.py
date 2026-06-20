from flask import render_template, redirect, url_for, flash, request, session, abort
from flask_login import login_required, current_user
from app.blueprints.customer import customer_bp
from app.extensions import db
from app.models.marketplace import ServiceRequest, Quote, Booking
from app.models.financial import Review
from app.models.service import ServiceCategory, ServiceSubcategory
from app.models.location import LocationIndex
from app.helpers import coerce_uuid, coerce_date, coerce_money, coerce_float


@customer_bp.route('/dashboard')
@login_required
def dashboard():
    open_requests = ServiceRequest.query.filter_by(
        customer_id=current_user.id, status='open').count()
    active_bookings = Booking.query.filter_by(
        customer_id=current_user.id, status='confirmed').count()
    return render_template('customer/dashboard.html',
        open_requests=open_requests, active_bookings=active_bookings)


@customer_bp.route('/post-request', methods=['GET', 'POST'])
@login_required
def post_request():
    categories = ServiceCategory.query.filter_by(is_active=True).order_by(ServiceCategory.sort_order).all()
    locations = LocationIndex.query.filter_by(is_active=True).order_by(LocationIndex.city, LocationIndex.area_name).all()
    if request.method == 'POST':
        req = ServiceRequest(
            customer_id=current_user.id,
            category_id=coerce_uuid(request.form.get('category_id')),
            subcategory_id=coerce_uuid(request.form.get('subcategory_id')),
            location_index_id=coerce_uuid(request.form.get('location_index_id')),
            title=request.form.get('title', '').strip(),
            description=request.form.get('description', '').strip(),
            budget_min=coerce_money(request.form.get('budget_min')),
            budget_max=coerce_money(request.form.get('budget_max')),
            preferred_date=coerce_date(request.form.get('preferred_date')),
            preferred_time_slot=request.form.get('preferred_time_slot') or None,
            is_urgent=bool(request.form.get('is_urgent')),
            location_from_gps=bool(request.form.get('location_from_gps')),
            location_lat=coerce_float(request.form.get('location_lat')),
            location_lng=coerce_float(request.form.get('location_lng')),
        )
        db.session.add(req)
        db.session.commit()
        flash('Request posted. Pros in your area will submit quotes.', 'success')
        return redirect(url_for('customer.view_request', request_id=req.id))
    return render_template('customer/post_request.html', categories=categories, locations=locations)


@customer_bp.route('/requests')
@login_required
def my_requests():
    requests = ServiceRequest.query.filter_by(
        customer_id=current_user.id).order_by(ServiceRequest.created_at.desc()).all()
    return render_template('customer/my_requests.html', requests=requests)


@customer_bp.route('/requests/<uuid:request_id>')
@login_required
def view_request(request_id):
    req = ServiceRequest.query.get_or_404(request_id)
    if req.customer_id != current_user.id:
        abort(403)
    quotes = Quote.query.filter_by(request_id=req.id).all()
    return render_template('customer/view_request.html', req=req, quotes=quotes)


@customer_bp.route('/requests/<uuid:request_id>/cancel', methods=['POST'])
@login_required
def cancel_request(request_id):
    req = ServiceRequest.query.get_or_404(request_id)
    if req.customer_id != current_user.id:
        abort(403)
    if req.status not in ('open', 'matched'):
        flash('This request cannot be cancelled at this stage.', 'danger')
        return redirect(url_for('customer.view_request', request_id=req.id))
    req.status = 'cancelled'
    db.session.commit()
    flash('Request cancelled.', 'info')
    return redirect(url_for('customer.my_requests'))


@customer_bp.route('/quotes/<uuid:request_id>')
@login_required
def view_quotes(request_id):
    req = ServiceRequest.query.get_or_404(request_id)
    if req.customer_id != current_user.id:
        abort(403)
    quotes = Quote.query.filter_by(request_id=req.id, status='pending').all()
    return render_template('customer/view_quotes.html', req=req, quotes=quotes)


@customer_bp.route('/quotes/<uuid:quote_id>/accept', methods=['POST'])
@login_required
def accept_quote(quote_id):
    quote = Quote.query.get_or_404(quote_id)
    req = ServiceRequest.query.get_or_404(quote.request_id)
    if req.customer_id != current_user.id:
        abort(403)
    booking = Booking(
        request_id=req.id,
        quote_id=quote.id,
        customer_id=current_user.id,
        pro_id=quote.pro_id,
        agreed_price=quote.amount,
        scheduled_date=quote.available_date,
        payment_method=request.form.get('payment_method', 'cash'),
    )
    booking.calculate_financials()
    quote.status = 'accepted'
    req.status = 'matched'
    Quote.query.filter(
        Quote.request_id == req.id,
        Quote.id != quote.id,
        Quote.status == 'pending'
    ).update({'status': 'rejected'})
    db.session.add(booking)
    db.session.commit()
    flash('Quote accepted. Booking confirmed!', 'success')
    return redirect(url_for('customer.view_booking', booking_id=booking.id))


@customer_bp.route('/bookings')
@login_required
def my_bookings():
    bookings = Booking.query.filter_by(
        customer_id=current_user.id).order_by(Booking.created_at.desc()).all()
    return render_template('customer/my_bookings.html', bookings=bookings)


@customer_bp.route('/bookings/<uuid:booking_id>')
@login_required
def view_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.customer_id != current_user.id:
        abort(403)
    review = Review.query.filter_by(booking_id=booking.id).first()
    return render_template('customer/view_booking.html', booking=booking, review=review)


@customer_bp.route('/bookings/<uuid:booking_id>/cancel', methods=['POST'])
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.customer_id != current_user.id:
        abort(403)
    if booking.status not in ('confirmed',):
        flash('This booking cannot be cancelled at this stage.', 'danger')
        return redirect(url_for('customer.view_booking', booking_id=booking.id))
    booking.status = 'cancelled'
    booking.cancellation_by = 'customer'
    booking.cancellation_reason = request.form.get('reason', '')
    db.session.commit()
    flash('Booking cancelled.', 'info')
    return redirect(url_for('customer.my_bookings'))


@customer_bp.route('/bookings/<uuid:booking_id>/review', methods=['GET', 'POST'])
@login_required
def leave_review(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.customer_id != current_user.id:
        abort(403)
    if booking.status != 'completed':
        flash('You can only review completed bookings.', 'danger')
        return redirect(url_for('customer.view_booking', booking_id=booking.id))
    if Review.query.filter_by(booking_id=booking.id).first():
        flash('You have already reviewed this booking.', 'info')
        return redirect(url_for('customer.view_booking', booking_id=booking.id))
    if request.method == 'POST':
        review = Review(
            booking_id=booking.id,
            reviewer_id=current_user.id,
            reviewee_id=booking.pro_id,
            rating=int(request.form.get('rating', 5)),
            comment=request.form.get('comment', '').strip()
        )
        db.session.add(review)
        pro = booking.quote.pro
        all_reviews = Review.query.filter_by(reviewee_id=booking.pro_id).all()
        pro.avg_rating = round(sum(r.rating for r in all_reviews) / len(all_reviews), 2)
        pro.total_reviews = len(all_reviews)
        db.session.commit()
        flash('Review submitted. Thank you!', 'success')
        return redirect(url_for('customer.view_booking', booking_id=booking.id))
    return render_template('customer/leave_review.html', booking=booking)


@customer_bp.route('/profile')
@login_required
def profile():
    return render_template('customer/profile.html')


@customer_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.full_name = request.form.get('full_name', current_user.full_name).strip()
        current_user.phone = request.form.get('phone', current_user.phone).strip()
        db.session.commit()
        flash('Profile updated.', 'success')
        return redirect(url_for('customer.profile'))
    return render_template('customer/edit_profile.html')
