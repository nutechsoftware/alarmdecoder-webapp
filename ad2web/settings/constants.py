# -*- coding: utf-8 -*-

from ..setup.constants import NETWORK_DEVICE, SERIAL_DEVICE
from ..user import User, UserDetail
from ..settings import Setting
from ..certificate import Certificate
from ..notifications import Notification, NotificationSetting, NotificationMessage
from ..zones import Zone
from ..keypad import KeypadButton
from ..cameras import Camera

HOSTS_FILE = '/etc/hosts'
HOSTNAME_FILE = '/etc/hostname'
NETWORK_FILE = '/etc/network/interfaces'

EXPORT_MAP = {
    'settings.json': Setting,
    'certificates.json': Certificate,
    'notifications.json': Notification,
    'notification_settings.json': NotificationSetting,
    'notification_messages.json': NotificationMessage,
    'users.json': User,
    'user_details.json': UserDetail,
    'zones.json': Zone,
    'buttons.json': KeypadButton,
    'cameras.json': Camera
}


KNOWN_MODULES = [ 'heapq', 'code', 'functools', 'random', 'cffi', 'tty', 'datetime', 'sysconfig', 'gc', 'pty', 'xml', 
 'importlib', 'flask', 'base64', 'collections', 'imp', 'itsdangerous', 'ConfigParser', 'zipimport',
 'SocketServer', 'string', 'zipfile', 'httplib2', 'textwrap', 'markupsafe', 'jinja2', 'subprocess', 'twilio', 'decimal',
 'compiler', 'httplib', 'resource', 'bisect', 'quopri', 'uuid', 'psutil', 'token', 'greenlet', 'usb', 'signal', 'dis',
 'cStringIO', 'openid', 'locale', 'stat', 'atexit', 'gevent', 'HTMLParser', 'encodings',
 'BaseHTTPServer', 'jsonpickle', 'calendar', 'abc', 'threading', 'warnings', 'tarfile', 'urllib', 're',
 'werkzeug', 'posix', 'email', 'math', 'cgi', 'blinker', 'ast', 'UserDict', 'inspect', 'urllib2', 'Queue',
 'exceptions', 'ctypes', 'codecs', 'posixpath', 'fcntl', 'logging', 'socket', 'thread', 'StringIO', 'traceback', 'unicodedata',
 'weakref', 'tempfile', 'itertools', 'opcode', 'wtforms', 'os', 'marshal', 'alembic', 'pprint', 'binascii', 'unittest',
 'pycparser', 'chump', 'pygments', 'operator', 'array', 'gntp', 'select', 'pkgutil', 'platform', 'errno', 'cv2', 'symbol', 'zlib',
 'json', 'tokenize', 'numpy', 'sleekxmpp', 'cPickle', 'sqlalchemy', 'termios', 'site', 'hashlib',
 'pwd', 'pytz', 'copy', 'cryptography', 'smtplib', 'keyword', 'socketio', 'uu', 'stringprep', 'markupbase',
 'fnmatch', 'getpass', 'mimetools', 'pickle', 'parser', 'ad2web', 'contextlib', 'numbers', 'io', 'pyexpat',
 'shutil', 'serial', 'mako', 'grp', 'alarmdecoder', 'six', 'genericpath', 'OpenSSL', 'gettext', 'sqlite3',
 'mimetypes', 'rfc822', 'pyftdi', 'glob', 'time', 'htmlentitydefs', 'struct', 'sys', 'codeop', 'ssl', 'geventwebsocket',
 'types', 'strop', 'argparse', 'sitecustomize', 'pyasn1', 'difflib', 'urlparse', 'linecache', 'sh', 'netifaces', 'babel', 'gzip', 'hmac' ]
