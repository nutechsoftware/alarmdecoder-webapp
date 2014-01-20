# -*- coding: utf-8 -*-

from sqlalchemy import Column, types
from sqlalchemy.ext.mutable import Mutable

from ..extensions import db


class Zone(db.Model):
    __tablename__ = 'zones'

    id = Column(db.Integer, primary_key=True)
    zone_id = Column(db.Integer, unique=True, nullable=False)
    name = Column(db.String(32), nullable=False)
    description = Column(db.String(255))

    @classmethod
    def get_name(cls, id):
        zone = cls.query.filter_by(zone_id=id).first()

        return zone.name if zone is not None else None
