from wtforms.widgets import html_params
from wtforms import Field
from flask import Markup 

class CancelButtonWidget(object):
    html_params = staticmethod(html_params)
    
    def __init__(self, text='Cancel', onclick='', **kwargs):
        self.text = text
        self.onclick = onclick

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)

        if 'onclick' not in kwargs:
            kwargs['onclick'] = self.onclick

        return Markup('<button type="button" class="btn btn-primary" {0}>{1}</button>'.format(self.html_params(name=field.name, **kwargs), self.text))

class CancelButtonField(Field):
    widget = CancelButtonWidget()

    def __init__( self, label='Cancel', validators=None, onclick='', **kwargs):
        super(CancelButtonField, self).__init__('', validators, **kwargs)
        self.widget = CancelButtonWidget(text=label, onclick=onclick)


class BackButtonWidget(object):
    html_params = staticmethod(html_params)

    def __init__(self, text=''):
        self.text = text

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)

        return Markup('<button type="button" onclick="history.back();" {0}>{1}</button>'.format(self.html_params(name=field.name, **kwargs), self.text))


class BackButtonField(Field):
    widget = BackButtonWidget()

    def __init__(self, label='', validators=None, **kwargs):
        super(BackButtonField, self).__init__('', validators, **kwargs)

        self.widget = BackButtonWidget(text=label)
