# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, abort, g, request, flash, Response
from flask import current_app as APP
from flask.ext.login import login_required, current_user

from ..extensions import db
from ..decorators import admin_required
from .constants import ACTIVE, CLIENT, CA, PACKAGE_TYPE_LOOKUP
from .models import Certificate, CertificatePackage
from .forms import GenerateCertificateForm

certificate = Blueprint('certificate', __name__, url_prefix='/certificate')

@certificate.route('/', methods=['GET', 'POST'])
@login_required
@admin_required
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

    return render_template('certificate/index.html', certificates=certificates, form=form)

@certificate.route('/<int:certificate_id>')
@login_required
@admin_required
def view(certificate_id):
    cert = Certificate.get_by_id(certificate_id)

    return render_template('certificate/view.html', certificate=cert)

@certificate.route('/<int:certificate_id>/download/<download_type>')
@login_required
@admin_required
def download(certificate_id, download_type):
    cert = Certificate.get_by_id(certificate_id)
    ca = Certificate.query.filter_by(type=CA).first_or_404()

    package = CertificatePackage(cert, ca)

    mime_type, filename, data = package.create(package_type=PACKAGE_TYPE_LOOKUP[download_type])

    return Response(data, mimetype=mime_type, headers={ 'Content-Type': mime_type, 'Content-Disposition': 'attachment; filename=' + filename })

@certificate.route('/<int:certificate_id>/revoke')
@login_required
@admin_required
def revoke(certificate_id):
    cert = Certificate.get_by_id(certificate_id)

    cert.revoke()

    db.session.add(cert)
    db.session.commit()

    flash('The certificate has been revoked.', 'success')

    return render_template('certificate/view.html', certificate=cert)
