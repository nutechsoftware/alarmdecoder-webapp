# -*- coding: utf-8 -*-

import datetime

from flask.ext.script import Manager

from ad2web import create_app, create_decoder_socket
from ad2web.decoder import Decoder, decoder
from ad2web.extensions import db
from ad2web.user import User, UserDetail, ADMIN, ACTIVE
from ad2web.certificate import Certificate
from ad2web.log import EventLogEntry
from ad2web.settings import Setting
from ad2web.utils import MALE
from ad2web.notifications import Notification, NotificationSetting
from ad2web.zones import Zone


app = create_app()
manager = Manager(app)
appsocket = create_decoder_socket(app)

@manager.command
def run():
    """Run in local machine."""

    try:
        decoder.app = app
        decoder.websocket = appsocket
        decoder.open()

        appsocket.serve_forever()

    finally:
        decoder.close()

@manager.command
def initdb():
    """Init/reset database."""

    db.drop_all()
    db.create_all()

    admin = User(
            name=u'admin',
            email=u'admin@example.com',
            password=u'testing',
            role_code=ADMIN,
            status_code=ACTIVE)
    db.session.add(admin)

    user = User(name=u'testing',
                email=u'test@test.com',
                password=u'testing',
                role_code=ADMIN,
                status_code=ACTIVE)
    db.session.add(user)

    cert = Certificate(
                name="AlarmDecoder CA",
                description='CA certificate used for authenticating others.',
                serial_number=1,
                status=1,
                type=0)
    cert.generate(common_name='Testing')
    db.session.add(cert)

    entry = EventLogEntry(type=0, message='Panel armed..')
    db.session.add(entry)
    entry = EventLogEntry(type=1, message='Panel disarmed..')
    db.session.add(entry)
    entry = EventLogEntry(type=3, message='Alarming!  Oh no!')
    db.session.add(entry)
    entry = EventLogEntry(type=4, message='Fire!  Oh no!')
    db.session.add(entry)

    sn = Setting(name="serialnumber", value=1)
    db.session.add(sn)

    notification = Notification(description='Test Email', type=0)
    notification.settings['source'] = NotificationSetting(name='source', value='root@localhost')
    notification.settings['destination'] = NotificationSetting(name='destination', value='root@localhost')
    notification.settings['server'] = NotificationSetting(name='server', value='localhost')
    notification.settings['username'] = NotificationSetting(name='username', value='')
    notification.settings['password'] = NotificationSetting(name='password', value='')
    db.session.add(notification)

    zone = Zone(zone_id=22, name='Some zone', description='This is some zone.')
    db.session.add(zone)

    db.session.commit()

manager.add_option('-c', '--config',
                   dest="config",
                   required=False,
                   help="config file")

if __name__ == "__main__":
    manager.run()
