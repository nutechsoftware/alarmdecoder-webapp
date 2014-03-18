# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, abort, g, request, flash, Response, redirect, url_for
from flask import current_app as APP
from flask.ext.login import login_required, current_user

from ..extensions import db
from ..decorators import admin_required
from .constants import ACTIVE, CLIENT, CA, PACKAGE_TYPE_LOOKUP, CERTIFICATE_TYPES, CERTIFICATE_STATUS
from .models import Certificate, CertificatePackage
from .forms import GenerateCertificateForm

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
    certificates = Certificate.query.all()
    ca_cert = Certificate.query.filter_by(type=CA).first()
    return render_template('certificate/index.html', certificates=certificates, ca_cert=ca_cert, active='certificates')

@certificate.route('/generate', methods=['GET', 'POST'])
@login_required
def generate():
    form = GenerateCertificateForm(next=request.args.get('next'))

    if form.validate_on_submit():
        cert = Certificate()
        parent = Certificate.query.filter_by(type=CA).first()

        form.populate_obj(cert)

        cert.generate(form.name.data, parent=parent)
        cert.status = ACTIVE
        cert.type = CLIENT
        cert.user = current_user

        db.session.add(cert)
        db.session.commit()

        flash('Certificate created.', 'success')

        return redirect(url_for('certificate.index'))

    return render_template('certificate/generate.html', form=form, active='certificates')


@certificate.route('/<int:certificate_id>')
@login_required
def view(certificate_id):
    cert = Certificate.get_by_id(certificate_id)
    if cert.user != current_user and not current_user.is_admin():
        abort(403)

    return render_template('certificate/view.html', certificate=cert, active='certificates')

@certificate.route('/<int:certificate_id>/download/<download_type>')
@login_required
def download(certificate_id, download_type):
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
    cert = Certificate.get_by_id(certificate_id)
    if cert.user != current_user and not current_user.is_admin():
        abort(403)

    cert.revoke()
    Certificate.save_certificate_index()
    Certificate.save_revocation_list()

    db.session.add(cert)
    db.session.commit()

    flash('The certificate has been revoked.', 'success')

    return render_template('certificate/view.html', certificate=cert)

@certificate.route('/generateCA')
@login_required
@admin_required
def generateCA():
    return redirect(url_for('certificate.index'))
