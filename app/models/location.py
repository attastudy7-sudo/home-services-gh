from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID
import uuid


class LocationIndex(db.Model):
    __tablename__ = 'location_index'

    id            = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    area_name     = db.Column(db.String(150), nullable=False)
    city          = db.Column(db.String(100), nullable=False)
    slug          = db.Column(db.String(220), nullable=False, unique=True)
    centroid_lat  = db.Column(db.Float, nullable=False)
    centroid_lng  = db.Column(db.Float, nullable=False)
    is_active     = db.Column(db.Boolean, default=True)


class UserLocation(db.Model):
    __tablename__ = 'user_locations'

    id                = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id           = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id', ondelete='CASCADE'))
    location_index_id = db.Column(UUID(as_uuid=True), db.ForeignKey('location_index.id', ondelete='SET NULL'), nullable=True)
    latitude          = db.Column(db.Float)
    longitude         = db.Column(db.Float)
    is_primary        = db.Column(db.Boolean, default=False)
    gps_captured      = db.Column(db.Boolean, default=False)
    captured_at       = db.Column(db.DateTime)

    location = db.relationship('LocationIndex')


class GeocodeCache(db.Model):
    __tablename__ = 'geocode_cache'

    id                = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lat_key           = db.Column(db.String(12), nullable=False)
    lng_key           = db.Column(db.String(12), nullable=False)
    resolved_city     = db.Column(db.String(100), nullable=False)
    resolved_area     = db.Column(db.String(150))
    location_index_id = db.Column(UUID(as_uuid=True), db.ForeignKey('location_index.id'), nullable=True)
    cached_at         = db.Column(db.DateTime, server_default=db.func.now())

    __table_args__ = (
        db.UniqueConstraint('lat_key', 'lng_key', name='uq_geocode_coords'),
    )
