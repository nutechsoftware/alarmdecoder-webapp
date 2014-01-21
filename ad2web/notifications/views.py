from flask import Blueprint, render_template, current_app, request, flash, redirect, url_for, abort
from flask.ext.login import login_required, current_user

from wtforms import FormField

from ..extensions import db
from ..decorators import admin_required
from ..settings import Setting
from .forms import CreateNotificationForm, EditNotificationForm, EmailNotificationForm, GoogleTalkNotificationForm
from .models import Notification, NotificationSetting
from .constants import NOTIFICATION_TYPES, EMAIL, GOOGLETALK

NOTIFICATION_TYPE_DETAILS = {
    'email': (EMAIL, EmailNotificationForm),
    'googletalk': (GOOGLETALK, GoogleTalkNotificationForm),
}

notifications = Blueprint('notifications', __name__, url_prefix='/settings/notifications')

@notifications.context_processor
def notifications_context_processor():
    return {
        'TYPES': NOTIFICATION_TYPES,
        'TYPE_DETAILS': NOTIFICATION_TYPE_DETAILS
    }

@notifications.route('/')
@login_required
def index():
    notification_list = Notification.query.all()

    return render_template('notifications/index.html', notifications=notification_list, active='notifications')

@notifications.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    notification = Notification.query.filter_by(id=id).first_or_404()
    if notification.user != current_user and not current_user.is_admin():
        abort(403)

    type_id, form_type = NOTIFICATION_TYPE_DETAILS[NOTIFICATION_TYPES[notification.type]]
    obj = notification
    if request.method == 'POST':
        obj = None

    form = form_type(obj=obj)

    if not form.is_submitted():
        form.populate_from_settings(id)

    if form.validate_on_submit():
        form.populate_obj(notification)
        form.populate_settings(notification.settings, id=id)

        db.session.add(notification)
        db.session.commit()

        flash('Notification saved.', 'success')

    return render_template('notifications/edit.html', form=form, id=id, notification=notification, active='notifications')

@notifications.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = CreateNotificationForm()

    if form.validate_on_submit():
        return redirect(url_for('notifications.create_by_type', type=form.type.data))

    return render_template('notifications/create.html', form=form, active='notifications')

@notifications.route('/create/<string:type>', methods=['GET', 'POST'])
@login_required
def create_by_type(type):
    if type not in NOTIFICATION_TYPE_DETAILS.keys():
        abort(404)

    type_id, form_type = NOTIFICATION_TYPE_DETAILS[type]
    form = form_type()
    form.type.data = type_id

    if form.validate_on_submit():
        obj = Notification()

        form.populate_obj(obj)
        obj.user = current_user
        form.populate_settings(obj.settings)

        db.session.add(obj)
        db.session.commit()

        flash('Notification created.', 'success')

        return redirect(url_for('notifications.index'))

    return render_template('notifications/create_by_type.html', form=form, type=type, active='notifications')
