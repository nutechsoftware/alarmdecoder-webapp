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


KNOWN_MODULES = [ 'heapq', 'code', 'distutils', 'functools', 'random', 'cffi', 'tty', 'datetime', 'sysconfig', 'gc', 'pty', 'xml', 
'PIL', 'importlib', 'flask', 'urllib3', 'base64', 'speaklater', 'collections', 'imp', 'itsdangerous', 'ConfigParser', 'zipimport',
 'SocketServer', 'string', 'zipfile', 'httplib2', 'textwrap', 'markupsafe', 'jinja2', 'subprocess', 'twilio', 'cookielib', 'decimal',
 'sndhdr', 'compiler', 'httplib', 'resource', 'bisect', 'quopri', 'uuid', 'psutil', 'token', 'greenlet', 'usb', 'signal', 'dis',
 'cStringIO', 'google', 'compileall', 'openid', 'locale', 'stat', 'atexit', 'gevent', 'html5lib', 'HTMLParser', 'encodings',
 'BaseHTTPServer', 'jsonpickle', 'calendar', 'dateutil', 'abc', 'threading', 'ujson', 'warnings', 'tarfile', 'urllib', 're',
 'werkzeug', 'posix', 'email', 'math', 'cgi', 'blinker', 'ast', 'optparse', 'UserDict', 'inspect', 'Crypto', 'urllib2', 'Queue',
 'exceptions', 'ctypes', 'codecs', 'posixpath', 'fcntl', 'logging', 'socket', 'thread', 'StringIO', 'traceback', 'unicodedata',
 'weakref', 'tempfile', 'itertools', 'opcode', 'wtforms', 'requests', 'os', 'marshal', 'alembic', 'pprint', 'binascii', 'unittest',
 'pycparser', 'chump', 'pygments', 'operator', 'array', 'gntp', 'select', 'pkgutil', 'platform', 'errno', 'cv2', 'symbol', 'zlib',
 'json', 'Cookie', 'dns', 'tokenize', 'numpy', 'sleekxmpp', 'cPickle', 'sqlalchemy', 'simplejson', 'termios', 'site', 'hashlib',
 'pwd', 'pytz', 'copy', 'cryptography', 'smtplib', 'pycurl', 'keyword', 'socketio', 'imghdr', 'uu', 'stringprep', 'markupbase',
 'chardet', 'fnmatch', 'getpass', 'mimetools', 'pickle', 'FixTk', 'parser', 'ad2web', 'contextlib', 'numbers', 'io', 'pyexpat',
 'shutil', 'serial', 'mako', 'distlib', 'lxml', 'bz2', 'grp', 'alarmdecoder', 'six', 'genericpath', 'OpenSSL', 'gettext', 'sqlite3', 'getopt',
 'csv', 'mimetypes', 'rfc822', 'pyftdi', 'glob', 'time', 'htmlentitydefs', 'struct', 'sys', 'colorama', 'codeop', 'ssl', 'geventwebsocket',
 'types', 'strop', 'argparse', 'sitecustomize', 'pyasn1', 'xmlrpclib', 'difflib', 'urlparse', 'linecache', 'sh', 'netifaces', 'babel', 'gzip', 'hmac' ]
