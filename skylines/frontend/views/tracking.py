from flask import Blueprint, jsonify, request

from skylines.frontend.cache import cache
from skylines.frontend.oauth import oauth
from skylines.lib.decorators import jsonp
from skylines.model import TrackingFix, Airport, Follower
from skylines.schemas import TrackingFixSchema, AirportSchema

tracking_blueprint = Blueprint('tracking', 'skylines')


@tracking_blueprint.route('/tracking', strict_slashes=False)
@tracking_blueprint.route('/live', strict_slashes=False)
@oauth.optional()
def index():
    fix_schema = TrackingFixSchema(only=('time', 'location', 'altitude', 'elevation', 'pilot'))
    airport_schema = AirportSchema(only=('id', 'name', 'countryCode'))

    @cache.memoize(timeout=(60 * 60))
    def get_nearest_airport(track):
        airport = Airport.by_location(track.location, None)
        if not airport:
            return None

        return dict(airport=airport_schema.dump(airport).data,
                    distance=airport.distance(track.location))

    tracks = []
    for t in TrackingFix.get_latest():
        nearest_airport = get_nearest_airport(t)

        track = fix_schema.dump(t).data
        if nearest_airport:
            track['nearestAirport'] = nearest_airport['airport']
            track['nearestAirportDistance'] = nearest_airport['distance']

        tracks.append(track)

    if request.user_id:
        followers = [f.destination_id for f in Follower.query(source_id=request.user_id)]
    else:
        followers = []

    return jsonify(friends=followers, tracks=tracks)


@tracking_blueprint.route('/tracking/latest.json')
@jsonp
def latest():
    fixes = []
    for fix in TrackingFix.get_latest():
        json = dict(time=fix.time.isoformat() + 'Z',
                    location=fix.location.to_wkt(),
                    pilot=dict(id=fix.pilot_id, name=unicode(fix.pilot)))

        optional_attributes = ['track', 'ground_speed', 'airspeed',
                               'altitude', 'vario', 'engine_noise_level']
        for attr in optional_attributes:
            value = getattr(fix, attr)
            if value is not None:
                json[attr] = value

        fixes.append(json)

    return jsonify(fixes=fixes)
