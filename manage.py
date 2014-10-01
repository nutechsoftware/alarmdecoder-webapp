# -*- coding: utf-8 -*-

import datetime
import signal
import sys

import werkzeug.serving
from werkzeug.debug import DebuggedApplication
from flask.ext.script import Manager

from alarmdecoder.util import NoDeviceError
from ad2web import create_app
from ad2web.decoder import Decoder
from ad2web.extensions import db

app, appsocket = create_app()
manager = Manager(app)

@manager.command
def run():
    """Run in local machine."""

    @werkzeug.serving.run_with_reloader
    def runDebugServer():
        try:
            app.debug = True
            dapp = DebuggedApplication(app, evalex=True)
            appsocket.serve_forever()

        except Exception, err:
            app.logger.error("Error", exc_info=True)

    runDebugServer()

@manager.command
def initdb():
    """Init/reset database."""

    db.drop_all()
    db.create_all()

    # Initialize alembic revision
    from alembic.config import Config
    from alembic import command
    alembic_cfg = Config('alembic.ini')
    command.stamp(alembic_cfg, "head")

    from ad2web.notifications.models import NotificationMessage
    from ad2web.notifications.constants import DEFAULT_EVENT_MESSAGES

    for event, message in DEFAULT_EVENT_MESSAGES.iteritems():
        db.session.add(NotificationMessage(id=event, text=message))

    db.session.commit()

manager.add_option('-c', '--config',
                   dest="config",
                   required=False,
                   help="config file")

if __name__ == "__main__":
    manager.run()
