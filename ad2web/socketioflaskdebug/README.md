SocketIO-Flask-Debug
====================

Holy cow, I have finally made the Werkzeug debugger work with gevent-socketio, see below for usage.
```python
# Server-side usage

from socketio.server import SocketIOServer
from socketio.namespace import BaseNamespace
from debugger import SocketIODebugger

class MyNamespace(BaseNamespace):
  def on_my_message(self, data):
    do_something()

app.debug=True
app = SocketIODebugger(app, evalex=True, namespace=MyNamespace)

SocketIOServer((host, port), app, resource='socket.io', policy_server=False).serve_forever()
```
```javascript
// Client-side usage

socket.on("exception", function () {
  window.location.reload(true);
});
```
To test it, run `python app.py`, then browse to http://127.0.0.1:8080 and click on the buttons.

How it works:
- extract the values from the generator returned by `werkzeug.debug.DebuggedApplication` whenever a 
  socket.io request is spotted, this enables to establish the socket connection properly;
- if a namespace is specified, wrap the namespace handlers in debugger's try/catch blocks;
- if an exception is caught within the namespace, save the full original traceback and emit an
  "exception" socket message;
- inject exception reraising into `app.before_request()` which allows forwarding any incoming requests 
  to the debugger if an exception was caught within the namespace.

Python dependencies: `flask`, `werkzeug`, `gevent`, `gevent-socketio`.
