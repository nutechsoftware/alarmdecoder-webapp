#!/bin/bash

# arguments: $RELEASE $LINUXFAMILY $BOARD $BUILD_DESKTOP
#
# This is the image customization script

# NOTE: It is copied to /tmp directory inside the image
# and executed inside a chroot environment
# so don't reference any files that are not already installed

# NOTE: If you want to transfer files between chroot and host
# userpatches/overlay directory on host is bind-mounted to /tmp/overlay in chroot
LPREFIX="**** AD2 ****"
RELEASE=$1
LINUXFAMILY=$2
BOARD=$3
BUILD_DESKTOP=$4
#
# settings
WEBAPP_BRANCH="nocache"

# Start processing
echo "Installing AlarmDecoder appliance on Release: $1 Family: $2 Board: $3 Desktop: $4"
# Add ad2 user
echo "$LPREFIX adding user ad2"
adduser --quiet --disabled-password --gecos "" ad2
# add user to dialout group for access to serial ports
echo "$LPREFIX add ad2 user to dialout group"
usermod -a -G dialout ad2
# change permissions of hosts and hostname so webapp can change it
echo "$LPREFIX change permissions on /etc/hostname and /etc/hosts"
chgrp dialout /etc/hosts /etc/hostname
chmod g+w /etc/hosts /etc/hostname
# Update pip and setuptools
echo "$LPREFIX update pip and setup tools"
pip install --upgrade pip
pip install --upgrade setuptools
# No package for flask_mail and missing from requirements.txt Should be deprecated as the module is deprecated.
echo "$LPREFIX Fix missing flask_mail. TODO deprecate usage of flask_mail."
pip install flask_mail
# TODO investigate these were missing also
echo "$LPREFIX Add missing flask packages using pip."
pip install Flask-Caching
pip install flask_login
pip install miniupnpc
pip install chump
#pip install pyftdi # failed missing for python 2
# create app folders and set permissions
echo "$LPREFIX create webapp and api folders"
mkdir -p /opt/alarmdecoder
mkdir -p /opt/alarmdecoder-webapp
echo "$LPREFIX set app folder permissions"
chown ad2:ad2 /opt/alarmdecoder
chown ad2:ad2 /opt/alarmdecoder-webapp
# git clone alarmdecoder python library
echo "$LPREFIX fetch alarmdecoder api from github"
su -c "cd /opt && git clone https://github.com/nutechsoftware/alarmdecoder.git" ad2
# add alarmdecoder api to python path
export PYTHONPATH="${PYTHONPATH}:/opt/alarmdecoder"
# git clone alarmdecoder-webapp
echo "$LPREFIX fetch alarmdecoder webapp from github"
su -c "cd /opt/ && git clone https://github.com/nutechsoftware/alarmdecoder-webapp.git" ad2
# add requirements if not already satisfied
echo "$LPREFIX checking out webapp branch $WEBAPP_BRANCH"
su -c "cd /opt/alarmdecoder-webapp/ && git checkout $WEBAPP_BRANCH" ad2
echo "$LPREFIX install webapp python requirements if not already satisfied"
su -c "cd /opt/alarmdecoder-webapp/ && pip install -r requirements.txt" ad2
# git clone ser2sock
echo "$LPREFIX fetch ser2sock from github"
cd /opt/ && git clone https://github.com/nutechsoftware/ser2sock.git
# build and install and configure ser2sock
echo "$LPREFIX build ser2sock"
cd /opt/ser2sock/ && ./configure && make && cp ./ser2sock /usr/local/bin/
echo "$LPREFIX install ser2sock"
mkdir -p /etc/ser2sock
cp /opt/ser2sock/etc/ser2sock/ser2sock.conf /etc/ser2sock/
sed -i 's/EXTRA_START_ARGS=/#EXTRA_START_ARGS=/g' /etc/init.d/ser2sock
sed -i 's/##EXTRA_START_ARGS=/EXTRA_START_ARGS=/g' /etc/init.d/ser2sock
sed -i 's/#RUN_AS=.*/RUN_AS=ad2:ad2/g' /etc/init.d/ser2sock
sed -i 's/raw_device_mode = 0/raw_device_mode = 1/g' /etc/ser2sock/ser2sock.conf
sed -i 's/device = \/dev\/ttyAMA0/device = \/dev\/serial0/g' /etc/ser2sock/ser2sock.conf
cp /opt/ser2sock/init/ser2sock /etc/init.d/
update-rc.d ser2sock defaults
chown -R ad2:ad2 /etc/ser2sock

# force /dev/ttyS1 to be /dev/serial0 our expected device name.
cat << EOF > /etc/udev/rules.d/alarmdecoder.rules
SUBSYSTEM=="tty" KERNEL=="ttyS1", SYMLINK+="serial0"
EOF

# configure avahi services
cat << EOF > /etc/avahi/services/alarmdecoder.service
<?xml version="1.0" standalone="no"?>
<!DOCTYPE service-group SYSTEM "avahi-service.dtd">
<service-group>
	<name replace-wildcards="yes">%h</name>
	<service>
		<type>_device-info._tcp</type>
		<port>0</port>
		<txt-record>model=AlarmDecoder</txt-record>
	</service>
	<service>
		<type>_ssh._tcp</type>
		<port>22</port>
	</service>
</service-group>
EOF

# build ssl keys for web app
echo "$LPREFIX FIXME: build nginx ssl keys"
mkdir -p /etc/nginx/ssl
# remove sample page prep html folder for webapp
echo "$LPREFIX remove sample html"
rm -r /var/www/html/
# create gunicorn service config and enable it
cat << EOF > /etc/systemd/user/gunicorn.service
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
PIDFile=/run/gunicorn/pid\nUser=pi
Group=dialout
WorkingDirectory=/opt/alarmdecoder-webapp
Environment="TERM=vt100"
ExecStart=/usr/bin/gunicorn --worker-class=socketio.sgunicorn.GeventSocketIOWorker --timeout=120 --env=POLICY_SERVER=0 --log-level=debug wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID\nExecStop=/bin/kill -s TERM $MAINPID
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF
ln -s /etc/systemd/user/gunicorn.service /etc/systemd/system/multi-user.target.wants/gunicorn.service
ln -s /etc/systemd/user/gunicorn.service /etc/systemd/system/gunicorn.service

cat << EOF > /etc/logrotate.d/alarmdecoder
/opt/alarmdecoder-webapp/instance/logs/*.log {
weekly
missingok
rotate 5
compress
delaycompress
notifempty
create 0640 ad2 ad2
sharedscripts
}
EOF

cat << EOF > /etc/logrotate.d/gunicorn
/var/log/gunicorn/*.log {
weekly
missingok
rotate 5
compress
delaycompress
notifempty
create 0640 www-data www-data
sharedscripts
postrotate
[ -s /run/gunicorn/alarmdecoder.pid ] && kill -USR1 `cat /run/gunicorn/alarmdecoder.pid`
endscript
}
EOF

mkdir -p /etc/gunicorn.d/
cp /opt/alarmdecoder-webapp/contrib/gunicorn.d/alarmdecoder /etc/gunicorn.d/
cp /opt/alarmdecoder-webapp/contrib/nginx/nginx.service /lib/systemd/system/nginx.service
cp /opt/alarmdecoder-webapp/contrib/nginx/alarmdecoder /etc/nginx/sites-available/
ln -s /etc/nginx/sites-available/alarmdecoder /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default
su -c "cd /opt/alarmdecoder-webapp/ && python manage.py initdb" ad2
#FIXME build keys etc
echo "$LPREFIX FIXME: build keys and stuff on first boot"
touch /boot/newkeys.txt

# Create /etc/systemd/user/alarmdecoder-earlyboot.service
cat << EOF > /etc/systemd/system/alarmdecoder-earlyboot.service
[Unit]
Description=AlarmDecoder WebApp generate unique keys
#DefaultDependencies=false
#Requires=sysinit.target
#After=sysinit.target
#Requires=network.target
#After=network.target
#Before=remount-sysroot.service

[Install]
WantedBy=multi-user.target

[Service]
Type=oneshot
RemainAfterExit=true
ExecStart=/usr/local/bin/alarmdecoder-earlyboot.sh
StandardOutput=journal
EOF

# Create /usr/local/bin/alarmdecoder-earlyboot.sh
cat << EOF > /usr/local/bin/alarmdecoder-earlyboot.sh
#!/bin/bash
if [ -e /boot/newkeys.txt ]; then 
/bin/rm -r /etc/mail/tls/sendmail-*
/bin/rm -v usr/share/sendmail/update_tls
/bin/rm -v /etc/ssh/ssh_host_*
# FIXME: did not create new keys?
dpkg-reconfigure openssh-server 
/bin/rm /boot/newkeys.txt
openssl req -x509 -nodes -sha256 -days 3650 -newkey rsa:4096 -keyout /etc/nginx/ssl/alarmdecoder.key -out /etc/nginx/ssl/alarmdecoder.crt -subj '/CN=AlarmDecoder.local/O=AlarmDecoder.com/C=US' -reqexts SAN -extensions SAN -config <(cat /etc/ssl/openssl.cnf  <(printf "\n[SAN]\nsubjectAltName=DNS:alarmdecoder,DNS:alarmdecoder.local"))
fi
EOF
chmod +x /usr/local/bin/alarmdecoder-earlyboot.sh
systemctl enable alarmdecoder-earlyboot

echo "$LPREFIX finished"

