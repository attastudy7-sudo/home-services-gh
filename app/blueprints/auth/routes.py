from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.blueprints.auth import auth_bp
from app.extensions import db
from app.models.user import User
from app.models.pro import ProProfile
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
        login_user(user)
        flash('Welcome to GhanaServe!', 'success')
        return redirect(url_for('customer.dashboard'))
    return render_template('auth/register.html')


@auth_bp.route('/register-pro', methods=['GET', 'POST'])
def register_pro():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        full_name = request.form.get('full_name', '').strip()
        password = request.form.get('password', '')
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
        slug = re.sub(r'[^a-z0-9]+', '-', business_name.lower()).strip('-')
        pro = ProProfile(user_id=user.id, business_name=business_name, slug=slug)
        db.session.add(pro)
        db.session.commit()
        login_user(user)
        flash('Pro account created. Your profile is pending admin approval.', 'info')
        return redirect(url_for('pro.dashboard'))
    return render_template('auth/register_pro.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        flash('If that email exists, a reset link has been sent.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/forgot_password.html')
