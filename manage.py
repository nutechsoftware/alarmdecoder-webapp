# -*- coding: utf-8 -*-

from flask.ext.script import Manager

from ad2web import create_app
from ad2web.extensions import db
from ad2web.user import User, UserDetail, ADMIN, ACTIVE
from ad2web.certificate import Certificate
from ad2web.settings import Setting
from ad2web.utils import MALE


app = create_app()
manager = Manager(app)


@manager.command
def run():
    """Run in local machine."""

    app.run(host='0.0.0.0')


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

    sn = Setting(name="serialnumber", value=1)
    db.session.add(sn)

    db.session.commit()


manager.add_option('-c', '--config',
                   dest="config",
                   required=False,
                   help="config file")

if __name__ == "__main__":
    manager.run()
