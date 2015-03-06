# -*- coding: utf-8 -*-

from sqlalchemy import Column, types
from sqlalchemy.ext.mutable import Mutable

from ..extensions import db

class Camera(db.Model):
    __tablename__ = 'cameras'

    id = Column(db.Integer, primary_key=True)
    name = Column(db.String(32), nullable=False)
    username = Column(db.String(32))
    password = Column(db.String(255))
    get_jpg_url = Column(db.String(255))
    user_id = Column(db.Integer, nullable=False)

    @classmethod
    def get_name(cls, camera_name):
        camera = cls.query.filter_by(name=camera_name).first()

        return camera.name if camera is not None else None
