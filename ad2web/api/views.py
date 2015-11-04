# -*- coding: utf-8 -*-

import json
import sh

from functools import wraps
from datetime import timedelta

from flask import Blueprint, current_app, request, jsonify, abort, Response
from flask.ext.login import login_user, current_user, logout_user

from ..extensions import db

from ..user import User
from ..zones import Zone
from ..notifications import Notification, NotificationSetting
from ..notifications.constants import EVENT_TYPES
from ..cameras import Camera
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
    if request.method == 'GET':
        ret = {}
        zones = Zone.query.all()

        ret['zones'] = []
        for z in zones:
            ret['zones'].append({
                'zone_id': z.zone_id,
                'name': z.name,
                'description': z.description
            })

        return jsonify(ret)

    elif request.method == 'POST':
        ret = {}
        req = request.get_json()
        if req is None:
            return jsonify(build_error(999, 'Missing request body or using incorrect content type.')), 422

        zone_id = req.get('zone_id', None)
        name = req.get('name', None)
        description = req.get('description', None)

        if zone_id is None:
            return jsonify(build_error(888, "Missing 'zone_id' entry.")), 422

        if name is None:
            return jsonify(build_error(888, "Missing 'name' entry.")), 422

        existing_zone = Zone.query.filter_by(zone_id=zone_id).first()
        if existing_zone is not None:
            return jsonify(build_error(777, 'Zone already exists.')), 409

        zone = Zone(zone_id=zone_id, name=name, description=description)
        
        db.session.add(zone)
        db.session.commit()

        ret = {
            'zone_id': zone_id,
            'name': name,
            'description': description
        }

        return jsonify(ret), 201

@api.route('/zones/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@api_authorized
def zones_by_id(id):
    z = Zone.query.filter_by(zone_id=id).first()
    if z is None:
        return jsonify(build_error(663, 'Zone does not exist.')), 404

    if request.method == 'GET':
        ret = {
            'zone_id': z.zone_id,
            'name': z.name,
            'description': z.description
        }

        return jsonify(ret)

    elif request.method == 'PUT':
        ret = {}

        req = request.get_json()
        if req is None:
            return jsonify(build_error(999, 'Missing request body or using incorrect content type.')), 422

        zone_id = req.get('zone_id', None)

        if zone_id is not None and zone_id != z.zone_id:
            check_zone = Zone.query.filter_by(zone_id=zone_id).first()
            if check_zone is not None:
                return jsonify(build_error(777, 'Zone already exists with the associated zone_id.')), 409
            else:
                z.zone_id = zone_id

        name = req.get('name', None)
        if name is not None:
            z.name = name

        description = req.get('description', None)
        if description is not None:
            z.description = description

        db.session.add(z)
        db.session.commit()

        ret = {
            'zone_id': z.zone_id,
            'name': z.name,
            'description': z.description
        }

        return jsonify(ret)

    elif request.method == 'DELETE':
        db.session.delete(z)
        db.session.commit()

        ret = { 'status': 'OK' }

        return jsonify(ret)


@api.route('/zones/<int:id>/fault', methods=['POST'])
@api_authorized
def zones_fault(id):
    z = Zone.query.filter_by(zone_id=id).first()
    if z is None:
        return jsonify(build_error(663, 'Zone does not exist.')), 404

    # TODO: Make a note in docs.. only supported for emulated zones.
    current_app.decoder.device.send("L{0}1\r".format(id))

    ret = { 'status': 'OK' }

    return jsonify(ret)

@api.route('/zones/<int:id>/restore', methods=['POST'])
@api_authorized
def zones_restore(id):
    z = Zone.query.filter_by(zone_id=id).first()
    if z is None:
        return jsonify(build_error(663, 'Zone does not exist.')), 404

    # TODO: Make a note in docs.. only supported for emulated zones.
    current_app.decoder.device.send("L{0}0\r".format(id))

    ret = { 'status': 'OK' }

    return jsonify(ret)

##### Notification routes
@api.route('/notifications', methods=['GET', 'POST'])
@api_authorized
def notifications():
    if request.method == 'GET':
        ret = {}
        notifications = Notification.query.all()

        ret['notifications'] = []
        for n in notifications:
            ret['notifications'].append({
                'id': n.id,
                'type': n.type,
                'description': n.description,
                'user_id': n.user_id
            })

        return jsonify(ret)

    elif request.method == 'POST':
        ret = {}
        req = request.get_json()
        if req is None:
            return jsonify(build_error(999, 'Missing request body or using incorrect content type.')), 422

        notification_type = req.get('type', None)
        if notification_type is None:
            return jsonify(build_error(888, "Missing 'type' entry.")), 422

        description = req.get('description', None)
        if description is None:
            return jsonify(build_error(888, "Missing 'description' entry.")), 422

        user_id = req.get('user_id', None)
        if user_id is None:
            return jsonify(build_error(888, "Missing 'user_id' entry.")), 422

        notification = Notification(type=notification_type, description=description, user_id=user_id)

        settings = req.get('settings', None)
        for name, value in settings.items():
            # TODO: Special case for subscriptions.

            notification.settings[name] = NotificationSetting(name=name, value=value)

        db.session.add(notification)
        db.session.commit()

        ret = {
            'id': notification.id,
            'type': notification.type,
            'description': notification.description,
            'user_id': notification.user_id
        }

        return jsonify(ret), 201

@api.route('/notifications/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def notifications_by_id(id):
    ret = { }

    notification = Notification.query.filter_by(id=id).first()
    if notification is None:
        return jsonify(build_error(663, 'Notification does not exist.')), 404

    if request.method == 'GET':
        settings = { }

        for setting_name, setting in notification.settings.items():
            # NOTE: Leaving authentication information out on purpose.  May need to expand this or do it a different way.
            if setting_name == 'username' or setting_name == 'password':
                continue

            value = setting.value

            # Special case for subscriptions.
            if setting_name == "subscriptions":
                value = json.loads(setting.value)

                output = { }
                for event_type in EVENT_TYPES:
                    output[EVENT_TYPES[event_type]] = False

                for k in value.keys():
                    output[EVENT_TYPES[int(k)]] = value[k]
                    del value[k]

                value = output

            settings[setting_name] = value

        ret = {
            'id': notification.id,
            'type': notification.type,
            'description': notification.description,
            'user_id': notification.user_id,
            'settings': settings
        }

    elif request.method == 'PUT':
        req = request.get_json()
        if req is None:
            return jsonify(build_error(999, 'Missing request body or using incorrect content type.')), 422

        notification_type = req.get('type', None)
        if notification_type is not None and notification_type != notification.type:
            return jsonify(build_error(123, 'Cannot change the type of an existing notification.')), 422

        description = req.get('description', None)
        user_id = req.get('user_id', None)
        settings = req.get('settings', None)

        if description is not None:
            notification.description = description
        if user_id is not None:
            notification.user_id = user_id

        if settings is not None:
            for name, value in settings:
                # TODO: special case for subscriptions

                setting = notification.settings.get(name, None)
                if setting is None:
                    setting = NotificationSetting(name=name)

                setting.value = value

        db.session.add(notification)
        db.session.commit()

        # TODO: produce notification data.  Probably consolidate into a function.
        ret = { 'status': 'OK' }

    elif request.method == 'DELETE':
        db.session.delete(notification)
        db.session.commit()

        # TODO: Maybe produce a better result?
        ret = { 'status': 'OK' }

    return jsonify(ret)


##### Camera routes
@api.route('/cameras', methods=['GET', 'POST'])
@api_authorized
def cameras():
    ret = { }

    if request.method == 'GET':
        cameras = Camera.query.all()

        ret['cameras'] = []
        for camera in cameras:
            ret['cameras'].append({
                'id': camera.id,
                'name': camera.name,
                'user_id': camera.user_id
            })

    elif request.method == 'POST':
        req = request.get_json()
        if req is None:
            return jsonify(build_error(999, 'Missing request body or using incorrect content type.')), 422

        name = req.get('name', None)
        url = req.get('url', None)
        user_id = req.get('user_id', None)
        username = req.get('username', '')  # TODO: Fix camera code so that it deals with nulls correctly
        password = req.get('password', '')  # TODO: Fix camera code so that it deals with nulls correctly

        if name is None:
            return jsonify(build_error(888, "Missing 'name' entry.")), 422

        if url is None:
            return jsonify(build_error(888, "Missing 'url' entry.")), 422

        if user_id is None:
            return jsonify(build_error(888, "Missing 'user_id' entry.")), 422

        camera = Camera(name=name, get_jpg_url=url, user_id=user_id, username=username, password=password)
        db.session.add(camera)
        db.session.commit()

        ret = {
            'id': camera.id,
            'name': camera.name,
            'user_id': camera.user_id,
            'url': camera.get_jpg_url
        }

    return jsonify(ret)

@api.route('/cameras/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@api_authorized
def cameras_by_id(id):
    ret = { }

    camera = Camera.query.filter_by(id=id).first()
    if camera is None:
        return jsonify(build_error(663, 'Camera does not exist.')), 404

    if request.method == 'GET':
        # NOTE: Leaving authentication information out on purpose.

        ret = {
            'id': camera.id,
            'name': camera.name,
            'url': camera.get_jpg_url,
            'user_id': camera.user_id
        }

    elif request.method == 'PUT':
        req = request.get_json()
        if req is None:
            return jsonify(build_error(999, 'Missing request body or using incorrect content type.')), 422

        name = req.get('name', None)
        url = req.get('url', None)
        user_id = req.get('user_id', None)
        username = req.get('username', None)
        password = req.get('password', None)

        if name is not None:
            camera.name = name
        if url is not None:
            camera.get_jpg_url = url
        if user_id is not None:
            camera.user_id = user_id
        if username is not None:
            camera.username = username
        if password is not None:
            camera.password = password

        db.session.add(camera)
        db.session.commit()

        # TODO: produce camera data.  Probably consolidate into a function.
        ret = { 'status': 'OK' }

    elif request.method == 'DELETE':
        db.session.delete(camera)
        db.session.commit()

        # TODO: Maybe produce a better result?
        ret = { 'status': 'OK' }

    return jsonify(ret)

##### User routes
@api.route('/users', methods=['GET', 'POST'])
@api_authorized
def users():
    ret = { }

    if request.method == 'GET':
        ret['users'] = []

        users = User.query.all()
        for user in users:
            ret['users'].append({
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'created_time': user.created_time,
                'role': user.role_code,
                'status': user.status
            })

    elif request.method == 'POST':
        req = request.get_json()
        if req is None:
            return jsonify(build_error(999, 'Missing request body or using incorrect content type.')), 422

        name = req.get('name', None)
        email = req.get('email', None)
        password = req.get('password', None)
        role = req.get('role', None)
        status = req.get('status', None)

        if name is None:
            return jsonify(build_error(888, "Missing 'name' entry.")), 422

        if email is None:
            return jsonify(build_error(888, "Missing 'email' entry.")), 422

        if password is None:
            return jsonify(build_error(888, "Missing 'password' entry.")), 422

        if role is None:
            return jsonify(build_error(888, "Missing 'role' entry.")), 422

        if status is None:
            return jsonify(build_error(888, "Missing 'status' entry.")), 422

        # TODO: check for unique email/username
        # TODO: generate password here.
        # TODO: make status code consistent

        user = User(name=name, email=email, password=password, role_code=role, status_code=status)
        db.session.add(user)
        db.session.commit()

        ret = {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'created_time': user.created_time,
            'role': user.role_code,
            'status': user.status
        }

    return jsonify(ret)

@api.route('/users/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@api_authorized
def users_by_id(id):
    ret = { }

    user = User.query.filter_by(id=id).first()
    if user is None:
        return jsonify(build_error(663, 'User does not exist.')), 404

    if request.method == 'GET':
        ret = {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'created_time': user.created_time,
            'role': user.role_code,
            'status': user.status
        }

    elif request.method == 'PUT':
        req = request.get_json()
        if req is None:
            return jsonify(build_error(999, 'Missing request body or using incorrect content type.')), 422

        name = req.get('name', None)
        email = req.get('email', None)
        role = req.get('role', None)
        status = req.get('status', None)

        if name is not None:
            user.name = name
        if email is not None:
            user.email = email
        if role is not None:
            user.role_code = role   # TODO: proper conversion, security checks.
        if status is not None:
            user.status = status    # TODO: proper conversion, security checks.

        db.session.add(user)
        db.session.commit()

        ret = {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'created_time': user.created_time,
            'role': user.role_code,
            'status': user.status
        }

    elif request.method == 'DELETE':
        # TODO: Don't allow deletion of primary admin user.

        db.session.delete(user)
        db.session.commit()

        # TODO: Maybe produce a better result?
        ret = { 'status': 'OK' }

    return jsonify(ret)

##### System routes
@api.route('/system', methods=['GET'])
@api_authorized
def system():
    uptime = ''
    with open('/proc/uptime', 'r') as f:
        seconds = float(f.readline().split()[0])
        uptime = timedelta(seconds=int(seconds))

    (update_available, branch, local_revision, remote_revision, status) = current_app.decoder.updater.check_updates()['webapp']

    ret = {
        'uptime': str(uptime),
        'webapp': {
            'update_available': update_available,
            'update_status': status,
            'branch': branch,
            'revision': local_revision
        }
    }

    return jsonify(ret)

@api.route('/system/reboot', methods=['POST'])
@api_authorized
def system_reboot():
    # TODO: Uncomment and test on something NOT my workstation.
    #sh.reboot()
    
    return jsonify({ 'status': 'OK' })

@api.route('/system/shutdown', methods=['POST'])
@api_authorized
def system_shutdown():
    # TODO: Uncomment and test on something NOT my workstation.
    #sh.shutdown()
    
    return jsonify({ 'status': 'OK' })
