# -*- coding: utf-8 -*-

from sqlalchemy import Column, types

from ..extensions import db

class KeypadButton(db.Model):
    __tablename__ = 'buttons'

    button_id = Column(db.Integer, primary_key=True)
    user_id = Column(db.Integer, nullable=False)
    label = Column(db.String(32), nullable=False)
    code = Column(db.String(32))

    @classmethod
    def get_label(cls, id):
        button = cls.query.filter_by(button_id=id).first()

        return button.label if button is not None else None
