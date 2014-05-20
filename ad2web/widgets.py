from wtforms.widgets import html_params
from wtforms import Field
from flask import Markup 

class CancelButtonWidget(object):
    text = ''
    html_params = staticmethod(html_params)
    
    def __init__(self, text='cancel', onclick='', **kwargs):
        self.text = text
        self.onclick = onclick

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        if 'value' not in kwargs:
            kwargs['value'] = field._value()
        if 'onclick' not in kwargs:
            kwargs['onclick'] = self.onclick

        return Markup('<button type="button" class="btn btn-primary" {0}>{1}</button>'.format(self.html_params(name=field.name, **kwargs), self.text))

class CancelButton(Field):
    widget = CancelButtonWidget()

    def __init__( self, label='', validators=None, text='Cancel', onclick='', **kwargs):
        super(CancelButton, self).__init__(label, validators, **kwargs)
        self.text = text
        self.widget = CancelButtonWidget(text=text, onclick=onclick)

    def _value(self):
        if self.data:
            return u''.join(self.data)
        else:
            return u''
