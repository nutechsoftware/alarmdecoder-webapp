from flask import (Blueprint, render_template, current_app, request, flash,
                    redirect, url_for, abort)
from flask.ext.login import login_required, current_user

from wtforms import FormField, TextField

from ..extensions import db
from ..settings import Setting
from ..zones import Zone
from .forms import (CreateNotificationForm, EditNotificationForm,
                    EditNotificationMessageForm,
                    EmailNotificationForm, GoogleTalkNotificationForm, PushoverNotificationForm,
                    TwilioNotificationForm, NMANotificationForm, ProwlNotificationForm, GrowlNotificationForm, CustomPostForm, ZoneFilterForm, ReviewNotificationForm)

from .models import Notification, NotificationSetting, NotificationMessage

from .constants import (EVENT_TYPES, NOTIFICATION_TYPES, DEFAULT_SUBSCRIPTIONS, 
                        EMAIL, GOOGLETALK, PUSHOVER, TWILIO, NMA, PROWL, GROWL, CUSTOM, ZONE_FAULT, ZONE_RESTORE)

NOTIFICATION_TYPE_DETAILS = {
    'email': (EMAIL, EmailNotificationForm),
    'googletalk': (GOOGLETALK, GoogleTalkNotificationForm),
    'pushover': (PUSHOVER, PushoverNotificationForm),
    'twilio': (TWILIO, TwilioNotificationForm),
    'NMA': (NMA, NMANotificationForm),
    'prowl': (PROWL, ProwlNotificationForm),
    'growl': (GROWL, GrowlNotificationForm),
    'custom': (CUSTOM, CustomPostForm)
}

notifications = Blueprint('notifications',
                            __name__,
                            url_prefix='/settings/notifications')

@notifications.context_processor
def notifications_context_processor():
    return {
        'TYPES': NOTIFICATION_TYPES,
        'TYPE_DETAILS': NOTIFICATION_TYPE_DETAILS,
        'EVENT_TYPES': EVENT_TYPES,
    }

@notifications.route('/')
@login_required
def index():
    use_ssl = Setting.get_by_name('use_ssl', default=False).value
    notification_list = Notification.query.all()

    return render_template('notifications/index.html',
                            notifications=notification_list,
                            active='notifications',
                            ssl=use_ssl)

@notifications.route('/<int:id>/edit', methods=['GET', 'POST'])
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
        notification.description = form.description.data
        form.populate_settings(notification.settings, id=id)

        db.session.add(notification)
        db.session.commit()

        current_app.decoder.refresh_notifier(id)

        if str(ZONE_FAULT) in form.subscriptions.data or str(ZONE_RESTORE) in form.subscriptions.data:
            return redirect(url_for('notifications.zone_filter', id=notification.id))

        return redirect(url_for('notifications.review', id=notification.id))

    use_ssl = Setting.get_by_name('use_ssl', default=False).value

    return render_template('notifications/edit.html',
                            form=form,
                            id=id,
                            notification=notification,
                            active='notifications',
                            ssl=use_ssl)

@notifications.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = CreateNotificationForm()

    if form.validate_on_submit():
        return redirect(url_for('notifications.create_by_type',
                        type=form.type.data))

    use_ssl = Setting.get_by_name('use_ssl', default=False).value

    return render_template('notifications/create.html',
                            form=form,
                            active='notifications',
                            ssl=use_ssl)

@notifications.route('/create/<string:type>', methods=['GET', 'POST'])
@login_required
def create_by_type(type):
    if type not in NOTIFICATION_TYPE_DETAILS.keys():
        abort(404)

    type_id, form_type = NOTIFICATION_TYPE_DETAILS[type]
    form = form_type()
    form.type.data = type_id

    if not form.is_submitted():
        form.subscriptions.data = [str(k) for k in DEFAULT_SUBSCRIPTIONS]

    if form.validate_on_submit():
        obj = Notification()

        obj.type = form.type.data
        obj.description = form.description.data
        obj.user = current_user
        form.populate_settings(obj.settings)

        db.session.add(obj)
        db.session.commit()

        current_app.decoder.refresh_notifier(obj.id)

        if str(ZONE_FAULT) in form.subscriptions.data or str(ZONE_RESTORE) in form.subscriptions.data:
            return redirect(url_for('notifications.zone_filter', id=obj.id))

        return redirect(url_for('notifications.review', id=obj.id))

    use_ssl = Setting.get_by_name('use_ssl', default=False).value

    return render_template('notifications/create_by_type.html',
                            form=form,
                            type=type,
                            active='notifications',
                            ssl=use_ssl)

def build_zone_list():
    zone_list = [(str(i), "Zone {0:02d}".format(i)) for i in range(1, 100)]

    zones = Zone.query.all()
    zone_list_len = len(zone_list)
    for z in zones:
        if z.zone_id <= zone_list_len - 1:
            zone_list[z.zone_id - 1] = (str(z.zone_id), 'Zone {0:02d} - {1}'.format(z.zone_id, z.name))

    return zone_list

@notifications.route('/<int:id>/zones', methods=['GET', 'POST'])
@login_required
def zone_filter(id):
    form = ZoneFilterForm()
    form.zones.choices = build_zone_list()

    if not form.is_submitted():
        form.populate_from_settings(id=id)

    if form.validate_on_submit():
        obj = Notification.query.filter_by(id=id).first_or_404()
        form.populate_settings(obj.settings)

        db.session.add(obj)
        db.session.commit()

        return redirect(url_for('notifications.review', id=id))

    return render_template('notifications/zone_filter.html', id=id, form=form, active='notifications')

@notifications.route('/<int:id>/remove', methods=['GET', 'POST'])
@login_required
def remove(id):
    notification = Notification.query.filter_by(id=id).first_or_404()
    if notification.user != current_user and not current_user.is_admin():
        abort(403)

    db.session.delete(notification)
    db.session.commit()

    current_app.decoder.refresh_notifier(id)

    flash('Notification deleted.', 'success')
    return redirect(url_for('notifications.index'))

@notifications.route('/<int:id>/review', methods=['GET', 'POST'])
@login_required
def review(id):
    form = ReviewNotificationForm()

    notification = Notification.query.filter_by(id=id).first_or_404()
    if notification.user != current_user and not current_user.is_admin():
        abort(403)

    if form.validate_on_submit():
        error = None
        if form.buttons.test.data:
            error = current_app.decoder.test_notifier(notification.id)

            if error:
                flash('Error sending test notification: {0}'.format(error), 'error')
            else:
                flash('Test notification sent.', 'success')
        else:
            flash('Notification saved.', 'success')
            
        if error is None:
            return redirect(url_for('notifications.index'))

    return render_template('notifications/review.html', notification=notification, form=form, active='notifications')

@notifications.route('/messages', methods=['GET'])
@login_required
def messages():
    if not current_user.is_admin():
        abort(403)

    messages = NotificationMessage.query.all()

    return render_template('notifications/messages.html',
                            messages=messages,
                            active='notifications')

@notifications.route('/messages/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_message(id):
    if not current_user.is_admin():
        abort(403)

    message = NotificationMessage.query.filter_by(id=id).first_or_404()
    form = EditNotificationMessageForm()

    if not form.is_submitted():
        form.id.data = message.id
        form.text.data = message.text
    else:
        message.text = form.text.data

        db.session.add(message)
        db.session.commit()

        flash('The notification message has been updated.', 'success')

        return redirect(url_for('notifications.messages'))

    return render_template('notifications/edit_message.html',
                            form=form,
                            message_id=message.id,
                            active='notifications')
