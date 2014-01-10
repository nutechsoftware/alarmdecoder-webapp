# -*- coding: utf-8 -*-

from gevent import monkey
monkey.patch_all()

from socketio import socketio_manage
from socketio.namespace import BaseNamespace
from socketio.mixins import BroadcastMixin
from socketio.server import SocketIOServer

from flask import Blueprint, Response, request, g
import jsonpickle

from alarmdecoder import AlarmDecoder
from alarmdecoder.devices import SerialDevice


decodersocket = Blueprint('sock', __name__, url_prefix='/socket.io')

def create_decoder_socket(app):
    return SocketIOServer(('', 5000), app, resource="socket.io")


class Decoder(object):
    def __init__(self, websocket):
        self.device = AlarmDecoder(SerialDevice(interface='/dev/ttyUSB2'))
        self.websocket = websocket

    def open(self):
        self.bind_alarmdecoder_events(self.websocket, self.device)
        self.device.open(baudrate=115200)

    def close(self):
        self.device.close()

    def bind_alarmdecoder_events(self, appsocket, decoder):
        def build_event_handler(socket, event_type):
            def event_handler(sender, *args, **kwargs):
                try:

                    message = kwargs.get('message', None)
                    packet = dict(type="event",
                                    name=event_type,
                                    args=jsonpickle.encode(message, unpicklable=False),
                                    endpoint='/alarmdecoder')

                    print 'event', event_type, message
                    for session, sock in socket.sockets.iteritems():
                        sock.send_packet(packet)

                except Exception, err:
                    print 'errrrr', err

            return event_handler

        self.device.on_message += build_event_handler(appsocket, 'message')

decoder = Decoder(None)

class DecoderNamespace(BaseNamespace, BroadcastMixin):
    def initialize(self):
        self._alarmdecoder = self.request

    def on_keypress(self, key):
        print 'sending keypress: {0}'.format(key)
        self._alarmdecoder.device.send(key)

@decodersocket.route('/<path:remaining>')
def handle_socketio(remaining):
    try:
        socketio_manage(request.environ, {'/alarmdecoder': DecoderNamespace}, g.alarmdecoder)

    except Exception, err:
        from flask import current_app
        current_app.logger.error("Exception while handling socketio connection", exc_info=True)

    return Response()
