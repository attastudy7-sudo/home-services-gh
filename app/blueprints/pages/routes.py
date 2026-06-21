from flask import render_template
from app.blueprints.pages import pages_bp


@pages_bp.route('/legal/terms')
def terms():
    return render_template('pages/legal.html', title='Terms of Service')


@pages_bp.route('/legal/privacy')
def privacy():
    return render_template('pages/legal.html', title='Privacy Policy')


@pages_bp.route('/legal/contact')
def contact():
    return render_template('pages/legal.html', title='Contact')
