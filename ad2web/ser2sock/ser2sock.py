import os

import ConfigParser
import psutil
import signal
import sh
from collections import OrderedDict
from OpenSSL import crypto

DEFAULT_SETTINGS = OrderedDict([
    ('daemonize', 1),
    ('device', ''),
    ('raw_device_mode', 1),
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
    """Exception generated when ser2sock is not found."""
    pass

class HupFailed(Exception):
    """Exception generated when ser2sock fails to be hupped."""
    pass

def read_config(path):
    """
    Reads an existing ser2sock configuration.

    :param path: Path to the configuration file.
    :type path: string
    :returns: A SafeConfigParser to operate on the configuration.
    """
    config = ConfigParser.SafeConfigParser()
    config.read(path)

    return config

def save_config(path, config_values):
    """
    Saves the ser2sock configuration.

    :param path: Path to the configuration file.
    :type path: string
    :param config_values: Configuration values to use
    :type config_values: dict
    """
    config = read_config(path)

    try:
        config.add_section('ser2sock')
    except ConfigParser.DuplicateSectionError:
        pass

    # Include default entries
    config_entries = OrderedDict(DEFAULT_SETTINGS.items() + config_values.items())

    for k, v in config_entries.iteritems():
        config.set('ser2sock', k, str(v))

    with open(path, 'w') as configfile:
        config.write(configfile)

def exists():
    """
    Determines whether or not ser2sock exists in our path.

    :returns: Whether or not ser2sock exists in the path.
    """
    return sh.which('ser2sock') is not None

def start():
    """
    Starts ser2sock
    """
    try:
        sh.ser2sock('-d', _bg=True)
    except sh.CommandNotFound, err:
        raise NotFound('Could not locate ser2sock.')

def stop():
    """
    Stops ser2sock
    """
    for proc in psutil.process_iter():
        if proc.name() == 'ser2sock':
            os.kill(proc.pid, signal.SIGKILL)

def hup():
    """
    Hups ser2sock in order to force it to reread it's configuration.
    """
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

def update_config(path, *args, **kwargs):
    """
    Updates the ser2sock configuration with new settings, saves the index
    and revocation list, and hups ser2sock.

    :param path: Path to the ser2sock configuration directory
    :type path: string
    :param args: Argument list
    :type args: list
    :param kwargs: Keyward arguments
    :type kwargs: dict
    """
    try:
        if path is not None:
            config = read_config(os.path.join(path, 'ser2sock.conf'))
        else:
            config = None

        if config is not None:
            # Pre-populate with existing settings from the config.
            config_values = {}
            if config.has_section('ser2sock'):
                for k, v in config.items('ser2sock'):
                    config_values[k] = v

            # Set any settings that were provided in our kwargs.
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

            save_config(os.path.join(path, 'ser2sock.conf'), config_values)
            hup()

    except (OSError, IOError), err:
        raise RuntimeError('Error updating ser2sock configuration: {0}'.format(err))
