# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, abort, g, request, flash, Response
from flask import current_app as APP
from flask.ext.login import login_required, current_user

from ..extensions import db
from ..decorators import admin_required
from .constants import ACTIVE, CLIENT, CA, PACKAGE_TYPE_LOOKUP, CERTIFICATE_TYPES, CERTIFICATE_STATUS
from .models import Certificate, CertificatePackage
from .forms import GenerateCertificateForm

certificate = Blueprint('certificate', __name__, url_prefix='/certificate')

@certificate.context_processor
def certificate_context_processor():
    return {
        'TYPES': CERTIFICATE_TYPES,
        'STATUS': CERTIFICATE_STATUS
    }

@login_required
@admin_required
@certificate.route('/', methods=['GET', 'POST'])
def index():
    form = GenerateCertificateForm(next=request.args.get('next'))

    if form.validate_on_submit():
        cert = Certificate()
        parent = Certificate.query.filter_by(type=CA).first()

        form.populate_obj(cert)

        cert.generate(form.name.data, parent=parent)
        cert.status = ACTIVE
        cert.type = CLIENT

        db.session.add(cert)
        db.session.commit()

        flash('Certificate created.', 'success')

    certificates = Certificate.query.all()

    return render_template('certificate/index.html', certificates=certificates, form=form, active='certificates')

@login_required
@admin_required
@certificate.route('/<int:certificate_id>')
def view(certificate_id):
    cert = Certificate.get_by_id(certificate_id)

    return render_template('certificate/view.html', certificate=cert, active='certificates')

@login_required
@admin_required
@certificate.route('/<int:certificate_id>/download/<download_type>')
def download(certificate_id, download_type):
    cert = Certificate.get_by_id(certificate_id)
    ca = Certificate.query.filter_by(type=CA).first_or_404()

    package = CertificatePackage(cert, ca)

    mime_type, filename, data = package.create(package_type=PACKAGE_TYPE_LOOKUP[download_type])

    return Response(data, mimetype=mime_type, headers={ 'Content-Type': mime_type, 'Content-Disposition': 'attachment; filename=' + filename })

@login_required
@admin_required
@certificate.route('/<int:certificate_id>/revoke')
def revoke(certificate_id):
    cert = Certificate.get_by_id(certificate_id)

    cert.revoke()

    db.session.add(cert)
    db.session.commit()

    flash('The certificate has been revoked.', 'success')

    return render_template('certificate/view.html', certificate=cert)
