from flask import Blueprint, render_template, current_app, request, flash, redirect, url_for, abort
from flask.ext.login import login_required, current_user

from wtforms import FormField

from ..extensions import db
from ..decorators import admin_required
from ..settings import Setting
from .forms import (CreateNotificationForm, EditNotificationForm, EmailNotificationForm, GoogleTalkNotificationForm, CreateCustomNotificationForm,
                     PowerChangedNotificationForm, AlarmNotificationForm, BypassNotificationForm, ArmNotificationForm, DisarmNotificationForm,
                     ZoneFaultNotificationForm, ZoneRestoreNotificationForm, FireNotificationForm, PanicNotificationForm, LRRNotificationForm,
                     EXPNotificationForm, RELNotificationForm, RFXNotificationForm, AUINotificationForm, KPENotificationForm)

from .models import Notification, NotificationSetting, CustomNotification, CustomNotificationSetting

from .constants import (NOTIFICATION_TYPES, EMAIL, GOOGLETALK, CUSTOM_NOTIFICATION_EVENTS_TYPES, CUSTOM_NOTIFICATION_EVENTS,
                     LRR_EVENTS_TYPES, LRR_EVENTS, ALARM_EXIT_ERROR, TROUBLE, BYPASS, ACLOSS, LOWBAT, TEST_CALL, OPEN, ARM_AWAY,
                     RFLOWBAT, CANCEL, RESTORE, TROUBLE_RESTORE, BYPASS_RESTORE, AC_RESTORE, LOWBAT_RESTORE, RFLOWBAT_RESTORE, TEST_RESTORE,
                     ALARM_PANIC, ALARM_FIRE, ALARM_ENTRY, ALARM_AUX, ALARM_AUDIBLE, ALARM_SILENT, ALARM_PERIMETER, POWER_CHANGED, ALARM,
                     BYPASS, ARM, DISARM, ZONE_FAULT, ZONE_RESTORE, FIRE, PANIC, LRR, EXP, REL, RFX, AUI, KPE)

NOTIFICATION_TYPE_DETAILS = {
    'email': (EMAIL, EmailNotificationForm),
    'googletalk': (GOOGLETALK, GoogleTalkNotificationForm),
}

CUSTOM_NOTIFICATION_EVENTS_DETAILS = {
    'powerchanged': (POWER_CHANGED, PowerChangedNotificationForm),
    'alarm': (ALARM, AlarmNotificationForm),
    'bypass': (BYPASS, BypassNotificationForm),
    'arm': (ARM, ArmNotificationForm),
    'disarm': (DISARM, DisarmNotificationForm),
    'zonefault': (ZONE_FAULT, ZoneFaultNotificationForm),
    'zonerestore': (ZONE_RESTORE, ZoneRestoreNotificationForm),
    'fire': (FIRE, FireNotificationForm),
    'panic': (PANIC, PanicNotificationForm),
    'lrrmessage': (LRR, LRRNotificationForm),
    'expmessage': (EXP, EXPNotificationForm),
    'relmessage': (REL, RELNotificationForm),
    'rfxmessage': (RFX, RFXNotificationForm),
    'auimessage': (AUI, AUINotificationForm),
    'keypressevent': (KPE, KPENotificationForm),
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
    use_ssl = Setting.get_by_name('use_ssl', default=False).value
    notification_list = Notification.query.all()

    return render_template('notifications/index.html', notifications=notification_list, active='notifications', ssl=use_ssl)

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

    use_ssl = Setting.get_by_name('use_ssl', default=False).value

    return render_template('notifications/edit.html', form=form, id=id, notification=notification, active='notifications', ssl=use_ssl)

@notifications.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = CreateNotificationForm()

    if form.validate_on_submit():
        return redirect(url_for('notifications.create_by_type', type=form.type.data))

    use_ssl = Setting.get_by_name('use_ssl', default=False).value

    return render_template('notifications/create.html', form=form, active='notifications', ssl=use_ssl)

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

    use_ssl = Setting.get_by_name('use_ssl', default=False).value

    return render_template('notifications/create_by_type.html', form=form, type=type, active='notifications', ssl=use_ssl)

@notifications.route('/remove/<int:id>', methods=['GET', 'POST'])
@login_required
def remove(id):
    notification = Notification.query.filter_by(id=id).first_or_404()
    if notification.user != current_user and not current_user.is_admin():
        abort(403)

    db.session.delete(notification)
    db.session.commit()

    flash('Notification deleted.', 'success')
    return redirect(url_for('notifications.index'))

@notifications.route('/custom/create', methods=['GET', 'POST'])
@login_required
def create_custom():
    form = CreateCustomNotificationForm()

    if form.validate_on_submit():
        return redirect(url_for('notifications.create_custom_by_event', notification_event=form.notification_event.data))

    use_ssl = Setting.get_by_name('use_ssl', default=False).value

    return render_template('notifications/custom.html', form=form, active='notifications', ssl=use_ssl)


@notifications.route('/custom', methods=['GET', 'POST'])
@login_required
def custom_index():
    notification_list = CustomNotification.query.all()
    return render_template('notifications/custom_index.html', notification_list=notification_list)

@notifications.route('/custom/create/<string:notification_event>', methods=['GET', 'POST'])
@login_required
def create_custom_by_event(notification_event):
    if notification_event not in CUSTOM_NOTIFICATION_EVENTS_DETAILS.keys():
        abort(404)

    notification_event_id, form_type = CUSTOM_NOTIFICATION_EVENTS_DETAILS[notification_event]
    form = form_type()
    form.notification_event = notification_event_id

    if form.validate_on_submit():
        obj = CustomNotification()

        form.populate_obj(obj)
        obj.user = current_user
        form.populate_settings(obj.settings)

        db.session.add(obj)
        db.session.commit()

        flash('Custom Notification created.', 'success')

        return redirect(url_for('notifications.custom_index'))

    use_ssl = Setting.get_by_name('use_ssl', default=False).value

    return render_template('notifications/create_by_event.html', form=form, notification_event=notification_event, active='custom_notifications', ssl=use_ssl)
