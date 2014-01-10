# -*- coding: utf-8 -*-

from gevent import monkey
monkey.patch_all(thread=False)

from socketio import socketio_manage
from socketio.namespace import BaseNamespace
from socketio.mixins import BroadcastMixin
from socketio.server import SocketIOServer

from flask import Blueprint, Response, request, g


PORT = 5000

sock = Blueprint('sock', __name__, url_prefix='/socket.io')

def create_socket(app, port=PORT):
    return SocketIOServer(('', port), app, resource="socket.io")

class AppNamespace(BaseNamespace, BroadcastMixin):
    def initialize(self):
        self._alarmdecoder = self.request

    def on_keypress(self, key):
        print 'sending keypress: {0}'.format(key)
        self._alarmdecoder.send(key)
        self.broadcast_event('message', 'hi')

@sock.route('/<path:remaining>')
def handle_socketio(remaining):
    try:
        socketio_manage(request.environ, {'/alarmdecoder': AppNamespace}, g.alarmdecoder)

    except Exception, err:
        import traceback
        traceback.print_exc(err)
        #print err
        #.logger.error("Exception while handling socketio connection", exc_info=True)

    return Response()
