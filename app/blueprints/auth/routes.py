from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.blueprints.auth import auth_bp
from app.extensions import db
from app.models.user import User
from app.models.pro import ProProfile
from app.auth_tokens import generate_reset_token, verify_reset_token, generate_email_token, verify_email_token
import re


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form.get('email')).first()
        if user and user.check_password(request.form.get('password')) and user.is_active:
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        flash('Invalid email or password.', 'danger')
    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        full_name = request.form.get('full_name', '').strip()
        password = request.form.get('password', '')
        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'danger')
            return redirect(url_for('auth.register'))
        if User.query.filter_by(email=email).first():
            flash('An account with this email already exists.', 'danger')
            return redirect(url_for('auth.register'))
        if User.query.filter_by(phone=phone).first():
            flash('An account with this phone number already exists.', 'danger')
            return redirect(url_for('auth.register'))
        user = User(email=email, phone=phone, full_name=full_name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        token = generate_email_token(user.id)
        verify_url = url_for('auth.verify_email', token=token, _external=True)
        print(f'[EMAIL STUB] Verification email for {email}: {verify_url}')
        login_user(user)
        flash('Welcome to GhanaServe! Please check your email to verify your account.', 'success')
        return redirect(url_for('customer.dashboard'))
    return render_template('auth/register.html')


@auth_bp.route('/register-pro', methods=['GET', 'POST'])
def register_pro():
    if current_user.is_authenticated:
        if current_user.is_pro:
            return redirect(url_for('pro.dashboard'))
        return redirect(url_for('auth.become_pro'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        full_name = request.form.get('full_name', '').strip()
        password = request.form.get('password', '')
        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'danger')
            return redirect(url_for('auth.register_pro'))
        business_name = request.form.get('business_name', '').strip()
        if User.query.filter_by(email=email).first():
            flash('An account with this email already exists.', 'danger')
            return redirect(url_for('auth.register_pro'))
        if User.query.filter_by(phone=phone).first():
            flash('An account with this phone number already exists.', 'danger')
            return redirect(url_for('auth.register_pro'))
        user = User(email=email, phone=phone, full_name=full_name)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
        token = generate_email_token(user.id)
        verify_url = url_for('auth.verify_email', token=token, _external=True)
        print(f'[EMAIL STUB] Verification email for {email}: {verify_url}')
        slug = re.sub(r'[^a-z0-9]+', '-', business_name.lower()).strip('-')
        pro = ProProfile(user_id=user.id, business_name=business_name, slug=slug)
        db.session.add(pro)
        db.session.commit()
        login_user(user)
        flash('Pro account created. Your profile is pending admin approval.', 'info')
        return redirect(url_for('pro.dashboard'))
    return render_template('auth/register_pro.html')


@auth_bp.route('/become-pro', methods=['GET', 'POST'])
@login_required
def become_pro():
    if current_user.is_pro or current_user.is_admin:
        flash('You already have a pro account.', 'info')
        return redirect(url_for('pro.dashboard' if current_user.is_pro else 'index'))
    if request.method == 'POST':
        business_name = request.form.get('business_name', '').strip()
        if not business_name:
            flash('Business name is required.', 'danger')
            return render_template('auth/become_pro.html')
        slug = re.sub(r'[^a-z0-9]+', '-', business_name.lower()).strip('-')
        pro = ProProfile(user_id=current_user.id, business_name=business_name, slug=slug)
        db.session.add(pro)
        db.session.commit()
        flash('Welcome to GhanaServe Pro! Set up your services and areas to start receiving leads.', 'success')
        return redirect(url_for('pro.onboarding_services'))
    return render_template('auth/become_pro.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/verify-email/<token>')
def verify_email(token):
    user_id = verify_email_token(token)
    if not user_id:
        flash('Invalid or expired verification link.', 'danger')
        return redirect(url_for('auth.login'))
    user = User.query.get(user_id)
    if not user:
        flash('Invalid or expired verification link.', 'danger')
        return redirect(url_for('auth.login'))
    if user.is_verified:
        flash('Email already verified.', 'info')
    else:
        user.is_verified = True
        db.session.commit()
        flash('Email verified successfully!', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/resend-verification', methods=['GET', 'POST'])
@login_required
def resend_verification():
    if current_user.is_verified:
        flash('Your email is already verified.', 'info')
        return redirect(url_for('index'))
    if request.method == 'POST':
        token = generate_email_token(current_user.id)
        verify_url = url_for('auth.verify_email', token=token, _external=True)
        print(f'[EMAIL STUB] Verification email for {current_user.email}: {verify_url}')
        flash('Verification link sent. Check your email.', 'info')
        return redirect(url_for('index'))
    return render_template('auth/resend_verification.html')


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        user = User.query.filter_by(email=email).first()
        if user:
            token = generate_reset_token(user.id)
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            print(f'[EMAIL STUB] Password reset link for {email}: {reset_url}')
        flash('If that email exists, a reset link has been sent.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/forgot_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user_id = verify_reset_token(token)
    if not user_id:
        flash('Invalid or expired reset link.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    user = User.query.get(user_id)
    if not user:
        flash('Invalid or expired reset link.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.reset_password', token=token))
        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'danger')
            return redirect(url_for('auth.reset_password', token=token))
        user.set_password(password)
        db.session.commit()
        flash('Password reset successfully. Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', token=token)
