from flask import Flask, render_template, abort
from config import config
from app.extensions import db, migrate, login_manager, csrf, scheduler
from sqlalchemy import func as sa_func


def resolve_location(slug):
    """Return (area_or_None, city_name, area_ids_list) for a slug.
    If slug matches a specific area, area_or_None is the LocationIndex.
    If slug matches a city name, area_or_None is None and area_ids holds all area IDs in that city.
    Otherwise aborts with 404.
    """
    from app.models.location import LocationIndex

    area = LocationIndex.query.filter_by(slug=slug).first()
    if area:
        return area, area.city, [area.id]

    areas = LocationIndex.query.filter(
        sa_func.lower(LocationIndex.city) == slug.lower()
    ).order_by(LocationIndex.area_name).all()
    if areas:
        return None, areas[0].city, [a.id for a in areas]

    abort(404)


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    from app.blueprints.auth import auth_bp
    from app.blueprints.customer import customer_bp
    from app.blueprints.pro import pro_bp
    from app.blueprints.admin import admin_bp
    from app.blueprints.api import api_bp
    from app.blueprints.pages import pages_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(customer_bp, url_prefix='/customer')
    app.register_blueprint(pro_bp, url_prefix='/pro')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(pages_bp, url_prefix='/')

    from app import models

    if not scheduler.running:
        from app.jobs import expire_stale_requests, expire_stale_quotes
        scheduler.add_job(func=expire_stale_requests, args=[app], trigger='interval', days=1, id='expire_stale_requests')
        scheduler.add_job(func=expire_stale_quotes, args=[app], trigger='interval', days=1, id='expire_stale_quotes')
        scheduler.start()

    @app.route('/')
    def index():
        from app.models.service import ServiceCategory
        from app.models.location import LocationIndex
        categories = ServiceCategory.query.filter_by(is_active=True).order_by(ServiceCategory.sort_order).all()
        locations = LocationIndex.query.filter_by(is_active=True).order_by(LocationIndex.city, LocationIndex.area_name).all()
        return render_template('index.html', locations=locations, categories=categories)

    @app.route('/<city_slug>')
    def city_landing(city_slug):
        from app.models.service import ServiceCategory
        area, city_name, _area_ids = resolve_location(city_slug)
        categories = ServiceCategory.query.filter_by(is_active=True).order_by(ServiceCategory.sort_order).all()
        return render_template('city_landing.html', area=area, city_name=city_name, categories=categories)

    @app.route('/<city_slug>/<category_slug>')
    def category_in_city(city_slug, category_slug):
        from app.models.service import ServiceCategory, ServiceSubcategory
        from app.models.pro import ProProfile, ProServiceArea, ProCategory, ProSubcategory

        area, city_name, area_ids = resolve_location(city_slug)
        category = ServiceCategory.query.filter_by(slug=category_slug, is_active=True).first_or_404()
        subcategories = ServiceSubcategory.query.filter_by(
            category_id=category.id, is_active=True
        ).order_by(ServiceSubcategory.name).all()

        pros = (ProProfile.query
            .join(ProServiceArea, ProServiceArea.pro_id == ProProfile.id)
            .join(ProCategory, ProCategory.pro_id == ProProfile.id)
            .filter(
                ProServiceArea.location_index_id.in_(area_ids),
                ProCategory.category_id == category.id,
                ProProfile.verification_status == 'approved',
                ProProfile.is_available == True
            ).order_by(ProProfile.avg_rating.desc()).all())

        rates = []
        if pros:
            subcat_rows = (db.session.query(ProSubcategory.pro_id, ServiceSubcategory.slug)
                .join(ServiceSubcategory, ServiceSubcategory.id == ProSubcategory.subcategory_id)
                .filter(ProSubcategory.pro_id.in_([p.id for p in pros]))
                .all())
            pro_subcat_slugs = {}
            for pro_id, slug in subcat_rows:
                pro_subcat_slugs.setdefault(pro_id, []).append(slug)
            for pro in pros:
                pro.subcat_slugs = pro_subcat_slugs.get(pro.id, [])
                if pro.base_hourly_rate:
                    rates.append(float(pro.base_hourly_rate))

        return render_template('category_in_city.html',
            area=area, city_name=city_name, category=category, subcategories=subcategories, pros=pros,
            price_min=min(rates) if rates else 0,
            price_max=max(rates) if rates else 0)

    return app
