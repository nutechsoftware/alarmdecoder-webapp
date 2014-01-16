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
            password=u'123456',
            role_code=ADMIN,
            status_code=ACTIVE,
            user_detail=UserDetail(
                sex_code=MALE,
                age=10,
                url=u'http://admin.example.com',
                deposit=100.00,
                location=u'Hangzhou',
                bio=u'admin Guy is ... hmm ... just a admin guy.'))
    db.session.add(admin)

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

    notification = Notification(name='Test Notification')
    notification_setting = NotificationSetting(name='test', value='test')
    notification.settings['test'] = notification_setting
    db.session.add(notification)

    db.session.commit()

manager.add_option('-c', '--config',
                   dest="config",
                   required=False,
                   help="config file")

if __name__ == "__main__":
    manager.run()
