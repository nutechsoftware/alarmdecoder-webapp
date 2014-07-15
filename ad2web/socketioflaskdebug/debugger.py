# -*- coding: utf-8 -*-

from werkzeug.debug import DebuggedApplication
from types import GeneratorType
import sys


class SocketIODebugger(DebuggedApplication):

    def __init__(self, app, **kwargs):
        """
        The arguments are the same as for DebuggedApplication in werkzeug.debug, with
        the only addition being the `namespace` keyword argument -- if specified, all
        handlers of the namespace will be wrapped in try/except clauses and exceptions
        will be propagated to the app and also emitted to the client via sockets.
        """
        namespace = kwargs.pop('namespace', None)
        self.exc_info = None
        super(SocketIODebugger, self).__init__(app, **kwargs)
        if namespace is not None:
            self.protect_namespace(namespace)
            if hasattr(self.app, 'before_request'):
                self.app.before_request(self.route_debugger)
            else:
                print 'app.before_request() not found, please route it yourself.'

    def protect_namespace(self, namespace):
        """
        Use `exception_handler_decorator` property of socketio.namespace.BaseNamespace
        to inject exception catching into the handlers. Try to preserve the original
        traceback if possible for reraising it later.
        """
        def protect_method(ns_instance, f):
            def protected_method(*args, **kwargs):
                try:
                    return f(*args, **kwargs)
                except:
                    try:
                        self.exc_info = sys.exc_info()
                        ns_instance.emit('exception')
                    except:
                        pass
            return protected_method
        namespace.exception_handler_decorator = protect_method

    def __call__(self, environ, start_response):
        """
        This function extracts the results from the generator returned by the __call__
        method of werkzeug.debug.DebuggedApplication in case of socket requests.
        """
        result = super(SocketIODebugger, self).__call__(environ, start_response)
        if 'socketio' in environ and isinstance(result, GeneratorType):
            for _ in result:
                pass
        return result

    def route_debugger(self):
        """
        Before each request, see if any exceptions occured in the namespace; if so,
        throw an exception so it gets caught by Werkzeug. We try to preserve the
        original traceback so the debugger messages are more informative.
        """
        if self.exc_info is not None:
            exc_type, exc_value, exc_traceback = self.exc_info
            self.exc_info = None
            raise exc_type, exc_value, exc_traceback
