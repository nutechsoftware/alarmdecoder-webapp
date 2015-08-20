# -*- coding: utf-8 -*-

import datetime
import signal
import sys

import werkzeug.serving
from werkzeug.debug import DebuggedApplication
from flask.ext.script import Manager, Command

from alarmdecoder.util import NoDeviceError
from ad2web import create_app, init_app
from ad2web.decoder import Decoder
from ad2web.extensions import db

import logging

app, appsocket = None, None

def _create_app(**kwargs):
    global app, appsocket

    app, appsocket = create_app()

    return app


class RunCommand(Command):
    def run(self):
        """Run in local machine."""

        @werkzeug.serving.run_with_reloader
        def runDebugServer():
            try:
                init_app(app, appsocket)

                app.debug = True
                dapp = DebuggedApplication(app, evalex=True)
                appsocket.serve_forever()

            except Exception, err:
                app.logger.error("Error", exc_info=True)

        try:
            runDebugServer()
        except:
            pass


class InitDBCommand(Command):
    def run(self):
        """Init/reset database."""

        try:
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
        except Exception, err:
            print("Database initialization failed: {0}".format(err))
        else:
            print("Database initialization complete!")


manager = Manager(_create_app)
manager.add_command('run', RunCommand())
manager.add_command('initdb', InitDBCommand())
manager.add_option('-c', '--config',
                   dest="config",
                   required=False,
                   help="config file")

if __name__ == "__main__":
    manager.run()
