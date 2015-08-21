# -*- coding: utf-8 -*-

import sys, os, pwd
import threading

project = "ad2web"

# Use instance folder, instead of env variables.
# specify dev/production config
#os.environ['%s_APP_CONFIG' % project.upper()] = ''
# http://code.google.com/p/modwsgi/wiki/ApplicationIssues#User_HOME_Environment_Variable
#os.environ['HOME'] = pwd.getpwuid(os.getuid()).pw_dir

BASE_DIR = os.path.join(os.path.dirname(__file__))
# activate virtualenv
# activate_this = os.path.join(BASE_DIR, "env/bin/activate_this.py")
# execfile(activate_this, dict(__file__=activate_this))

if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# give wsgi the "application"

from ad2web import create_app, init_app

class SocketIOThread(threading.Thread):
	def __init__(self, appsocket):
		threading.Thread.__init__(self)
		self._appsocket = appsocket

	def run(self):
		self._appsocket.serve_forever()

application, appsocket = create_app()
init_app(application, appsocket)
socket_thread = SocketIOThread(appsocket)
socket_thread.start()
