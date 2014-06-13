from wtforms.widgets import html_params, ListWidget, CheckboxInput
from wtforms import Field, SelectMultipleField
from flask import Markup 

class ButtonWidget(object):
    html_params = staticmethod(html_params)
    
    def __init__(self, text='', onclick='', **kwargs):
        self.text = text
        self.onclick = onclick

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)

        if 'onclick' not in kwargs:
            kwargs['onclick'] = self.onclick

        return Markup('<button type="button" class="btn" {0}>{1}</button>'.format(self.html_params(name=field.name, **kwargs), self.text))


class ButtonField(Field):
    widget = ButtonWidget()

    def __init__( self, label='', validators=None, onclick='', **kwargs):
        super(ButtonField, self).__init__('', validators, **kwargs)
        self.widget = ButtonWidget(text=label, onclick=onclick)


class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = ListWidget(prefix_label=True)
    option_widget = CheckboxInput()