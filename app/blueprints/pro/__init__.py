from flask import Blueprint

pro_bp = Blueprint('pro', __name__, template_folder='../../templates/pro')

from app.blueprints.pro import routes
