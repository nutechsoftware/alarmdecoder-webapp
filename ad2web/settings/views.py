# -*- coding: utf-8 -*-

import os
import hashlib
import io
import tarfile
import json

from datetime import datetime

from flask import Blueprint, render_template, current_app, request, flash, Response, url_for, redirect
from flask.ext.login import login_required, current_user

from sqlalchemy.orm import class_mapper
from sqlalchemy.exc import SQLAlchemyError

from ..ser2sock import ser2sock
from ..extensions import db
from ..user import User, UserDetail
from ..utils import allowed_file, make_dir, tar_add_directory, tar_add_textfile
from ..decorators import admin_required
from ..settings import Setting
from .forms import ProfileForm, PasswordForm, ImportSettingsForm, HostSettingsForm
from ..setup.forms import DeviceTypeForm, LocalDeviceForm, NetworkDeviceForm
from .constants import NETWORK_DEVICE, SERIAL_DEVICE, EXPORT_MAP
from ..certificate import Certificate, CA, SERVER
from ..notifications import Notification, NotificationSetting
from ..zones import Zone
import socket
import netifaces
import sh
from sh import hostname, service, sudo

settings = Blueprint('settings', __name__, url_prefix='/settings')

@settings.route('/')
@login_required
def index():
    ssl = Setting.get_by_name('use_ssl',default=False).value
    return render_template('settings/index.html', ssl=ssl, active='index')

@settings.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.filter_by(name=current_user.name).first_or_404()
    form = ProfileForm(obj=user.user_detail,
            email=current_user.email,
            role_code=current_user.role_code,
            status_code=current_user.status_code,
            next=request.args.get('next'))

    if form.validate_on_submit():

        if form.avatar_file.data:
            upload_file = request.files[form.avatar_file.name]
            if upload_file and allowed_file(upload_file.filename):
                # Don't trust any input, we use a random string as filename.
                # or use secure_filename:
                # http://flask.pocoo.org/docs/patterns/fileuploads/

                user_upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], "user_%s" % user.id)
                current_app.logger.debug(user_upload_dir)

                make_dir(user_upload_dir)
                root, ext = os.path.splitext(upload_file.filename)
                today = datetime.now().strftime('_%Y-%m-%d')
                # Hash file content as filename.
                hash_filename = hashlib.sha1(upload_file.read()).hexdigest() + "_" + today + ext
                user.avatar = hash_filename

                avatar_ab_path = os.path.join(user_upload_dir, user.avatar)
                # Reset file curso since we used read()
                upload_file.seek(0)
                upload_file.save(avatar_ab_path)

        form.populate_obj(user)
        form.populate_obj(user.user_detail)

        db.session.add(user)
        db.session.commit()

        flash('Public profile updated.', 'success')

    return render_template('settings/profile.html', user=user,
            active="profile", form=form)


@settings.route('/password', methods=['GET', 'POST'])
@login_required
def password():
    user = User.query.filter_by(name=current_user.name).first_or_404()
    form = PasswordForm(next=request.args.get('next'))

    if form.validate_on_submit():
        form.populate_obj(user)
        user.password = form.new_password.data

        db.session.add(user)
        db.session.commit()

        flash('Password updated.', 'success')

    use_ssl = Setting.get_by_name('use_ssl', default=False).value

    return render_template('settings/password.html', user=user,
            active="password", form=form, ssl=use_ssl)

@settings.route('/host', methods=['GET', 'POST'])
@login_required
@admin_required
def host():
    hostname = socket.getfqdn()
    form = HostSettingsForm()
    
    if not form.is_submitted():
        form.hostname.data = hostname

    if form.validate_on_submit():
        hosts_file = '/etc/hosts'
        hostname_file = '/etc/hostname'
        new_hostname = form.hostname.data

        _sethostname(hosts_file, hostname, new_hostname)
        _sethostname(hostname_file, hostname, new_hostname)

        sh.sudo.hostname("-b", new_hostname)

        return redirect(url_for('settings.index'))

    return render_template('settings/host.html', hostname=hostname, form=form, active="host settings")

def _sethostname(config_file, old_hostname, new_hostname):
    #read the file and determine location where our old hostname is
    f = open(config_file, 'r')
    set_host = f.read()
    f.close()
    pointer_hostname = set_host.find(old_hostname)
    #replace old hostname with new hostname and write
    set_host = set_host.replace(old_hostname, new_hostname)
    f = open(config_file, 'w')
    f.seek(pointer_hostname)
    f.write(set_host)
    f.close()

def _list_network_interfaces():
    interfaces = netifaces.interfaces()

    return interfaces

@settings.route('/export', methods=['GET', 'POST'])
@login_required
@admin_required
def export():
    prefix = 'alarmdecoder-export'
    filename = '{0}-{1}.tar.gz'.format(prefix, datetime.now().strftime('%Y%m%d%H%M%S'))
    fileobj = io.BytesIO()

    with tarfile.open(name=bytes(filename), mode='w:gz', fileobj=fileobj) as tar:
        tar_add_directory(tar, prefix)

        for export_file, model in EXPORT_MAP.iteritems():
            tar_add_textfile(tar, export_file, bytes(_export_model(model)), prefix)

    return Response(fileobj.getvalue(), mimetype='application/x-gzip', headers={ 'Content-Type': 'application/x-gzip', 'Content-Disposition': 'attachment; filename=' + filename })

def _export_model(model):
    data = []
    for res in model.query.all():
        res_dict = {}
        for c in class_mapper(res.__class__).columns:
            value = getattr(res, c.key)

            if isinstance(value, datetime):
                value = value.strftime('%Y-%m-%d %H:%M:%S.%f')

            elif isinstance(value, set):
                continue

            res_dict[c.key] = value

        data.append(res_dict)

    return json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '), skipkeys=True)

@settings.route('/import', methods=['GET', 'POST'], endpoint='import')
@login_required
@admin_required
def import_backup():
    form = ImportSettingsForm()
    form.multipart = True
    if form.validate_on_submit():
        archive_data = form.import_file.data.read()
        fileobj = io.BytesIO(archive_data)

        prefix = 'alarmdecoder-export'

        try:
            with tarfile.open(mode='r:gz', fileobj=fileobj) as tar:
                root = tar.getmember(prefix)

                for member in tar.getmembers():
                    if member.name == prefix:
                        continue
                    else:
                        filename = os.path.basename(member.name)
                        if filename in EXPORT_MAP.keys():
                            _import_model(tar, member, EXPORT_MAP[filename])

                db.session.commit()

                _import_refresh()

                current_app.logger.info('Successfully imported backup file.')
                flash('Import finished.', 'success')

                return redirect(url_for('frontend.index'))

        except (tarfile.ReadError, KeyError), err:
            current_app.logger.error('Import Error: {0}'.format(err))
            flash('Import Failed: Not a valid AlarmDecoder archive.', 'error')

        except (SQLAlchemyError, ValueError), err:
            db.session.rollback()

            current_app.logger.error('Import Error: {0}'.format(err))
            flash('Import failed: {0}'.format(err), 'error')

    use_ssl = Setting.get_by_name('use_ssl', default=False).value

    return render_template('settings/import.html', form=form, ssl=use_ssl)

def _import_model(tar, tarinfo, model):
    model.query.delete()

    filedata = tar.extractfile(tarinfo).read()
    items = json.loads(filedata)

    for itm in items:
        m = model()
        for k, v in itm.iteritems():
            if isinstance(model.__table__.columns[k].type, db.DateTime) and v is not None:
                v = datetime.strptime(v, '%Y-%m-%d %H:%M:%S.%f')

            if k == 'password' and model == User:
                setattr(m, '_password', v)
            else:
                setattr(m, k, v)

        db.session.add(m)

def _import_refresh():
    config_path = Setting.get_by_name('ser2sock_config_path')
    if config_path:
        kwargs = {}

        kwargs['device_path'] = Setting.get_by_name('device_path', '/dev/ttyAMA0').value
        kwargs['device_baudrate'] = Setting.get_by_name('device_baudrate', 115200).value
        kwargs['device_port'] = Setting.get_by_name('device_port', 10000).value
        kwargs['use_ssl'] = Setting.get_by_name('use_ssl', False).value
        if kwargs['use_ssl']:
            kwargs['ca_cert'] = Certificate.query.filter_by(type=CA).first()
            kwargs['server_cert'] = Certificate.query.filter_by(type=SERVER).first()

            Certificate.save_certificate_index()
            Certificate.save_revocation_list()

        ser2sock.update_config(config_path.value, **kwargs)
        current_app.decoder.close()
        current_app.decoder.init()
