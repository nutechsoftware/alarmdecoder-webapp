# -*- coding: utf-8 -*-

from sqlalchemy import Column, orm

from ..extensions import db
from ..settings.models import Setting

class EventLogEntry(db.Model):
    __tablename__ = 'event_log'

    id = Column(db.Integer, primary_key=True)
    type = Column(db.SmallInteger, nullable=False)
    timestamp = Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), index=True)
    message = Column(db.Text, nullable=False)
