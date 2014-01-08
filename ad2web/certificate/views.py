# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, abort, g, request, flash
from flask import current_app as APP
from flask.ext.login import login_required, current_user

from ..extensions import db
from ..decorators import admin_required
from .models import Certificate
from .forms import GenerateCertificateForm

certificate = Blueprint('certificate', __name__, url_prefix='/certificate')

@certificate.route('/', methods=['GET', 'POST'])
@login_required
@admin_required
def index():
    form = GenerateCertificateForm(next=request.args.get('next'))

    if form.validate_on_submit():
        cert = Certificate()

        cert.status = ACTIVE
        cert.type = CLIENT

        #  TEMP
        cert.serial_number = '0001'
        cert.certificate = ''
        cert.key = ''
        # /TEMP

        form.populate_obj(cert)

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
    print 'download requested', certificate_id, download_type

@certificate.route('/<int:certificate_id>/revoke')
@login_required
@admin_required
def revoke(certificate_id):
    print 'revoke requested'
