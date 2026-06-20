from flask import Flask, render_template
from config import config
from app.extensions import db, migrate, login_manager


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app.blueprints.auth import auth_bp
    from app.blueprints.customer import customer_bp
    from app.blueprints.pro import pro_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.api import api_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(customer_bp, url_prefix='/customer')
    app.register_blueprint(pro_bp, url_prefix='/pro')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')

    from app import models

    @app.route('/')
    def index():
        from app.models.service import ServiceCategory
        from app.models.location import LocationIndex
        categories = ServiceCategory.query.filter_by(is_active=True).order_by(ServiceCategory.sort_order).all()
        cities = LocationIndex.query.with_entities(LocationIndex.city).distinct().all()
        return render_template('index.html', categories=categories, cities=cities)

    @app.route('/<city_slug>')
    def city_landing(city_slug):
        from app.models.location import LocationIndex
        from app.models.service import ServiceCategory
        area = LocationIndex.query.filter_by(slug=city_slug).first_or_404()
        categories = ServiceCategory.query.filter_by(is_active=True).order_by(ServiceCategory.sort_order).all()
        return render_template('city_landing.html', area=area, categories=categories)

    @app.route('/<city_slug>/<category_slug>')
    def category_in_city(city_slug, category_slug):
        from app.models.location import LocationIndex
        from app.models.service import ServiceCategory
        from app.models.pro import ProProfile, ProServiceArea, ProCategory
        area = LocationIndex.query.filter_by(slug=city_slug).first_or_404()
        category = ServiceCategory.query.filter_by(slug=category_slug, is_active=True).first_or_404()
        pros = (ProProfile.query
            .join(ProServiceArea, ProServiceArea.pro_id == ProProfile.id)
            .join(ProCategory, ProCategory.pro_id == ProProfile.id)
            .filter(
                ProServiceArea.location_index_id == area.id,
                ProCategory.category_id == category.id,
                ProProfile.verification_status == 'approved',
                ProProfile.is_available == True
            ).all())
        return render_template('category_in_city.html', area=area, category=category, pros=pros)

    return app
