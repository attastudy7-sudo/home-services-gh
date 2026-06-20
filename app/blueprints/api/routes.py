from flask import jsonify, request, session
from flask_login import login_required, current_user
from app.blueprints.api import api_bp
from app.extensions import db
from app.models.financial import Notification
from app.models.location import GeocodeCache, LocationIndex
from app.models.service import ServiceCategory, ServiceSubcategory
import requests as http


@api_bp.route('/notifications/unread-count')
@login_required
def unread_count():
    count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return jsonify({'count': count})


@api_bp.route('/notifications/<uuid:notif_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notif_id):
    notif = Notification.query.get_or_404(notif_id)
    if notif.user_id != current_user.id:
        return jsonify({'error': 'Forbidden'}), 403
    notif.is_read = True
    db.session.commit()
    return jsonify({'ok': True})


@api_bp.route('/reverse-geocode', methods=['POST'])
def reverse_geocode():
    data = request.get_json()
    lat = data.get('lat')
    lng = data.get('lng')
    if not lat or not lng:
        return jsonify({'error': 'Missing coordinates'}), 400

    lat_key = str(round(float(lat), 3))
    lng_key = str(round(float(lng), 3))

    cached = GeocodeCache.query.filter_by(lat_key=lat_key, lng_key=lng_key).first()
    if cached:
        session['user_city'] = cached.resolved_city
        session['user_area'] = cached.resolved_area
        session['location_source'] = 'gps'
        return jsonify({'city': cached.resolved_city, 'area': cached.resolved_area})

    try:
        from flask import current_app
        resp = http.get(
            'https://nominatim.openstreetmap.org/reverse',
            params={'lat': lat, 'lon': lng, 'format': 'json'},
            headers={'User-Agent': current_app.config.get('GEOCODE_USER_AGENT', 'GhanaServe/1.0')},
            timeout=5
        )
        result = resp.json()
        addr = result.get('address', {})
        city = addr.get('city') or addr.get('town') or addr.get('county', 'Accra')
        area = addr.get('suburb') or addr.get('city_district') or addr.get('neighbourhood', '')

        cache_entry = GeocodeCache(lat_key=lat_key, lng_key=lng_key, resolved_city=city, resolved_area=area)
        db.session.add(cache_entry)
        db.session.commit()

        session['user_city'] = city
        session['user_area'] = area
        session['location_source'] = 'gps'

        return jsonify({'city': city, 'area': area})
    except Exception as e:
        return jsonify({'error': 'Geocoding failed', 'detail': str(e)}), 500


@api_bp.route('/set-location', methods=['POST'])
def set_location():
    data = request.get_json()
    city = data.get('city')
    area = data.get('area')
    if not city:
        return jsonify({'error': 'City required'}), 400
    session['user_city'] = city
    session['user_area'] = area
    session['location_source'] = 'manual'
    return jsonify({'ok': True})


@api_bp.route('/locations')
def list_locations():
    locations = LocationIndex.query.filter_by(is_active=True).order_by(
        LocationIndex.city, LocationIndex.area_name).all()
    return jsonify([{
        'id': str(loc.id),
        'area_name': loc.area_name,
        'city': loc.city,
        'slug': loc.slug
    } for loc in locations])


@api_bp.route('/categories')
def list_categories_api():
    cats = ServiceCategory.query.filter_by(is_active=True).order_by(ServiceCategory.sort_order).all()
    return jsonify([{'id': str(c.id), 'name': c.name, 'slug': c.slug} for c in cats])


@api_bp.route('/subcategories/<uuid:category_id>')
def list_subcategories(category_id):
    subs = ServiceSubcategory.query.filter_by(
        category_id=category_id, is_active=True).all()
    return jsonify([{'id': str(s.id), 'name': s.name, 'slug': s.slug} for s in subs])
