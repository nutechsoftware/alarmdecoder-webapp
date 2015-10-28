# -*- coding: utf-8 -*-

from functools import wraps

from flask import Blueprint, current_app, request, jsonify, abort, Response
from flask.ext.login import login_user, current_user, logout_user

from ..user import User
from ..settings import Setting

api = Blueprint('api', __name__, url_prefix='/api/v1')

##### Utility
def api_authorized(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        apikey = Setting.get_by_name('apikey').value
        if apikey is None or apikey != request.args.get('apikey'):
            return jsonify(build_error(666, 'Not authorized.')), 401

        if current_app.decoder.device is None:
            return jsonify(build_error(777, 'Device has not finished initializing.')), 503

        return f(*args, **kwargs)

    return wrapped

def build_error(code, message):
    return {
        'error': {
            'code': code,
            'message': message,
        }
    }

##### AlarmDecoder device routes
@api.route('/alarmdecoder', methods=['GET'])
@api_authorized
def alarmdecoder():
    ret = {
        'panel_type': current_app.decoder.device.mode,                          # TODO: convert to human-readable.
        'panel_powered': current_app.decoder.device._power_status,
        'panel_alarming': current_app.decoder.device._alarm_status,
        'panel_bypassed': current_app.decoder.device._bypass_status,
        'panel_armed': current_app.decoder.device._armed_status,
        'panel_fire_detected': current_app.decoder.device._fire_status[0],
        'panel_on_battery': current_app.decoder.device._battery_status[0],
        'panel_panicked': current_app.decoder.device._panic_status,             # TODO: Can we default this to False instead of None?
        'panel_relay_status': current_app.decoder.device._relay_status          # TODO: Is JSON going to like our tuple index?  Test with real data.
    }

    return jsonify(ret)

@api.route('/alarmdecoder/send', methods=['POST'])
@api_authorized
def alarmdecoder_send():
    ret = { 'status': 'OK' }

    req = request.get_json()
    if req is None:
        return jsonify(build_error(999, "Missing request body or using incorrect content type.")), 422

    keys = req.get('keys', None)
    if keys is None:
        return jsonify(build_error(888, "Missing 'keys' in request.")), 422

    current_app.decoder.device.send(req['keys'])

    return jsonify(ret)

@api.route('/alarmdecoder/reboot', methods=['POST'])
@api_authorized
def alarmdecoder_reboot():
    ret = { 'status': 'OK' }

    current_app.decoder.device.reboot()

    return jsonify(ret)

@api.route('/alarmdecoder/configuration', methods=['GET', 'PUT'])
@api_authorized
def alarmdecoder_configuration():
    device = current_app.decoder.device

    if request.method == 'GET':
        ret = {
            'address': device.address,
            'config_bits': device.configbits,
            'address_mask': device.address_mask,
            'emulate_zone': device.emulate_zone,
            'emulate_relay': device.emulate_relay,
            'emulate_lrr': device.emulate_lrr,
            'deduplicate': device.deduplicate,
            'mode': device.mode                             # TODO: make sure this gets converted correctly.
        }

        return jsonify(ret)

    elif request.method == 'PUT':
        req = request.get_json()
        if req is None:
            return jsonify(build_error(999, "Missing request body or using incorrect content type.")), 422

        if req.get('address', None) is not None:
            device.address = req['address']
        if req.get('config_bits', None) is not None:
            device.configbits = req['config_bits']
        if req.get('address_mask', None) is not None:
            device.address_mask = req['address_mask']
        if req.get('emulate_zone', None) is not None:
            device.emulate_zone = req['emulate_zone']
        if req.get('emulate_relay', None) is not None:
            device.emulate_relay = req['emulate_relay']
        if req.get('emulate_lrr', None) is not None:
            device.emulate_lrr = req['emulate_lrr']
        if req.get('deduplicate', None) is not None:
            device.deduplicate = req['deduplicate']
        if req.get('mode', None) is not None:
            device.mode = req['mode']                       # TODO: make sure this gets converted correctly.

        device.save_config()

        return jsonify(status='OK')


##### Zone routes
@api.route('/zones', methods=['GET', 'POST'])
@api_authorized
def zones():
    pass

@api.route('/zones/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@api_authorized
def zones_by_id(id):
    pass

@api.route('/zones/<int:id>/fault', methods=['POST'])
@api_authorized
def zones_fault(id):
    pass


##### Notification routes
@api.route('/notifications', methods=['GET', 'POST'])
@api_authorized
def notifications():
    pass

@api.route('/notifications/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def notifications_by_id(id):
    pass


##### Camera routes
@api.route('/cameras', methods=['GET', 'POST'])
@api_authorized
def cameras():
    pass

@api.route('/cameras/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@api_authorized
def cameras_by_id(id):
    pass


##### User routes
@api.route('/users', methods=['GET', 'POST'])
@api_authorized
def users():
    pass

@api.route('/users/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@api_authorized
def users_by_id(id):
    pass


##### System routes
@api.route('/system', methods=['GET'])
@api_authorized
def system():
    pass

@api.route('/system/reboot', methods=['POST'])
@api_authorized
def system_reboot():
    pass

@api.route('/system/shutdown', methods=['POST'])
@api_authorized
def system_shutdown():
    pass
