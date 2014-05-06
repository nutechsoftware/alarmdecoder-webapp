import os

import ConfigParser
import psutil
import signal
import sh
from collections import OrderedDict
from OpenSSL import crypto

from ..certificate.models import Certificate
from ..certificate.constants import CRL_CODE, ACTIVE, REVOKED, CA

DEFAULT_SETTINGS = OrderedDict([
    ('daemonize', 1),
    ('device', ''),
    ('baudrate', 19200),
    ('port', 10000),
    ('preserve_connections', 1),
    ('bind_ip', '0.0.0.0'),
    ('send_terminal_init', 0),
    ('device_open_delay', 5000),
    ('encrypted', '0'),
    ('ca_certificate', ''),
    ('ssl_certificate', ''),
    ('ssl_key', ''),
    ('ssl_crl', '/etc/ser2sock/ser2sock.crl'),
])

class NotFound(Exception):
    pass

class HupFailed(Exception):
    pass

def read_config(path):
    config = ConfigParser.SafeConfigParser()
    config.read(path)

    return config

def save_config(path, config_values):
    config = read_config(path)

    try:
        config.add_section('ser2sock')
    except ConfigParser.DuplicateSectionError:
        pass

    config_entries = OrderedDict(DEFAULT_SETTINGS.items() + config_values.items())

    for k, v in config_entries.iteritems():
        config.set('ser2sock', k, str(v))

    with open(path, 'w') as configfile:
        config.write(configfile)

def exists():
    return sh.which('ser2sock') is not None

def start():
    try:
        sh.ser2sock('-d', _bg=True)
    except sh.CommandNotFound, err:
        raise NotFound('Could not locate ser2sock.')

def stop():
    for proc in psutil.process_iter():
        if proc.name() == 'ser2sock':
            os.kill(proc.pid, signal.SIGKILL)

def hup():
    found = False

    for proc in psutil.process_iter():
        try:
            if proc.name() == 'ser2sock':
                found = True
                os.kill(proc.pid, signal.SIGHUP)
        except OSError, err:
            raise HupFailed('Error attempting to restart ser2sock (pid {0}): {1}'.format(proc.pid, err))

    if not found:
        start()

def save_certificate_index(path):
    path = os.path.join(path, 'certs', 'certindex')

    with open(path, 'w') as cert_index:
        for cert in Certificate.query.all():
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

def save_revocation_list(path):
    path = os.path.join(path, 'ser2sock.crl')

    ca_cert = Certificate.query.filter_by(type=CA).first()

    with open(path, 'w') as crl_file:
        crl = crypto.CRL()

        for cert in Certificate.query.all():
            if cert.type != CA:
                if cert.status == REVOKED:
                    revoked = crypto.Revoked()

                    revoked.set_reason(None)
                    # NOTE: crypto.Revoked() expects YYYY instead of YY as needed by the cert index above.
                    revoked.set_rev_date(time.strftime('%Y%m%d%H%M%SZ', cert.revoked_on.utctimetuple()))
                    revoked.set_serial(cert.serial_number)

                    crl.add_revoked(revoked)

        crl_data = crl.export(ca_cert.certificate_obj, ca_cert.key_obj)
        crl_file.write(crl_data)

def update_config(path, *args, **kwargs):
    try:
        if path is not None:
            config = read_config(os.path.join(path, 'ser2sock.conf'))
        else:
            config = None

        if config is not None:
            config_values = {}
            if config.has_section('ser2sock'):
                for k, v in config.items('ser2sock'):
                    config_values[k] = v

            if 'device_path' in kwargs.keys():
                config_values['device'] = kwargs['device_path']
            if 'device_baudrate' in kwargs.keys():
                config_values['baudrate'] = kwargs['device_baudrate']
            if 'device_port' in kwargs.keys():
                config_values['port'] = kwargs['device_port']
            if 'use_ssl' in kwargs.keys():
                config_values['encrypted'] = int(kwargs['use_ssl'])

            if 'encrypted' in config_values and config_values['encrypted'] == 1:
                cert_path = os.path.join(path, 'certs')
                if not os.path.exists(cert_path):
                    os.mkdir(cert_path, 0700)

                ca_cert = kwargs['ca_cert'] if 'ca_cert' in kwargs.keys() else None
                server_cert = kwargs['server_cert'] if 'server_cert' in kwargs.keys() else None

                if ca_cert is not None and server_cert is not None:
                    ca_cert.export(cert_path)
                    server_cert.export(cert_path)

                    config_values['ca_certificate'] = os.path.join(cert_path, '{0}.pem'.format(ca_cert.name))
                    config_values['ssl_certificate'] = os.path.join(cert_path, '{0}.pem'.format(server_cert.name))
                    config_values['ssl_key'] = os.path.join(cert_path, '{0}.key'.format(server_cert.name))

                    save_certificate_index(path)
                    save_revocation_list(path)

            save_config(os.path.join(path, 'ser2sock.conf'), config_values)
            hup()

    except (OSError, IOError), err:
        raise RuntimeError('Error updating ser2sock configuration: {0}'.format(err))
