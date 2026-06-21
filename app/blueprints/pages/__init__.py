from flask import Blueprint

pages_bp = Blueprint('pages', __name__, template_folder='../../templates/pages')

from app.blueprints.pages import routes
