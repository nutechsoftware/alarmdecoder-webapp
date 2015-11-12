# -*- coding: utf-8 -*-

from sqlalchemy import Column, types

from ..extensions import db

class APIKey(db.Model):
    __tablename__ = 'apikeys'

    id = Column(db.Integer, primary_key=True)
    user_id = Column(db.Integer, db.ForeignKey('users.id'))
    key = Column(db.String(64))
