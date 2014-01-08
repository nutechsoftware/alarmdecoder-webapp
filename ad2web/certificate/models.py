# -*- coding: utf-8 -*-

from sqlalchemy import Column, types

from ..extensions import db
from .constants import CERTIFICATE_TYPES, CA, SERVER, CLIENT, INTERNAL, CERTIFICATE_STATUS, REVOKED, ACTIVE

class Certificate(db.Model):
    __tablename__ = 'certificates'

    id = Column(db.Integer, primary_key=True, autoincrement=True)
    name = Column(db.String(32), unique=True, nullable=False)
    serial_number = Column(db.String(128), nullable=False)
    status = Column(db.SmallInteger, nullable=False)
    type = Column(db.SmallInteger, nullable=False)
    certificate = Column(db.Text, nullable=False)
    key = Column(db.Text, nullable=False)
    created_on = Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    revoked_on = Column(db.TIMESTAMP)

    @classmethod
    def get_by_id(cls, user_id):
        return cls.query.filter_by(id=user_id).first_or_404()
