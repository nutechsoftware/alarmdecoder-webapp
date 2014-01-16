from flask import Blueprint, render_template, current_app, request, flash
from flask.ext.login import login_required, current_user

from ..extensions import db
from ..decorators import admin_required
from ..settings import Setting
from .forms import EditNotificationForm
from .models import Notification, NotificationSetting
from .constants import NOTIFICATION_TYPES, EMAIL

notifications = Blueprint('notifications', __name__, url_prefix='/notifications')

@notifications.route('/')
@login_required
def index():
    notification_list = Notification.query.all()

    return render_template('notifications/index.html', notifications=notification_list, active='notifications')

@notifications.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    notification = Notification.query.filter_by(id=id).first_or_404()

    form = EditNotificationForm(obj=notification)
    if form.validate_on_submit():
        pass

    return render_template('notifications/edit.html', form=form, active='notifications')

@notifications.route('/view/<int:id>')
@login_required
def view(id):
    notification = Notification.query.filter_by(id=id).first_or_404()

    return render_template('notifications/view.html', notification=notification, active='notifications')

@notifications.route('/create')
@login_required
def create():
    form = EditNotificationForm()

    if form.validate_on_submit():
        pass

    return render_template('notifications/edit.html', form=form, active='notifications')
