# -*- coding: utf-8 -*-

from flask import Blueprint, current_app, request, jsonify
from flask.ext.login import login_user, current_user, logout_user

from ..user import User


api = Blueprint('api', __name__, url_prefix='/api/v1')

# TODO: KEEP OR REMOVE THESE?
@api.route('/login', methods=['POST'])
def login():
    if current_user.is_authenticated():
        return jsonify(flag='success')

    username = request.form.get('username')
    password = request.form.get('password')
    if username and password:
        user, authenticated = User.authenticate(username, password)
        if user and authenticated:
            if login_user(user, remember='y'):
                return jsonify(flag='success')

    current_app.logger.debug('login(api) failed, username: %s.' % username)
    return jsonify(flag='fail', msg='Sorry, try again.')


@api.route('/logout')
def logout():
    if current_user.is_authenticated():
        logout_user()
    return jsonify(flag='success', msg='Logouted.')

# /TODO

##### AlarmDecoder device routes
@api.route('/alarmdecoder', methods=['GET'])
def alarmdecoder():
    return jsonify(status='OK')

@api.route('/alarmdecoder/send', methods=['POST'])
def alarmdecoder_send():
    pass

@api.route('/alarmdecoder/reboot', methods=['POST'])
def alarmdecoder_reboot():
    pass

@api.route('/alarmdecoder/configuration', methods=['GET', 'PUT'])
def alarmdecoder_configuration():
    pass


##### Zone routes
@api.route('/zones', methods=['GET', 'POST'])
def zones():
    pass

@api.route('/zones/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def zones_by_id(id):
    pass

@api.route('/zones/<int:id>/fault', methods=['POST'])
def zones_fault(id):
    pass


##### Notification routes
@api.route('/notifications', methods=['GET', 'POST'])
def notifications():
    pass

@api.route('/notifications/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def notifications_by_id(id):
    pass


##### Camera routes
@api.route('/cameras', methods=['GET', 'POST'])
def cameras():
    pass

@api.route('/cameras/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def cameras_by_id(id):
    pass


##### User routes
@api.route('/users', methods=['GET', 'POST'])
def users():
    pass

@api.route('/users/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def users_by_id(id):
    pass


##### System routes
@api.route('/system', methods=['GET'])
def system():
    pass

@api.route('/system/reboot', methods=['POST'])
def system_reboot():
    pass

@api.route('/system/shutdown', methods=['POST'])
def system_shutdown():
    pass
