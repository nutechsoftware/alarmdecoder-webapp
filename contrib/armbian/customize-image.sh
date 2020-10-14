#!/bin/bash

# arguments: $RELEASE $LINUXFAMILY $BOARD $BUILD_DESKTOP
#
# This is the image customization script

# NOTE: It is copied to /tmp directory inside the image
# and executed inside a chroot environment
# so don't reference any files that are not already installed

# NOTE: If you want to transfer files between chroot and host
# userpatches/overlay directory on host is bind-mounted to /tmp/overlay in chroot
LPREFIX="**** AD2 **** "
RELEASE=$1
LINUXFAMILY=$2
BOARD=$3
BUILD_DESKTOP=$4

#
# settings
## AlarmDecoder webapp github branch
WEBAPP_BRANCH="master"

# Start processing
echo "Installing AlarmDecoder appliance on Armbian Release: $1 Family: $2 Board: $3 Desktop: $4"

# Add ad2 user
echo "$LPREFIX Adding user 'ad2' with a default password of 'alarmdecoder'"
adduser --quiet --disabled-password ad2
echo "$LPREFIX Setting default ad2 user password"
echo -e "alarmdecoder\nalarmdecoder" | (passwd ad2)
echo "$LPREFIX Adding user 'ad2' to sudo group"
usermod -aG sudo ad2
echo "$LPREFIX add ad2 user to dialout group"
usermod -a -G dialout ad2
echo "$LPREFIX TODO: force password change on next login for user 'ad2'"

# Disable create new user prompt in Armbian
echo "$LPREFIX Disable default Armbian new user prompt"
rm -f /root/.not_logged_in_yet

# remove password from root prevent direct login unless user changes password.
echo "$LPREFIX FIXME: no login for root unless password set"
sudo passwd -d root

# Change permissions of hosts and hostname so webapp can change it
echo "$LPREFIX change permissions on /etc/hostname and /etc/hosts"
chgrp dialout /etc/hosts /etc/hostname
chmod g+w /etc/hosts /etc/hostname

# Update pip and setuptools
echo "$LPREFIX update pip and setup tools"
pip install --upgrade pip
pip install --upgrade setuptools

# No package for flask_mail and missing from requirements.txt Should be deprecated as the module is deprecated.
echo "$LPREFIX Fix missing flask_mail. TODO deprecate usage of flask_mail"
pip install flask_mail

# TODO investigate these were missing also
echo "$LPREFIX Add missing flask packages using pip"
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

# Clone alarmdecoder python library from github
echo "$LPREFIX fetch alarmdecoder api from github"
su -c "cd /opt && git clone https://github.com/nutechsoftware/alarmdecoder.git" ad2

# Clone alarmdecoder-webapp from github
echo "$LPREFIX fetch alarmdecoder webapp from github"
su -c "cd /opt/ && git clone https://github.com/nutechsoftware/alarmdecoder-webapp.git" ad2

# Add requirements if not already satisfied
echo "$LPREFIX checking out webapp branch $WEBAPP_BRANCH"
su -c "cd /opt/alarmdecoder-webapp/ && git checkout $WEBAPP_BRANCH" ad2
echo "$LPREFIX install webapp python requirements if not already satisfied"
cd /opt/alarmdecoder-webapp/ && pip install -r requirements.txt

# FIXME: temp fix for issues with flask and  werkzeug
echo "$LPREFIX FIXME upgrading flask and werkzeug."
pip install --upgrade Flask
pip install --upgrade werkzeug==0.16.1

# Clone ser2sock from github
echo "$LPREFIX fetch ser2sock from github"
cd /opt/ && git clone https://github.com/nutechsoftware/ser2sock.git

# Build and install and configure ser2sock
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

# Force /dev/ttyS1 to be /dev/serial0 our expected device name.
cat << EOF > /etc/udev/rules.d/alarmdecoder.rules
SUBSYSTEM=="tty" KERNEL=="ttyS1", SYMLINK+="serial0"
EOF

# Configure avahi services
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

# Build ssl keys for web app
echo "$LPREFIX FIXME: build nginx ssl keys"
mkdir -p /etc/nginx/ssl

# Remove sample page prep html folder for webapp
echo "$LPREFIX remove sample html"
rm -r /var/www/html/

# Create gunicorn service config and enable it
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

# Enable log rotation for webapp
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

# Enable log rotation for gunicorn
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

# Enable gunicorn and nginx services
mkdir -p /etc/gunicorn.d/
cp /opt/alarmdecoder-webapp/contrib/gunicorn.d/alarmdecoder /etc/gunicorn.d/
cp /opt/alarmdecoder-webapp/contrib/nginx/nginx.service /lib/systemd/system/nginx.service

# Enable nginx site
cp /opt/alarmdecoder-webapp/contrib/nginx/alarmdecoder /etc/nginx/sites-available/
ln -s /etc/nginx/sites-available/alarmdecoder /etc/nginx/sites-enabled/

# Remove sample html
rm /etc/nginx/sites-enabled/default

# Initialize the webapp databasee
su -c "cd /opt/alarmdecoder-webapp/ && PYTHONPATH=${PYTHONPATH}:/opt/alarmdecocer python manage.py initdb" ad2

# Force new keys on first boot
echo "$LPREFIX enabling build keys and stuff on first boot"
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
if [[ -f /boot/newkeys.txt ]]; then
  ## SSH server keys
   echo "$LPREFIX Building new personal keys for SSH"
   /bin/rm -v /etc/ssh/ssh_host_*
   /usr/sbin/dpkg-reconfigure openssh-server
  ## sendmail keys
   ### /etc/mail/tls/is emtpy already auto build on first boot.
   #/bin/rm -r /etc/mail/tls/sendmail-....
  ## Build keys for nginx
   echo "$LPREFIX Building new personal keys for HTTPS with nginx"
   /usr/bin/openssl req -x509 -nodes -sha256 -days 3650 -newkey rsa:4096 -keyout /etc/nginx/ssl/alarmdecoder.key -out /etc/nginx/ssl/alarmdecoder.crt -subj '/CN=AlarmDecoder.local/O=AlarmDecoder.com/C=US' -reqexts SAN -extensions SAN -config <(cat /etc/ssl/openssl.cnf  <(printf "\n[SAN]\nsubjectAltName=DNS:alarmdecoder,DNS:alarmdecoder.local"))
   /usr/sbin/service nginx restart
  ## cleanup state trigger
   echo "$LPREFIX removing /boot/newkeys.txt state file"
   /bin/rm /boot/newkeys.txt
  ## FIXME: Kick everyone off reboot after we are all done with this
  ## /sbin/reboot
fi
EOF
chmod +x /usr/local/bin/alarmdecoder-earlyboot.sh
systemctl enable alarmdecoder-earlyboot

echo "$LPREFIX finished"

