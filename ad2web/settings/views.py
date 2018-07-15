# -*- coding: utf-8 -*-

import os
import platform
import hashlib
import io
import tarfile
import json
import re
import socket
import random
try:
    import netifaces
    hasnetifaces = 1
except ImportError:
    hasnetifaces = 0
import sh
import compiler
import sys
import types
import importlib
import time

try:
    import miniupnpc
    has_upnp = True
except ImportError:
    has_upnp = False

from compiler.ast import Discard, Const
from compiler.visitor import ASTVisitor

from datetime import datetime, timedelta

from flask import Blueprint, render_template, current_app, request, flash, Response, url_for, redirect
from flask.ext.login import login_required, current_user

from sqlalchemy.orm import class_mapper
from sqlalchemy.exc import SQLAlchemyError

from alarmdecoder.panels import ADEMCO, DSC, PANEL_TYPES
from ..ser2sock import ser2sock
from ..extensions import db
from ..user import User, UserDetail
from ..utils import allowed_file, make_dir, tar_add_directory, tar_add_textfile, INSTANCE_FOLDER_PATH
from ..decorators import admin_required
from ..settings import Setting
from .forms import ProfileForm, PasswordForm, ImportSettingsForm, HostSettingsForm, EthernetSelectionForm, EthernetConfigureForm, SwitchBranchForm, EmailConfigureForm, UPNPForm, VersionCheckerForm, ExportConfigureForm
from ..setup.forms import DeviceTypeForm, LocalDeviceForm, NetworkDeviceForm
from .constants import NETWORK_DEVICE, SERIAL_DEVICE, EXPORT_MAP, HOSTS_FILE, HOSTNAME_FILE, NETWORK_FILE, KNOWN_MODULES, DAILY, IP_CHECK_SERVER_URL
from ..certificate import Certificate, CA, SERVER
from ..notifications import Notification, NotificationSetting
from ..zones import Zone
from ..upnp import UPNP
from sh import hostname, sudo
from ..exporter import Exporter

try:
    from sh import service
    hasservice = True
except ImportError:
    hasservice = False

import urllib2
import ssl

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
    operating_system = platform.system()

    if operating_system.title() != 'Linux':
        flash('Only supported on Linux systems!', 'error')
        return redirect(url_for('settings.index'))

    uptime = _get_system_uptime()
    cpu_temp = _get_cpu_temperature()

    #if missing netifaces dependency, we do not allow to view host settings
    if hasnetifaces == 1:
        hostname = socket.getfqdn()
        form = EthernetSelectionForm()

        network_interfaces = _list_network_interfaces()
        form.ethernet_devices.choices = [(i, i) for i in network_interfaces]

        if form.validate_on_submit():
            return redirect(url_for('settings.configure_ethernet_device', device=form.ethernet_devices.data))

        return render_template('settings/host.html', hostname=hostname, uptime=uptime, cpu_temp=cpu_temp, form=form, active="host settings")
    else:
        flash('Please install the netifaces module (sudo pip install netifaces) to view host settings information.', 'error')
        return redirect(url_for('settings.index'))

@settings.route('/hostname', methods=['GET', 'POST'])
@login_required
@admin_required
def hostname():
    hostname = socket.getfqdn()
    form = HostSettingsForm()

    if not form.is_submitted():
        form.hostname.data = hostname

    if form.validate_on_submit():
        new_hostname = form.hostname.data

        if os.access(HOSTS_FILE, os.W_OK):
            _sethostname(HOSTS_FILE, hostname, new_hostname)
        else:
            flash('Unable to write HOSTS FILE, check permissions', 'error')

        if os.access(HOSTNAME_FILE, os.W_OK):
            _sethostname(HOSTNAME_FILE, hostname, new_hostname)
        else:
            flash('Unable to write HOSTNAME FILE, check permissions', 'error')

        with sh.sudo:
            try:
                sh.hostname("-b", new_hostname)
            except sh.ErrorReturnCode_1:
                flash('Error setting hostname with the hostname command.', 'error')

            if hasservice:
                try:
                    sh.service("avahi-daemon", "restart")
                except sh.ErrorReturnCode_1:
                    flash('Error restarting the avahi-daemon', 'error')

        return redirect(url_for('settings.host'))

    return render_template('settings/hostname.html', hostname=hostname, form=form, active="hostname")

@settings.route('/get_ethernet_info/<string:device>', methods=['GET', 'POST'])
@login_required
@admin_required
def get_ethernet_info(device):
#get ethernet properties of passed in device
#prepare json array for XHR
    eth_properties = {}

    if hasnetifaces == 1:
        addresses = netifaces.ifaddresses(device)
        gateways = netifaces.gateways()

        eth_properties['device'] = device
        eth_properties['ipv4'] = addresses[netifaces.AF_INET]
        if netifaces.AF_INET6 in addresses.keys():
            eth_properties['ipv6'] = addresses[netifaces.AF_INET6]
        eth_properties['mac_address'] = addresses[netifaces.AF_LINK]
        eth_properties['default_gateway'] = gateways['default'][netifaces.AF_INET]

    return json.dumps(eth_properties)

@settings.route('/reboot', methods=['GET', 'POST'])
@login_required
@admin_required
def system_reboot():
    with sh.sudo:
        try:
            sh.sync()
            sh.reboot()
        except sh.ErrorReturnCode_1:
            flash('Unable to reboot device!', 'error')
            return redirect(url_for('settings.host'))
        except sh.ErrorReturnCode_143:
            pass

    flash('Rebooting device!', 'success')
    return redirect(url_for('settings.host'))

@settings.route('/shutdown', methods=['GET', 'POST'])
@login_required
@admin_required
def system_shutdown():
    with sh.sudo:
        try:
            sh.sync()
            sh.halt()
        except sh.ErrorReturnCode_1:
            flash('Unable to shutdown device!', 'error')
            return redirect(url_for('settings.host'))
        except sh.ErrorReturnCode_143:
            pass

    flash('Shutting device down!', 'success')
    return redirect(url_for('settings.host'))

@settings.route('/network/<string:device>', methods=['GET', 'POST'])
@login_required
@admin_required
def configure_ethernet_device(device):
    form = EthernetConfigureForm()
    device_map = None

    if os.access(NETWORK_FILE, os.W_OK):
        device_map = _parse_network_file()
    else:
        flash(NETWORK_FILE + ' is not writable!', 'error')
        return redirect(url_for('settings.host'))

    properties = _get_ethernet_properties(device, device_map)
    addresses = netifaces.ifaddresses(device)
    ipv4 = addresses[netifaces.AF_INET]

#first address and gateway
    ip_address = ipv4[0]['addr']
    subnet_mask = ipv4[0]['netmask']
    gateways = netifaces.gateways()
    gateway = gateways['default'][netifaces.AF_INET]
    default_gateway = gateway[0]

    if not form.is_submitted():
        form.ip_address.data = ip_address
        form.gateway.data = default_gateway
        form.netmask.data = subnet_mask

        if not properties:
            if device == 'lo' or device == 'lo0':
                flash('Unable to configure loopback device!', 'error')
                return redirect(url_for('settings.host'))

            flash('Device ' + device + ' not found in ' + NETWORK_FILE + ' you should use your OS tools to configure your network.', 'error')
            return redirect(url_for('settings.host'))
        else:
            for s in properties:
                if 'loopback' in s:
                    flash('Unable to configure loopback device!', 'error')
                    return redirect(url_for('settings.host'))
                if 'static' in s:
                    form.connection_type.data = 'static'
                if 'dhcp' in s:
                    form.connection_type.data = 'dhcp'

    if form.validate_on_submit():
        if form.connection_type.data == 'static':
            i = 0
            interface_index = 0

#find our iface definition string for "device"
            for i in range(0, len(properties)):
                if properties[i].find("dhcp") != -1 and properties[i].find(device) != -1:
                    interface_index = device_map.index(properties[i])
                    x = properties[i].replace('dhcp', 'static')
                    #replace dhcp with static, remove original add copy
                    del properties[i]
#delete our interface from the map, add it to new properties list for re-adding to map later
                    del device_map[interface_index]
                    properties.append(x)
                    break
                else:
                    if properties[i].find("static") != -1 and properties[i].find(device) != -1:
                        interface_index = device_map.index(properties[i])
                        truncated = properties[i].splitlines()
                        #truncate off address/netmask/gateway, we add after
                        del properties[i]
#if we're static but we just want to change our address
                        del device_map[interface_index]
                        properties.append(truncated[0] + "\n")
                        break

            for i in range(0, len(device_map)):
                if device_map[i].find("auto " + device) != -1:
                    del device_map[i]
                    break

            #append address values to interface string
            address = str("\taddress " + form.ip_address.data + "\n")
            netmask = str("\tnetmask " + form.netmask.data + "\n")
            gateway = str("\tgateway " + form.gateway.data + "\n")

            properties.append(address)
            properties.append(netmask)
            properties.append(gateway)

            #append new interface string with address information included
            for i in range(0, len(properties)):
                device_map.insert(interface_index + i, properties[i])

            #write the network file with the new device map
            for i in range(0, len(device_map)):
                if device_map[i].find("iface default inet dhcp") != -1:
                    x = device_map[i].replace('dhcp', 'static')
                    del device_map[i]
                    device_map.append(x)
                    break

            _write_network_file(device_map);
        else:
            for i in range(0, len(properties)):
                if properties[i].find("static") != -1 and properties[i].find(device) != -1:
                    interface_index = device_map.index(properties[i])
                    truncated = properties[0].splitlines()
                    x = truncated[0].replace('static', 'dhcp')

                    del properties
                    properties = []
                    properties.append("auto " + device + "\n" + x + "\n")

                    del device_map[interface_index]
                    for i in range(0, len(properties)):
                        device_map.insert(interface_index + i, properties[i])

            for i in range(0, len(device_map)):
                if device_map[i].find("iface default inet static") != -1:
                    x = device_map[i].replace('static', 'dhcp')
                    del device_map[i]
                    device_map.append(x)
                    break

            _write_network_file(device_map)
#substitute values in the device_map, write the file and restart networking
        with sh.sudo:
            try:
                sh.ifdown(str(device))
            except sh.ErrorReturnCode_1:
                flash('Unable to restart networking. Please try manually.', 'error')
            try:
                sh.ifup(str(device))
            except sh.ErrorReturnCode_1:
                flash('Unable to restart networking.  Please try manually.', 'error')

        form.ethernet_device.data = device

    form.ethernet_device.data = device

    return render_template('settings/configure_ethernet_device.html', form=form, device=device, active="network settings")

def _sethostname(config_file, old_hostname, new_hostname):
    #read the file and determine location where our old hostname is
    f = open(config_file, 'r')
    set_host = f.read()
    f.close()
    pointer_hostname = set_host.find(old_hostname)
    #replace old hostname with new hostname and write
    set_host = set_host.replace(old_hostname, new_hostname)
    f = open(config_file, 'w')
    f.write(set_host)
    f.close()

def _list_network_interfaces():
    interfaces = None

    if hasnetifaces == 1:
        interfaces = netifaces.interfaces()

    return interfaces

def _parse_network_file():
    text = open(NETWORK_FILE, 'r').read()
    #iface string should also contain dhcp/static address gateway netmask information according to the RE
    indexes = [s.start() for s in re.finditer('auto|iface|source|mapping|allow-|wpa-', text)]
    result = map(text.__getslice__, indexes, indexes[1:] + [len(text)])

    return result

def _write_network_file(device_map):
    text = ''
    f = open(NETWORK_FILE, 'r+')
    #go to beginning of file, rewrite ethernet device map, truncate old since we'll have a whole copy of the file in the map
    f.seek(0)

    if device_map is not None:
        for i in range(0, len(device_map)):
            text = text + device_map[i]

        f.write(text)
        f.truncate()

    f.close()

#reading the network file and tokenizing for ability to update network settings
def _get_ethernet_properties(device, device_map):
    properties = []
    if device_map is not None:
        for s in device_map:
            if device in s and s.find("auto") == -1:
                properties.append(s)

    return properties

#system uptime
def _get_system_uptime():
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
        uptime_string = str(timedelta(seconds = uptime_seconds))

    uptime_string = uptime_string[:-4]
    return uptime_string

#cpu temperature
def _get_cpu_temperature():
    if os.path.isfile('/sys/class/thermal/thermal_zone0/temp'):
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            cpu_temperature = float(f.readline())
	cpu_temperature_string = str(cpu_temperature / 1000)
        return cpu_temperature_string
    else:
        return 'not supported'

@settings.route('/configure_exports', methods=['GET', 'POST'])
@login_required
@admin_required
def configure_exports():
    form = ExportConfigureForm()

    if not form.is_submitted():
        email_server = Setting.get_by_name('system_email_server',default=None).value

        if email_server is None:
            flash('No system email configured!', 'error')
            return redirect(url_for('settings.configure_system_email'))

        form.frequency.data = Setting.get_by_name('export_frequency',default=DAILY).value
        form.email.data = Setting.get_by_name('export_email_enable',default=True).value
        form.email_address.data = Setting.get_by_name('export_mailer_to',default=None).value
        form.local_file.data = Setting.get_by_name('enable_local_file_storage',default=True).value
        form.local_file_path.data = Setting.get_by_name('export_local_path',default=os.path.join(INSTANCE_FOLDER_PATH, 'exports')).value
        if form.local_file_path.data == '':
            form.local_file_path.data = os.path.join(INSTANCE_FOLDER_PATH, 'exports')
        form.days_to_keep.data = Setting.get_by_name('days_to_keep',default=7).value

    if form.validate_on_submit():
        frequency = int(form.frequency.data)
        email_enable = form.email.data
        email_address = form.email_address.data
        local_file = form.local_file.data
        local_file_path = form.local_file_path.data
        days = form.days_to_keep.data

        to_email = Setting.get_by_name('export_mailer_to')
        to_email.value = email_address

        email = Setting.get_by_name('export_email_enable')
        email.value = email_enable

        export_frequency = Setting.get_by_name('export_frequency')
        export_frequency.value = frequency

        localfile = Setting.get_by_name('enable_local_file_storage')
        localfile.value = local_file

        localpath = Setting.get_by_name('export_local_path')
        localpath.value = local_file_path
        days_to_keep = Setting.get_by_name('days_to_keep')
        days_to_keep.value = days

        db.session.add(to_email)
        db.session.add(email)
        db.session.add(export_frequency)
        db.session.add(localfile)
        db.session.add(localpath)
        db.session.add(days_to_keep)

        db.session.commit()

        current_app.decoder._exporter_thread.prepParams()

        return redirect(url_for('settings.index'))
    return render_template('settings/configure_exports.html', form=form, active='advanced')

@settings.route('/export', methods=['GET', 'POST'])
@login_required
@admin_required
def export():
    exporter = Exporter()

    exporter.exportSettings()
    return exporter.ReturnResponse()

@settings.route('/git', methods=['GET', 'POST'] )
@login_required
@admin_required
def switch_branch():
    form = SwitchBranchForm()
    cwd = os.getcwd()

    current_branch = None
    try:
        git = sh.git.bake(_cwd=cwd)
        status = str(git.status())
        current_branch = git('rev-parse', '--abbrev-ref', 'HEAD')
    except sh.ErrorReturnCode_1:
        flash('Unable to access git command!', 'error')
        return redirect(url_for('settings.index'))

    #list all local branches
    try:
        branches = git.branch("-l")
    except sh.ErrorReturnCode_1:
        flash('Error getting list of local branches!', 'error')
        return redirect(url_for('settings.index'))

    branch_list = {}
    remote_list = {}
    err = None
    checked_out = True
    #store the sh.RunningCommand output in a dictionary, replace all special characters from git bash output
    for line in branches:
        line = line.replace("*", "")
        line = line.replace("\x1b[32m", "")
        line = line.replace("\x1b[m", "")
        line = line.replace("\n", "")
        line = line.replace(" ", "")
        line = line.replace("\x1b[31m", "")
        branch_list[line] = line


    try:
        remotes = git.remote()
        for line in remotes:
            remote_list[line] = line.replace("\n", "")
    except sh.ErrorReturnCode_1:
        flash('Error getting list of git remotes!', 'error')
        return redirect(url_for('settings.index'))

    #assign all branches to the dropdown
    form.branches.choices = [(branch_list[i], branch_list[i]) for i in branch_list]
    form.remotes.choices = [(remote_list[i], remote_list[i]) for i in remote_list]

    use_ssl = Setting.get_by_name('use_ssl', default=False).value

    if form.validate_on_submit():
        branch = form.branches.data
        remote = form.remotes.data

        try:
            git.checkout(branch)
        except sh.ErrorReturnCode_1:
            err = "You may have local changes - commit or stash them before you can switch branches."
            flash('Error switching branches! ' + err, 'error')
            checked_out = False

        if checked_out:
            try:
                git.pull(remote, branch)
            except sh.ErrorReturnCode_1:
                flash('Error pulling code from remote: ' + remote + ' branch: ' + branch, 'error')

        return redirect(url_for('settings.switch_branch'))

    return render_template('settings/git.html', form=form, ssl=use_ssl, current_branch=current_branch)

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

        kwargs['device_path'] = Setting.get_by_name('device_path', '/dev/serial0').value
        kwargs['device_baudrate'] = Setting.get_by_name('device_baudrate', 115200).value
        kwargs['device_port'] = Setting.get_by_name('device_port', 10000).value
        kwargs['use_ssl'] = Setting.get_by_name('use_ssl', False).value
        kwargs['raw_device_mode'] = Setting.get_by_name('raw_device_mode', 1).value

        if kwargs['use_ssl']:
            kwargs['ca_cert'] = Certificate.query.filter_by(type=CA).first()
            kwargs['server_cert'] = Certificate.query.filter_by(type=SERVER).first()

            Certificate.save_certificate_index()
            Certificate.save_revocation_list()

        ser2sock.update_config(config_path.value, **kwargs)
        current_app.decoder.close()
        current_app.decoder.init()

@settings.route('/diagnostics', methods=['GET', 'POST'])
@login_required
@admin_required
def system_diagnostics():
    device_settings = {}
    device_settings['address'] = current_app.decoder.device.address
    device_settings['configbits'] = hex(current_app.decoder.device.configbits).upper()
    device_settings['address_mask'] = hex(current_app.decoder.device.address_mask).upper()
    device_settings['emulate_zone'] = current_app.decoder.device.emulate_zone
    device_settings['emulate_relay'] = current_app.decoder.device.emulate_relay
    device_settings['emulate_lrr'] = current_app.decoder.device.emulate_lrr
    device_settings['deduplicate'] = current_app.decoder.device.deduplicate
    device_settings['firmware'] = current_app.decoder.device.version_number
    device_settings['serial'] = current_app.decoder.device.serial_number.upper()
    device_settings['flags'] = current_app.decoder.device.version_flags
    mode = current_app.decoder.device.mode

    device_settings['mode'] = "ADEMCO"
    if mode == DSC:
        device_settings['mode'] = "DSC"

    return render_template('settings/diagnostics.html', settings=device_settings)

@settings.route('/advanced', methods=['GET'])
@login_required
@admin_required
def advanced():
    return render_template('settings/advanced.html', active="advanced")

@settings.route('/get_imports_list', methods=['GET', 'POST'])
@login_required
@admin_required
def get_system_imports():
    imported = {}
    module_list = []
    for module in sys.modules.keys():  #get list of all modules loaded into memory
        module_name = module.split('.')[0] #everything left of a .
        if module_name.find('_') == -1:  #ignore items containing _
            if module_name not in module_list:  #unique module list
                module_list.append(module_name)

    module_list.sort()
    for val in KNOWN_MODULES:  #see if module exists in known modules, try import if does, otherwise mark not found
        found = 0
        if val in module_list:
            try:
                importlib.import_module( val )
                found = 1
            except:
                found = 0
        else:
            found = 0

        imported[val] = {'modname': val, 'found': found }

# this code block uses the .py parsing method below to try and find imports
#    for d, f in pyfiles(os.getcwd()):
#        if d.find("alembic") == -1:  #ignore the alembic directory
#            imported[d + '/' + f] = parse_python_source(os.path.join(d,f))

    return json.dumps(imported)

@settings.route('/disable_forward', methods=['GET', 'POST'])
@login_required
@admin_required
def disable_forwarding():
    if not has_upnp:
        flash(u'Missing library: miniupnpc - install using pip', 'error')
        return redirect(url_for('settings.index'))

    current_external_port = Setting.get_by_name('upnp_external_port',default=None)
    current_internal_port = Setting.get_by_name('upnp_internal_port',default=None)
    try:
        upnp = UPNP(current_app.decoder)
        if current_external_port.value is not None:
            upnp.removePortForward(current_external_port.value)
            current_internal_port.value = None
            current_external_port.value = None
            db.session.add(current_internal_port)
            db.session.add(current_external_port)
            db.session.commit()

    except Exception as ex:
        flash(u'Unable to remove port forward - {0}'.format(ex), 'error')
    else:
        flash(u'Port Forward removed successfully.', 'info')

    return redirect(url_for('settings.index'))

@settings.route('/port_forward', methods=['GET', 'POST'])
@login_required
@admin_required
def port_forwarding():
    form = UPNPForm()

    internal_ip = "alarmdecoder.local"
    external_ip = get_external_ip()

    current_internal_port = Setting.get_by_name('upnp_internal_port',default=None).value
    current_external_port = Setting.get_by_name('upnp_external_port',default=None).value
    if not has_upnp:
        flash(u'Missing library: miniupnpc - install using pip', 'error')

    if not form.is_submitted():
        form.internal_port.data = Setting.get_by_name('upnp_internal_port',default=443).value
        form.external_port.data = Setting.get_by_name('upnp_external_port',default=random.randint(1200,60000)).value

    if form.validate_on_submit():
        internal_port = Setting.get_by_name('upnp_internal_port')
        internal_port.value = int(form.internal_port.data)
        external_port = Setting.get_by_name('upnp_external_port')
        external_port.value = int(form.external_port.data)

        if has_upnp:
            try:
                upnp = UPNP(current_app.decoder)

                #remove old bindings
                if current_external_port is not None:
                    upnp.removePortForward(current_external_port)

                #add new bindings
                upnp.addPortForward(internal_port.value, external_port.value)
            except Exception as ex:
                flash(u'Error setting up port forwarding: {0}'.format(ex), 'error')
            else:
                flash(u'Port forwarding created successfully.', 'info')


        else:
            flash(u'Missing library: miniupnpc - install using pip', 'error')

        db.session.add(internal_port)
        db.session.add(external_port)
        db.session.commit()

        return redirect(url_for('settings.index'))

    return render_template('settings/port_forward.html', form=form, current_internal_port=current_internal_port, current_external_port=current_external_port, internal_ip=internal_ip, external_ip=external_ip)

def get_external_ip():
    try:
        my_ip = json.load(urllib2.urlopen(IP_CHECK_SERVER_URL, context=ssl._create_unverified_context()))['origin']
    except Exception as e:
        return None

    return my_ip

@settings.route('/configure_updater', methods=['GET', 'POST'])
@login_required
@admin_required
def configure_updater():
    form = VersionCheckerForm()
    last_check_time = float(Setting.get_by_name('version_checker_last_check_time', default=time.time()).value)

    if not form.is_submitted():
        form.version_checker_timeout.data = Setting.get_by_name('version_checker_timeout',default=600).value
        form.version_checker_disable.data = Setting.get_by_name('version_checker_disable',default=False).value

    if form.validate_on_submit():
        timeout = form.version_checker_timeout.data
        disable = form.version_checker_disable.data

        version_checker_timeout = Setting.get_by_name('version_checker_timeout')
        version_checker_timeout.value = int(timeout)

        version_checker_disable = Setting.get_by_name('version_checker_disable')
        version_checker_disable.value = disable
        current_app.decoder._version_thread.setTimeout(timeout)
        current_app.decoder._version_thread.setDisable(disable)
        db.session.add(version_checker_disable)
        db.session.add(version_checker_timeout)

        db.session.commit()

        flash('Update settings updated.', 'success')
        return redirect(url_for('settings.index'))

    last_check = datetime.fromtimestamp(last_check_time).strftime('%m-%d-%Y %H:%M:%S')
    return render_template('settings/updater_config.html', active="advanced", form=form, last_check=last_check)


@settings.route('/configure_system_email', methods=['GET', 'POST'])
@login_required
@admin_required
def configure_system_email():
    form = EmailConfigureForm()

    #populate unsubmitted form with db values if they exist
    if not form.is_submitted():
        form.mail_server.data = Setting.get_by_name('system_email_server', default='localhost').value
        form.port.data = Setting.get_by_name('system_email_port', default=25).value
        form.tls.data = Setting.get_by_name('system_email_tls', default=False).value
        form.auth_required.data = Setting.get_by_name('system_email_auth',default=False).value
        form.username.data = Setting.get_by_name('system_email_username').value
        form.password.data = Setting.get_by_name('system_email_password').value
        form.default_sender.data = Setting.get_by_name('system_email_from', default='root@alarmdecoder').value

    if form.validate_on_submit():
        email_server = form.mail_server.data
        email_port = form.port.data
        email_tls = form.tls.data
        email_username = form.username.data
        email_password = form.password.data
        email_from = form.default_sender.data
        email_auth = form.auth_required.data

        system_email_server = Setting.get_by_name('system_email_server')
        system_email_server.value = email_server
        system_email_port = Setting.get_by_name('system_email_port')
        system_email_port.value = email_port
        system_email_tls = Setting.get_by_name('system_email_tls')
        system_email_tls.value = email_tls
        system_email_username = Setting.get_by_name('system_email_username')
        system_email_username.value = email_username
        system_email_password = Setting.get_by_name('system_email_password')
        system_email_password.value = email_password
        system_email_from = Setting.get_by_name('system_email_from')
        system_email_from.value = email_from
        system_email_auth = Setting.get_by_name('system_email_auth')
        system_email_auth.value = email_auth

        db.session.add(system_email_server)
        db.session.add(system_email_port)
        db.session.add(system_email_tls)
        db.session.add(system_email_username)
        db.session.add(system_email_password)
        db.session.add(system_email_from)
        db.session.add(system_email_auth)

        db.session.commit()

        flash('System Email settings updated.', 'success')
        return redirect(url_for('settings.index'))

    return render_template('settings/system_email.html', active="advanced", form=form)

#below code used to parse .py files and find imported modules - currently does not catch things that are straight imports only froms
#leaving in case we want to improve and use
def pyfiles(startPath):
    r = []
    d = os.path.abspath(startPath)
    if os.path.exists(d) and os.path.isdir(d):
        for root, dirs, files in os.walk(d):
            for f in files:
                n, ext = os.path.splitext(f)
                if ext == '.py':
                    r.append([root, f])

    return r

class ImportVisitor(object):
        def __init__(self):
            self.modules = []
            self.recent = []
            self.exists = []

        def visitImport(self, node):
            self.accept_imports()

            mod = {}
            for x in node.names:
                mod['modname'] = x[0]
                mod['importname'] = None
                mod['viewname'] = x[1] or x[0]
                mod['lineno'] = node.lineno
                mod['level'] = 0

                exist = {'modname': x[0], 'importname': None}
                if exist not in self.exists:
                    self.recent.append(mod)
                    self.exists.append(exist)

        def visitFrom(self, node):
            self.accept_imports()
            modname = node.modname
            if modname == '__future__':
                return  #ignore!

            #module name, import name, view name, line number of script, level
            mod = {}
            for name, as_ in node.names:
                if name == '*':
                    mod['modname'] = modname
                    mod['importname'] = None
                    mod['viewname'] = None
                    mod['lineno'] = node.lineno
                    mod['level'] = node.level
                else:
                    mod['modname'] = modname
                    mod['importname'] = name
                    mod['viewname'] = as_ or name
                    mod['lineno'] = node.lineno
                    mod['level'] = node.level

                exist = {'modname': mod['modname'], 'importname': mod['importname'] }

                if exist not in self.exists:
                    self.recent.append(mod)
                    self.exists.append(exist)

        def default(self, node):
            pragma = None
            if self.recent:
                if isinstance(node, Discard):
                    children = node.getChildren()
                    if len(children) == 1 and isinstance(children[0], Const):
                        const_node = children[0]
                        pragma = const_node.value

            self.accept_imports(pragma)

        def accept_imports(self, pragma=None):
            for item in self.recent:
                self.modules.append(item)
            self.recent = []

        def finalize(self):
            self.accept_imports();
            return self.modules


class ImportWalker(ASTVisitor):
    def __init__(self, visitor):
        ASTVisitor.__init__(self)
        self._visitor = visitor

    def default( self, node, *args):
        self._visitor.default(node)
        ASTVisitor.default(self, node, *args)


def parse_python_source(fn):
    contents = open(fn, 'rU').read()
    ast = compiler.parse(contents)
    vis = ImportVisitor()

    compiler.walk(ast, vis, ImportWalker(vis))
    return vis.finalize()
