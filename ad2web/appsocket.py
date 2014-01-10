# -*- coding: utf-8 -*-

from gevent import monkey
monkey.patch_all()

from socketio import socketio_manage
from socketio.namespace import BaseNamespace
from socketio.mixins import BroadcastMixin
from socketio.server import SocketIOServer

from flask import Blueprint, Response, request


PORT = 5000

sock = Blueprint('sock', __name__, url_prefix='/socket.io')

def create_socket(app, port=PORT):
    return SocketIOServer(('', port), app, resource="socket.io")

class AppNamespace(BaseNamespace):
    def initialize(self):
        pass

@sock.route('/<path:remaining>')
def handle_socketio(remaining):
    print 'whadafuck'
    try:
        socketio_manage(request.environ, {'/alarmdecoder': AppNamespace}, request)
    except Exception, err:
        import traceback
        traceback.print_exc(err)
        #print err
        #.logger.error("Exception while handling socketio connection", exc_info=True)

    return Response()
