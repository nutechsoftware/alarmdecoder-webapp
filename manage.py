# -*- coding: utf-8 -*-

from flask.ext.script import Manager

from ad2web import create_app, create_decoder_socket
from ad2web.decoder import Decoder, decoder
from ad2web.extensions import db
from ad2web.user import User, UserDetail, ADMIN, ACTIVE
from ad2web.certificate import Certificate
from ad2web.log import EventLogEntry, PanelLogEntry
from ad2web.settings import Setting
from ad2web.utils import MALE


app = create_app()
manager = Manager(app)
appsocket = create_decoder_socket(app)

@manager.command
def run():
    """Run in local machine."""

    try:
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

    entry = PanelLogEntry(message='[0000000100000010----],111,[f700001800110002080200000100ff],"CHECK 111 WIRE  EXPANSION       "')
    db.session.add(entry)
    entry = PanelLogEntry(message='[0000000100000010----],041,[f70000871041000208020000000000],"CHECK 41                        "')
    db.session.add(entry)
    entry = PanelLogEntry(message='[0000000100000010----],112,[f700001800120002080200000100ff],"CHECK 112 RELAY MODULE          "')
    db.session.add(entry)
    entry = PanelLogEntry(message='[0000000100010000----],008,[f70000871008004c08020000000000],"SYSTEM LO BAT                   "')
    db.session.add(entry)

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

    db.session.commit()

manager.add_option('-c', '--config',
                   dest="config",
                   required=False,
                   help="config file")

if __name__ == "__main__":
    manager.run()
