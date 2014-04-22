# -*- coding: utf-8 -*-

import os
import datetime
import tarfile
import io
import time
import tempfile
import subprocess
import OpenSSL.crypto

from flask import current_app

from OpenSSL import crypto, SSL
from sqlalchemy import Column, orm

from ..extensions import db
from ..settings.models import Setting
from .constants import CERTIFICATE_TYPES, CA, SERVER, CLIENT, INTERNAL, \
                        CERTIFICATE_STATUS, REVOKED, ACTIVE, EXPIRED, \
                        PACKAGE_TYPES, TGZ, PKCS12, BKS, CRL_CODE
from ..utils import tar_add_directory, tar_add_textfile

class Certificate(db.Model):
    __tablename__ = 'certificates'

    id = Column(db.Integer, primary_key=True, autoincrement=True)
    name = Column(db.String(32), unique=True, nullable=False)
    serial_number = Column(db.String(32), nullable=False)
    status = Column(db.SmallInteger, nullable=False)
    type = Column(db.SmallInteger, nullable=False)
    certificate = Column(db.Text, nullable=False)
    key = Column(db.Text, nullable=True)
    created_on = Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    revoked_on = Column(db.TIMESTAMP)
    description = Column(db.String(255))
    user_id = Column(db.Integer, db.ForeignKey("users.id"))
    ca_id = Column(db.Integer)

    @orm.reconstructor
    def init_on_load(self):
        try:
            self.key_obj = crypto.load_privatekey(crypto.FILETYPE_PEM, self.key)
        except crypto.Error, err:
            self.key_obj = None

        try:
            self.certificate_obj = crypto.load_certificate(crypto.FILETYPE_PEM, self.certificate)
        except crypto.Error, err:
            self.certificate_obj = None

    @classmethod
    def get_by_id(cls, user_id):
        return cls.query.filter_by(id=user_id).first_or_404()

    @classmethod
    def save_certificate_index(cls):
        ser2sock_config_path = Setting.get_by_name('ser2sock_config_path')
        if ser2sock_config_path.value is None:
            raise ValueError('ser2sock_config_path is not set.')

        path = os.path.join(ser2sock_config_path.value, 'certs', 'certindex')

        with open(path, 'w') as cert_index:
            for cert in cls.query.all():
                if cert.type != CA:
                    revoked_time = ''
                    if cert.revoked_on:
                        revoked_time = time.strftime('%y%m%d%H%M%SZ', cert.revoked_on.utctimetuple())

                    subject = '/'.join(['='.join(t) for t in [()] + cert.certificate_obj.get_subject().get_components()])
                    cert_index.write("\t".join([
                        CRL_CODE[cert.status],
                        cert.certificate_obj.get_notAfter()[2:],    # trim off the first two characters in the year.
                        revoked_time,
                        cert.serial_number.zfill(2),
                        'unknown',
                        subject
                    ]) + "\n")

    @classmethod
    def save_revocation_list(cls):
        ser2sock_config_path = Setting.get_by_name('ser2sock_config_path')
        if ser2sock_config_path.value is None:
            raise ValueError('ser2sock_config_path is not set.')

        path = os.path.join(ser2sock_config_path.value, 'ser2sock.crl')

        ca_cert = cls.query.filter_by(type=CA).first()

        with open(path, 'w') as crl_file:
            crl = crypto.CRL()

            for cert in cls.query.all():
                if cert.type != CA:
                    if cert.status == REVOKED:
                        revoked = crypto.Revoked()

                        revoked.set_reason(None)
                        # NOTE: crypto.Revoked() expects YYYY instead of YY as needed by the cert index above.
                        revoked.set_rev_date(time.strftime('%Y%m%d%H%M%SZ', cert.revoked_on.utctimetuple()))
                        revoked.set_serial(str(cert.serial_number))

                        crl.add_revoked(revoked)

            crl_data = crl.export(ca_cert.certificate_obj, ca_cert.key_obj)
            crl_file.write(crl_data)

    def revoke(self):
        self.status = REVOKED
        self.revoked_on = datetime.datetime.today()

    def generate(self, common_name, parent=None):
        self.serial_number = self._generate_serial_number(parent)

        # Generate a key and apply it to our cert.
        key = self._create_key()
        req = self._create_request(common_name, key)
        cert = self._create_cert(req, key, self.serial_number, parent)

        self.certificate = crypto.dump_certificate(crypto.FILETYPE_PEM, cert)
        self.certificate_obj = cert

        self.key = crypto.dump_privatekey(crypto.FILETYPE_PEM, key)
        self.key_obj = key

    def _create_key(self, type=crypto.TYPE_RSA, bits=2048):
        key = crypto.PKey()
        key.generate_key(type, bits)

        return key

    def _create_request(self, common_name, key):
        req = crypto.X509Req()

        req.get_subject().O = "AlarmDecoder"
        req.get_subject().CN = common_name

        req.set_pubkey(key)
        req.sign(key, 'md5')

        return req

    def _create_cert(self, req, key, serial_number, parent=None):
        cert = crypto.X509()

        cert.set_version(2)
        cert.set_serial_number(self.serial_number)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(20*365*24*60*60)   # 20 years.
        cert.set_subject(req.get_subject())
        cert.set_pubkey(req.get_pubkey())

        # Set specific extensions based on whether or not we're the CA.
        if parent is None:
            cert.add_extensions((crypto.X509Extension("keyUsage", True, "keyCertSign, cRLSign"),))
            cert.add_extensions((crypto.X509Extension("basicConstraints", False, "CA:TRUE"),))
            cert.add_extensions((crypto.X509Extension("subjectKeyIdentifier", False, "hash", subject=cert),))               # Subject = self
            cert.add_extensions((crypto.X509Extension("authorityKeyIdentifier", False, "keyid:always", issuer=cert),))      # Authority = self

            # CA cert is self-signed.
            cert.set_issuer(req.get_subject())
            cert.sign(key, 'sha1')

        else:
            cert.add_extensions((crypto.X509Extension("subjectKeyIdentifier", False, "hash", subject=cert),))                             # Subject = self
            cert.add_extensions((crypto.X509Extension("authorityKeyIdentifier", False, "keyid:always", issuer=parent.certificate_obj),))  # Authority = CA
            cert.add_extensions((crypto.X509Extension("basicConstraints", False, "CA:FALSE"),))

            # Client certs are signed by the CA.
            cert.set_issuer(parent.certificate_obj.get_subject())
            cert.sign(parent.key_obj, 'sha1')

        return cert

    def _generate_serial_number(self, parent=None):
        if parent is None:
            return 1

        serial_setting = Setting.get_by_name('ssl_serial_number', default=1)
        serial_setting.value = serial_setting.value + 1

        db.session.add(serial_setting)
        db.session.commit()

        return serial_setting.value

    def export(self, path):
        open(os.path.join(path, '{0}.key'.format(self.name)), 'w').write(self.key)
        open(os.path.join(path, '{0}.pem'.format(self.name)), 'w').write(self.certificate)

class CertificatePackage(object):
    def __init__(self, certificate, ca):
        self.certificate = certificate
        self.ca = ca
        self.mime_type = None
        self.data = None

    def create(self, package_type=TGZ):
        if package_type == TGZ:
            mime_type = 'application/x-gzip'
            filename, data = self._create_tgz()

        elif package_type == PKCS12:
            mime_type = 'application/x-pkcs12'
            filename, data = self._create_pkcs12()

        elif package_type == BKS:
            mime_type = 'application/octet-stream'
            filename, data = self._create_bks()

        else:
            raise ValueError('Invalid package type')

        self.mime_type = mime_type
        self.filename = filename
        self.data = data

        return mime_type, filename, data

    def _create_tgz(self):
        filename = self.certificate.name + '.tar.gz'
        fileobj = io.BytesIO()

        with tarfile.open(name=bytes(filename), mode='w:gz', fileobj=fileobj) as tar:
            tar_add_directory(tar, self.certificate.name)

            tar_add_textfile(tar, 'ca.pem', bytes(self.ca.certificate), parent_path=self.certificate.name)
            tar_add_textfile(tar, self.certificate.name + '.pem', bytes(self.certificate.certificate), parent_path=self.certificate.name)
            tar_add_textfile(tar, self.certificate.name + '.key', bytes(self.certificate.key), parent_path=self.certificate.name)

        return filename, fileobj.getvalue()

    def _create_pkcs12(self, password='', export=True):
        filename = self.certificate.name + '.p12'
        p12cert = crypto.PKCS12()

        p12cert.set_ca_certificates((self.ca.certificate_obj,))
        p12cert.set_certificate(self.certificate.certificate_obj)
        p12cert.set_privatekey(self.certificate.key_obj)
        p12cert.set_friendlyname(bytes(self.certificate.name))

        if export:
            data = p12cert.export(passphrase=password)
        else:
            data = p12cert

        return filename, data

    def _create_bks(self, password=''):
        # FIXME
        bouncycastle_path = 'bcprov-jdk15on-146.jar'

        # Create our base PKCS12 cert
        filename, p12cert = self._create_pkcs12(export=False)
        filename = self.certificate.name + '.bks'

        # Create temporary files.
        with tempfile.NamedTemporaryFile(delete=False) as p12file:
            p12file.write(p12cert.export(passphrase=''))    # NOTE: Passphrase must be specified so that the pkcs12 can be used by Mono.

        with tempfile.NamedTemporaryFile(delete=False) as cafile:
            cafile.write(self.ca.certificate)

        with tempfile.NamedTemporaryFile() as output:       # HACK: mktemp is deprecated.. I guess this works.
            pass

        # Import PKCS12 cert into keystore
        subprocess.Popen(["keytool", "-importkeystore", "-destkeystore", output.name, "-srckeystore", p12file.name,
                            "-srcstoretype", "PKCS12", "-alias", self.certificate.name, "-storetype", "BKS", "-provider", "org.bouncycastle.jce.provider.BouncyCastleProvider",
                            "-providerpath", bouncycastle_path, "-srcstorepass", '', "-deststorepass", "alarmdecoder", "-noprompt"],      # TODO: Remove temporary password.
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE).communicate()

        # Import CA as trusted
        subprocess.Popen(["keytool", "-import", "-trustcacerts", "-alias", "CA", "-file", cafile.name, "-keystore",
                            output.name, "-storetype", "BKS", "-providerclass", "org.bouncycastle.jce.provider.BouncyCastleProvider",
                            "-providerpath", bouncycastle_path, "-storepass", "alarmdecoder", "-trustcacerts", "-noprompt"],              # TODO: Remove temporary password.
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE).communicate()

        # Retrieve BKS data
        data = None
        with open(output.name, 'rb') as bksfile:
            data = bksfile.read()

        # Remove temporary files.
        os.unlink(p12file.name)
        os.unlink(cafile.name)
        os.unlink(output.name)

        return filename, data
