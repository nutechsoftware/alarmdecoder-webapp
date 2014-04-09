# -*- coding: utf-8 -*-
import os

from flask import Blueprint, render_template, abort, g, request, flash, Response, redirect, url_for
from flask import current_app as APP
from flask.ext.login import login_required, current_user

from ..extensions import db
from ..decorators import admin_required
from .constants import ACTIVE, CLIENT, CA, PACKAGE_TYPE_LOOKUP, CERTIFICATE_TYPES, CERTIFICATE_STATUS, SERVER, INTERNAL, REVOKED
from .models import Certificate, CertificatePackage
from .forms import GenerateCertificateForm
from ..settings.models import Setting
from ..ser2sock import ser2sock

certificate = Blueprint('certificate', __name__, url_prefix='/settings/certificates')

@certificate.context_processor
def certificate_context_processor():
    return {
        'TYPES': CERTIFICATE_TYPES,
        'STATUS': CERTIFICATE_STATUS
    }

@certificate.route('/', methods=['GET', 'POST'])
@login_required
def index():
    use_ssl = Setting.get_by_name('use_ssl', default=False).value
    if use_ssl == False:
        abort(404)

    certificates = Certificate.query.all()
    ca_cert = Certificate.query.filter_by(type=CA).first()

    return render_template('certificate/index.html', certificates=certificates, ca_cert=ca_cert, active='certificates', ssl=use_ssl)

@certificate.route('/generate', methods=['GET', 'POST'])
@login_required
def generate():
    use_ssl = Setting.get_by_name('use_ssl', default=False).value
    if use_ssl == False:
        abort(404)

    form = GenerateCertificateForm(next=request.args.get('next'))

    if form.validate_on_submit():
        cert = Certificate()
        parent = Certificate.query.filter_by(type=CA).first()

        form.populate_obj(cert)

        cert.generate(form.name.data, parent=parent)
        cert.status = ACTIVE
        cert.type = CLIENT
        cert.user = current_user

        if parent is not None:
            cert.ca_id = parent.id

        db.session.add(cert)
        db.session.commit()

        flash('Certificate created.', 'success')

        return redirect(url_for('certificate.index'))

    return render_template('certificate/generate.html', form=form, active='certificates', ssl=use_ssl)


@certificate.route('/<int:certificate_id>')
@login_required
def view(certificate_id):
    use_ssl = Setting.get_by_name('use_ssl', default=False).value
    if use_ssl == False:
        abort(404)

    cert = Certificate.get_by_id(certificate_id)

    if cert.type != CLIENT and not current_user.is_admin():
        abort(403)

    ca_cert = Certificate.query.filter_by(type=CA).first()
    if cert.user != current_user and not current_user.is_admin():
        abort(403)

    return render_template('certificate/view.html', certificate=cert, ca_cert=ca_cert, current_user=current_user, active='certificates', ssl=use_ssl)

@certificate.route('/<int:certificate_id>/download/<download_type>')
@login_required
def download(certificate_id, download_type):
    use_ssl = Setting.get_by_name('use_ssl', default=False).value
    if use_ssl == False:
        abort(404)

    cert = Certificate.get_by_id(certificate_id)
    if cert.user != current_user and not current_user.is_admin():
        abort(403)

    ca = Certificate.query.filter_by(type=CA).first_or_404()
    package = CertificatePackage(cert, ca)

    mime_type, filename, data = package.create(package_type=PACKAGE_TYPE_LOOKUP[download_type])

    return Response(data, mimetype=mime_type, headers={ 'Content-Type': mime_type, 'Content-Disposition': 'attachment; filename=' + filename })

@certificate.route('/<int:certificate_id>/revoke')
@login_required
def revoke(certificate_id):
    use_ssl = Setting.get_by_name('use_ssl', default=False).value
    if use_ssl == False:
        abort(404)

    cert = Certificate.get_by_id(certificate_id)
    if cert.user != current_user and not current_user.is_admin():
        abort(403)

    cert.revoke()
    Certificate.save_certificate_index()
    Certificate.save_revocation_list()

    db.session.add(cert)
    db.session.commit()

    flash('The certificate has been revoked.', 'success')

    return render_template('certificate/view.html', certificate=cert, ssl=use_ssl)

@certificate.route('/generateCA')
@login_required
@admin_required
def generateCA():
    use_ssl = Setting.get_by_name('use_ssl', default=False).value
    if use_ssl == False:
        abort(404)

    ca_cert = Certificate(
                name="AlarmDecoder CA",
                description='CA certificate used for authenticating others.',
                status=ACTIVE,
                type=CA)
    ca_cert.generate(common_name='AlarmDecoder CA')
    db.session.add(ca_cert)
    db.session.commit()

    server_cert = Certificate(
                name="AlarmDecoder Server",
                description='Server certificate used by ser2sock.',
                status=ACTIVE,
                type=SERVER,
                ca_id=ca_cert.id)
    server_cert.generate(common_name='AlarmDecoder Server', parent=ca_cert)
    db.session.add(server_cert)
    
    internal_cert = Certificate(
                name="AlarmDecoder Internal",
                description='Internal certificate used to communicate with ser2sock.',
                status=ACTIVE,
                type=INTERNAL,
                ca_id=ca_cert.id)
    internal_cert.generate(common_name='AlarmDecoder Internal', parent=ca_cert)
    db.session.add(internal_cert)

    config_path = Setting.get_by_name('ser2sock_config_path')
    if config_path is not None:
        _update_ser2sock_config(config_path.value)
    db.session.commit()

    return redirect(url_for('certificate.index'), ssl=use_ssl)

def _update_ser2sock_config(path):
    if path is not None:
        config = ser2sock.read_config(os.path.join(path, 'ser2sock.conf'))
    else:
        config = None

    if config is not None:
        config_values = {}
        for k, v in config.items('ser2sock'):
            config_values[k] = v

        config_values['device'] = Setting.get_by_name('device_path').value
        config_values['baudrate'] = Setting.get_by_name('device_baudrate').value
        config_values['port'] = Setting.get_by_name('device_port').value
        config_values['encrypted'] = Setting.get_by_name('use_ssl').value
        if config_values['encrypted'] == 1:
            ca = Certificate.query.filter_by(type=CA).first()
            server_cert = Certificate.query.filter_by(type=SERVER).first()

            if ca is not None and server_cert is not None:
                ca.export(os.path.join(path, 'certs'))
                server_cert.export(os.path.join(path, 'certs'))

                config_values['ca_certificate'] = os.path.join(path, 'certs', '{0}.pem'.format(ca.name))
                config_values['ssl_certificate'] = os.path.join(path, 'certs', '{0}.pem'.format(server_cert.name))
                config_values['ssl_key'] = os.path.join(path, 'certs', '{0}.key'.format(server_cert.name))

                ser2sock.save_certificate_index(path)
                ser2sock.save_revocation_list(path)

        ser2sock.save_config(os.path.join(path, 'ser2sock.conf'), config_values)
        ser2sock.hup()

@certificate.route('/revokeCA')
@login_required
@admin_required
def revokeCA():
    use_ssl = Setting.get_by_name('use_ssl', default=False).value
    if use_ssl == False:
        abort(404)

    ca = Certificate.query.filter_by(type=CA).first()
    certs = Certificate.query.filter_by(ca_id=ca.id).delete()
    ca = Certificate.query.filter_by(type=CA).delete()
    db.session.commit()

    return redirect(url_for('certificate.index'), ssl=use_ssl)
