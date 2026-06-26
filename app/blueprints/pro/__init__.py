from flask import Blueprint, redirect, url_for, flash, request
from flask_login import current_user

pro_bp = Blueprint('pro', __name__, template_folder='../../templates/pro')


@pro_bp.before_request
def check_onboarding():
    if not current_user.is_authenticated or not current_user.is_pro:
        return
    if request.endpoint in ('pro.onboarding_services', 'pro.onboarding_areas', 'pro.public_profile'):
        return
    pro = current_user.pro_profile
    if pro is None:
        return
    if pro.categories.count() == 0:
        flash('Please set up your services to continue.', 'info')
        return redirect(url_for('pro.onboarding_services'))
    if pro.service_areas.count() == 0:
        flash('Please set up your service areas to continue.', 'info')
        return redirect(url_for('pro.onboarding_areas'))


from app.blueprints.pro import routes
