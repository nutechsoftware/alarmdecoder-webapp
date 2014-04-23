# -*- coding: utf-8 -*-

# http://docs.fabfile.org/en/1.5/tutorial.html

import os

from fabric.api import *
from flask.ext.script import Manager
import git
import git.exc

from ad2web import create_app
from ad2web.extensions import db
from ad2web.utils import INSTANCE_FOLDER_PATH
from ad2web.settings import Setting
from ad2web.certificate import Certificate
from ad2web.certificate.constants import ACTIVE, CA, SERVER, INTERNAL, CLIENT
from ad2web.decoder import Decoder
from ad2web.ser2sock import ser2sock
from ad2web.updater import Updater

project = "ad2web"

# the user to use for the remote commands
env.user = ''
# the servers where the commands are executed
env.hosts = ['']


def reset():
    """
    Reset local debug env.
    """

    local("rm -rf {0}".format(INSTANCE_FOLDER_PATH))
    local("mkdir {0}".format(INSTANCE_FOLDER_PATH))
    local("python manage.py initdb")


def setup():
    """
    Setup virtual env.
    """

    local("virtualenv env")
    activate_this = "env/bin/activate_this.py"
    execfile(activate_this, dict(__file__=activate_this))
    local("python setup.py install")
    reset()


def d():
    """
    Debug.
    """

    reset()
    local("python manage.py run")


def certs():
    reset()

    decoder = Decoder(None, None)
    app, appsocket = create_app()
    manager = Manager(app)

    with app.app_context():
        config_path = Setting(name='ser2sock_config_path', value='/etc/ser2sock')
        db.session.add(config_path)
        db.session.commit()

        ca = Certificate(name='AlarmDecoder CA', status=ACTIVE, type=CA)
        ca.generate(ca.name)

        server = Certificate(name='AlarmDecoder Server', status=ACTIVE, type=SERVER)
        server.generate(server.name, parent=ca)

        internal = Certificate(name='AlarmDecoder Internal', status=ACTIVE, type=INTERNAL)
        internal.generate(internal.name, parent=ca)

        test_1 = Certificate(name='Test #1', status=ACTIVE, type=CLIENT)
        test_1.generate(test_1.name, parent=ca)

        test_2 = Certificate(name='Test #2', status=ACTIVE, type=CLIENT)
        test_2.generate(test_2.name, parent=ca)

        db.session.add(ca)
        db.session.add(server)
        db.session.add(internal)
        db.session.add(test_1)
        db.session.add(test_2)
        db.session.commit()

        path = os.path.join(os.path.sep, 'etc', 'ser2sock', 'certs')
        ca.export(path)
        server.export(path)
        internal.export(path)
        test_1.export(path)
        test_2.export(path)

        Certificate.save_certificate_index()
        Certificate.save_revocation_list()

        ser2sock.hup()

def revoke_cert(name):
    print 'Revoking: ', name

    decoder = Decoder(None, None)
    app, appsocket = create_app()
    manager = Manager(app)

    with app.app_context():
        cert = Certificate.query.filter_by(name=name).first()

        if cert is not None:
            cert.revoke()

            Certificate.save_certificate_index()
            Certificate.save_revocation_list()

            ser2sock.hup()

            db.session.add(cert)
            db.session.commit()

            print name, 'successfully revoked.'
        else:
            print name, 'not found.'

def update():
    u = Updater()

    update_needed = u.check_updates()

    if len(update_needed):
        print 'The following components need an update: '

        for component, (branch, local_revision, remote_revision) in update_needed.items():
            print 'Component: ', component, local_revision, '->', remote_revision

        print 'Updating components..'
        u.update()
        print 'Complete!'
    else:
        print 'No update necessary.'

def babel():
    """
    Babel compile.
    """

    local("python setup.py compile_catalog --directory `find -name translations` --locale zh -f")
