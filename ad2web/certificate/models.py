# -*- coding: utf-8 -*-

import os
import datetime
import tarfile
import io
import time
import tempfile
import subprocess

from flask import current_app

from OpenSSL import crypto, SSL
from sqlalchemy import Column, orm

from ..extensions import db
from ..settings.models import Setting
from .constants import CERTIFICATE_TYPES, CA, SERVER, CLIENT, INTERNAL, \
                        CERTIFICATE_STATUS, REVOKED, ACTIVE, \
                        PACKAGE_TYPES, TGZ, PKCS12, BKS

class Certificate(db.Model):
    __tablename__ = 'certificates'

    id = Column(db.Integer, primary_key=True, autoincrement=True)
    name = Column(db.String(32), unique=True, nullable=False)
    serial_number = Column(db.String(32), nullable=False)
    status = Column(db.SmallInteger, nullable=False)
    type = Column(db.SmallInteger, nullable=False)
    certificate = Column(db.Text, nullable=False)
    key = Column(db.Text, nullable=False)
    created_on = Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    revoked_on = Column(db.TIMESTAMP)
    description = Column(db.String(255))
    user_id = Column(db.Integer, db.ForeignKey("users.id"))

    @orm.reconstructor
    def init_on_load(self):
        try:
            self.key_obj = crypto.load_privatekey(crypto.FILETYPE_PEM, self.key)
            self.certificate_obj = crypto.load_certificate(crypto.FILETYPE_PEM, self.certificate)

        except crypto.Error, err:
            self.key_obj = None
            self.certificate_obj = None

    @classmethod
    def get_by_id(cls, user_id):
        return cls.query.filter_by(id=user_id).first_or_404()

    def revoke(self):
        self.status = REVOKED
        self.revoked_on = datetime.datetime.today()

    def generate(self, common_name, parent=None):
        cert = crypto.X509()

        cert.set_version(2)
        cert.get_subject().O = "AlarmDecoder"
        cert.get_subject().CN = common_name

        # Generate a serial number
        serial_number = 1
        if parent:
            serial_setting = Setting.get_by_name('serialnumber')
            serial_setting.value = serial_setting.value + 1

            db.session.add(serial_setting)
            db.session.commit()

            serial_number = serial_setting.value

        cert.set_serial_number(serial_number)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(20*365*24*60*60)   # 20 years.

        # Generate a key and apply it to our cert.
        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, 2048)

        cert.set_pubkey(key)

        # Set specific extensions based on whether or not we're the CA.
        if parent is None:
            cert.add_extensions((crypto.X509Extension("keyUsage", True, "keyCertSign"),))
            cert.add_extensions((crypto.X509Extension("basicConstraints", False, "CA:TRUE"),))
            cert.add_extensions((crypto.X509Extension("subjectKeyIdentifier", False, "hash", subject=cert),))               # Subject = self
            cert.add_extensions((crypto.X509Extension("authorityKeyIdentifier", False, "keyid:always", issuer=cert),))      # Authority = self

            # CA cert is self-signed.
            cert.set_issuer(cert.get_subject())
            cert.sign(key, 'sha1')

        else:
            cert.add_extensions((crypto.X509Extension("subjectKeyIdentifier", False, "hash", subject=cert),))                           # Subject = self
            cert.add_extensions((crypto.X509Extension("authorityKeyIdentifier", False, "keyid:always", issuer=parent.certificate_obj),))  # Authority = CA
            cert.add_extensions((crypto.X509Extension("basicConstraints", False, "CA:FALSE"),))

            # Client certs are signed by the CA.
            cert.set_issuer(parent.certificate_obj.get_subject())
            cert.sign(parent.key_obj, 'sha1')

        self.serial_number = serial_number
        self.certificate = crypto.dump_certificate(crypto.FILETYPE_PEM, cert)
        self.key = crypto.dump_privatekey(crypto.FILETYPE_PEM, key)

        self.certificate_obj = cert
        self.key_obj = key

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
            self._tar_add_directory(tar, self.certificate.name)

            self._tar_add_cert(tar, 'ca.pem', bytes(self.ca.certificate), parent_path=self.certificate.name)
            self._tar_add_cert(tar, self.certificate.name + '.pem', bytes(self.certificate.certificate), parent_path=self.certificate.name)
            self._tar_add_cert(tar, self.certificate.name + '.key', bytes(self.certificate.key), parent_path=self.certificate.name)

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

    def _tar_add_directory(self, tar, name):
        ti = tarfile.TarInfo(name=name)
        ti.mtime = time.time()
        ti.type = tarfile.DIRTYPE
        ti.mode = 0755
        tar.addfile(ti)

    def _tar_add_cert(self, tar, name, data, parent_path=None):
        path = name
        if parent_path:
            path = os.path.join(parent_path, name)

        ti = tarfile.TarInfo(name=path)
        ti.mtime = time.time()
        ti.size = len(data)

        tar.addfile(ti, io.TextIOWrapper(buffer=io.BytesIO(data), encoding='ascii'))
