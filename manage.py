# -*- coding: utf-8 -*-

import datetime
import signal
import sys

from flask.ext.script import Manager

from ad2web import create_app, create_decoder_socket
from ad2web.decoder import Decoder
from ad2web.extensions import db
from ad2web.user import User, UserDetail, ADMIN, USER, ACTIVE
from ad2web.certificate import Certificate
from ad2web.log import EventLogEntry
from ad2web.settings import Setting
from ad2web.utils import MALE
from ad2web.notifications import Notification, NotificationSetting
from ad2web.zones import Zone

decoder = Decoder(None, None)
app = create_app()
manager = Manager(app)
appsocket = create_decoder_socket(app)

def signal_handler(signal, frame):
    decoder.close()
    appsocket.stop()

@manager.command
def run():
    """Run in local machine."""

    signal.signal(signal.SIGINT, signal_handler)

    app.decoder = decoder
    decoder.app = app
    decoder.websocket = appsocket
    decoder.open()

    appsocket.serve_forever()

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
                role_code=USER,
                status_code=ACTIVE)
    db.session.add(user)


    db.session.add(Setting(name="serialnumber", value=1))
    db.session.commit()

    ca_cert = Certificate(
                name="AlarmDecoder CA",
                description='CA certificate used for authenticating others.',
                serial_number=1,
                status=1,
                type=0,
                certificate='''
-----BEGIN CERTIFICATE-----
MIIDPzCCAiegAwIBAgIBATANBgkqhkiG9w0BAQUFADAyMRYwFAYDVQQKEw1BbGFy
bSBEZWNvZGVyMRgwFgYDVQQDEw9BbGFybURlY29kZXIgQ0EwHhcNMTMxMjA2MjMw
ODMzWhcNMzMxMjAxMjMwODMzWjAyMRYwFAYDVQQKEw1BbGFybSBEZWNvZGVyMRgw
FgYDVQQDEw9BbGFybURlY29kZXIgQ0EwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAw
ggEKAoIBAQDsUP9m4oT6557SwJIjxfPLv53yQk+Sc+Po/5fXAYJcJEnvqFcWCNdW
9gzu9s/aR/pFjxRqDLWWrUedUK8zT0gwztsLNc7RF3n0qXL5oWvSLtgPOKJQA5us
J4zUKatNOmlW0Gpmg/MWqcXvv/SBmCZdukhlwY6yITHCkQhAyO9Ys1XqBghQmuxA
raPkvRfromuuUjfxl0zRTjtAABlriyeubmdD1pkJF65jDRtoMaeddhO/qZq9OYjt
PJ3pe+dRsOm3/se/euj9XPOjnIrtkP/bGbtMtilZGOSeHUAlteO2BVCnZpttbdBG
JyPO0+4eKxbatP8xrgMhP75JleUl7F/rAgMBAAGjYDBeMA4GA1UdDwEB/wQEAwIC
BDAMBgNVHRMEBTADAQH/MB0GA1UdDgQWBBRcQvGo7jWMvlPQ85tfvbTqPVunJDAf
BgNVHSMEGDAWgBRcQvGo7jWMvlPQ85tfvbTqPVunJDANBgkqhkiG9w0BAQUFAAOC
AQEAmv3YAm8hSjzO0Ak0JJ9qcy88mLjqU3SlYKoC8AkCM1gdcFLLmGELTzyFdTyp
LoCksv+O689+FpE18iulF2T1oQvTCY2hcXiQFPVNKkUXxhRNRtlCwtkDXMKZppp7
QkoZHLweEh3TMouCasXyai3+7rskhwe/RSObci0JTMsk5rSm71S4YoArAOD/kJD5
A3inJ+ZXglQM4oZmuEIm5GD52Qnt1wX/nBkRAqO19dEAKbO7jq7vH/cRrlqc1sqr
etIezomA8s9gBUofEFSfdP7F2jMQJGFOH8iUDW/J+Bo6aZJvP14rVf2JZ97/lAUf
W9fU1HMlZF/TKfROFIIdUbTpxg==
-----END CERTIFICATE-----''', key='''
-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDsUP9m4oT6557S
wJIjxfPLv53yQk+Sc+Po/5fXAYJcJEnvqFcWCNdW9gzu9s/aR/pFjxRqDLWWrUed
UK8zT0gwztsLNc7RF3n0qXL5oWvSLtgPOKJQA5usJ4zUKatNOmlW0Gpmg/MWqcXv
v/SBmCZdukhlwY6yITHCkQhAyO9Ys1XqBghQmuxAraPkvRfromuuUjfxl0zRTjtA
ABlriyeubmdD1pkJF65jDRtoMaeddhO/qZq9OYjtPJ3pe+dRsOm3/se/euj9XPOj
nIrtkP/bGbtMtilZGOSeHUAlteO2BVCnZpttbdBGJyPO0+4eKxbatP8xrgMhP75J
leUl7F/rAgMBAAECggEAdcRXw1oXk0Jib/zv10wLFvrDJ7vME9wVNERL0yY5ZNng
zsJBxAVb60ZrY5s0Mj+0hX2sWr1CsXhhPBC9fwB/pXMwzgFes+zTJg5b8fNz3Cbk
HZHHscBakAyVrhWl/LKjVFRA8h3Hwv+QWM58dyjv1b3D3pH7HuJT/fZw+ngobzba
2g0aau6oxiqL/bwJUT0DyFStfCBdaVj2uxBiQqXMEIRbOuj7yd6Tb+Y5aIkX74Uz
cixdcKb5+9VOHeac4EL9aHnWaGxEl+JEGPowMLKkP7UfFRolngPfykOsBNvAGf9d
2p+WqeyMzEF5VRMHAANSx7peQBiXLqKyEbjXGsxooQKBgQD8c0cAYnQRhxnZ0SXQ
F4bDaPXLC82+T1Sf6zZd5DDDhAqlPv8rnDHs4aEfr8iWYbQaFAfOm8UE27UlLUuf
kswlX2gCy8C7Jsi89cd+4CxfXchxHwG3+zcij0kGY0CShpo+rhuRWON6GBFSIYTK
eBVbS9JHMmuC2RZM9KSmqYb4VwKBgQDvo6UBCEK61QRMsTw86FgRMzQvUDeoVFZZ
bSAJsz9P5KgUK5+5BvsI2KpFqUdLy/Fbt5xIQCWUMYPhzm42coyeodYUmml3tJnT
c59ca25Ow6nnXeKi51rEjKd3bW4JHx5hkHe1MeSs9bGyBYDVbgHFINuWBao5PcTr
GtppkXgojQKBgQDIOH2VloBL7oTYNoLw+dfOYA6hjakOSUjq1Nh3uyXZy33N9ZrX
8be/EmyB/x7t9murSzut5+loowCWjcgutXToJzUNEqC3TlljVON2g0FuGamB3n+0
dbAS3uWiBVIPZGYtVFVU/9Ta3v/NzfvNwVPe5tHN2fVe/+IqAtYbwNTlXQKBgAvw
Sisn/zMRo7oyZj7ekGyi8WmeBHfVY8vmvN7e2Duht6Hxnm54Y49IRAteaJflHCwm
lJmg4H5mjRx1zVXXFRxeEa1LGBAHplY7f2f6Ti+MXe2R5tWY0xPRshIoGIBJ1Zik
uuIDD1Jylxy4W3fGmD366hWqSJW7dxEDcHgr8CGNAoGAfaYV/4eLDVsXnRFTPqOA
xxmsu8vWJSkqSrO+Vnzcks3RbF9evMnsUNZjSGvddLD62ytwqlnqxYOMqbeAyxnO
T3a1ZjHA1CSOfHU3e81cyRkXjw2t3MpYjn0/8IAKz6CWKdOfgmX/TigrM2+Cs1Ns
F6F8aKjZ3Ze8mGhApbGXFwo=
-----END PRIVATE KEY-----''')
    #ca_cert.generate(common_name='AlarmDecoder CA')
    ca_cert.init_on_load()
    db.session.add(ca_cert)
    
    cert = Certificate(
            name="AlarmDecoder Internal",
            description='Test Cert',
            serial_number=2,
            status=1,
            type=2)
    cert.generate(common_name='AlarmDecoder Internal', parent=ca_cert)
    db.session.add(cert)

    notification = Notification(description='Test Email', type=0, user=user)
    notification.settings['source'] = NotificationSetting(name='source', value='root@localhost')
    notification.settings['destination'] = NotificationSetting(name='destination', value='root@localhost')
    notification.settings['server'] = NotificationSetting(name='server', value='localhost')
    notification.settings['username'] = NotificationSetting(name='username', value='')
    notification.settings['password'] = NotificationSetting(name='password', value='')
    db.session.add(notification)

    db.session.add(Zone(zone_id=22, name='Some zone', description='This is some zone.'))
    db.session.add(EventLogEntry(type=0, message='Panel armed..'))
    db.session.add(EventLogEntry(type=1, message='Panel disarmed..'))
    db.session.add(EventLogEntry(type=3, message='Alarming!  Oh no!'))
    db.session.add(EventLogEntry(type=4, message='Fire!  Oh no!'))

    db.session.add(Setting(name='device_type', value='AD2PI'))
    db.session.add(Setting(name='device_location', value='network'))
    db.session.add(Setting(name='device_address', value='localhost'))
    db.session.add(Setting(name='device_port', value=10000))
    db.session.add(Setting(name='use_ssl', value=True))

    db.session.commit()

manager.add_option('-c', '--config',
                   dest="config",
                   required=False,
                   help="config file")

if __name__ == "__main__":
    manager.run()

