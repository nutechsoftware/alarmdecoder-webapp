# AlarmDecoder Webapp

## Summary

This is the home of the official webapp for the [AlarmDecoder](http://www.alarmdecoder.com) family of home security devices.

![Keypad Screenshot](http://github.com/nutechsoftware/alarmdecoder-webapp/raw/master/screenshot.png "Keypad Screenshot")

## Features

- Supports all of the [AlarmDecoder](http://www.alarmdecoder.com) devices: AD2USB, AD2SERIAL and AD2PI.
- Web-based keypad for your alarm system
- Notifications on alarm events
- Multiple user accounts and per-user notifications and certificates (if configured)

## Installation

### Requirements

- nginx >= 1.6
- gunicorn

NOTE: Other web and WSGI servers will likely work but will require configuration.

### Pre-installed Image

If you're running on a Raspberry Pi the easiest way to get started is to download our pre-configured Raspbian image.  The image can be found at [here](http://www.alarmdecoder.com/wiki/index.php/Raspberry_Pi).

### Manual Installation

If you would rather do it by hand you can follow these steps using a Raspbian 9 base image:
You can also look at the [PiBakery](contrib/PiBakery/) recipe for the steps. This presumes you will be the pi user with a monitor and keyboard attached to the Pi. Optionally you can connect over the network after enabling ssh and WiFi. See also [Headless wifi setup](https://www.raspberrypi.org/documentation/configuration/wireless/headless.md)
* Enable SSH at boot (optional)
```
sudo touch /boot/ssh
sudo rm /etc/ssh/ssh_host_*; dpkg-reconfigure openssh-server # !!Change keys!!
```
* Set default user password to 'raspberry' (user configuration)
```
passwd
```
* Modify config.txt to enable the GPIO UART and force cpu to turbo tested on Pi3, PiB, Pi3B+ and PiZero
```
sudo sed -i '/enable_uart\|pi3-miniuart-bt-overlay\|force_turbo/d' /boot/config.txt
```  
* Disable serial console so the kernel does not try to talk to the AD2Pi on the GPIO header  
```
sudo raspi-config nonint do_serial 1
```
* Set hostname to AlarmDecoder
```
sudo hostname AlarmDecoder
```
* Set country code for WIFI (user option)
```
sudo raspi-config nonint do_wifi_country US
```
* Set TZ (user option) (user option)
```
sudo raspi-config nonint do_change_timezone America/Los_Angeles
``` 
* Set the Keyboard layout and language (user option)
```
sudo raspi-config nonint do_configure_keyboard US pc101
```
* Setup WiFi (optional) see also [Headless wifi setup](https://www.raspberrypi.org/documentation/configuration/wireless/headless.md)
```
sudo echo -E '
network={
    ssid="«your_SSID»"
    psk="«your_PSK»"
    key_mgmt=WPA-PSK
}' >> /etc/wpa_supplicant/wpa_supplicant.conf
```
* Resize the file system and reboot
```
sudo raspi-config nonint do_expand_rootfs
```
* Update repositories.
```
sudo apt-get update
```
* Install packages
```
sudo apt-get install \
  autoconf \
  automake \
  build-essential \
  cmake \
  cmake-data \
  git \
  gunicorn \
  libcurl4-openssl-dev \
  libffi-dev \
  libpcre3-dev \
  libpcre++-dev \
  libssl-dev \
  minicom \
  miniupnpc \
  nginx \
  python2.7-dev \
  python-dev \
  python-httplib2 \
  python-opencv \
  python-pip \
  python-virtualenv \
  screen \
  sendmail \
  sqlite3 \
  telnet \
  vim \
  zlib1g-dev
```
* Update pip
```
sudo pip install --upgrade pip
```
* Update pip setuptools
```
sudo pip install --upgrade setuptools
```
* Create needed directories and set permissions for updates
```
sudo mkdir -p /opt/alarmdecoder /opt/alarmdecoder-webapp && sudo chown pi:pi /opt/alarmdecoder /opt/alarmdecoder-webapp
``` 
* Grab the latest master branch of the AlarmDecoder Python API
```
cd /opt && git clone https://github.com/nutechsoftware/alarmdecoder.git
```
* Grab the latest master branch of the AlarmDecoder web services app
```
cd /opt && git clone https://github.com/nutechsoftware/alarmdecoder-webapp.git
```
* Add Python requirements to the entire system as root
```
cd /opt/alarmdecoder-webapp/ && sudo pip install -r requirements.txt
```
* Add ser2sock
```
cd /opt && sudo git clone https://github.com/nutechsoftware/ser2sock.git
cd /opt/ser2sock/ && sudo ./configure && sudo make && sudo cp ./ser2sock /usr/local/bin/
```
* Allow pi user to have r/w access to serial ports and a few key files for the WEB services to udpate by adding them to the same group and adding +w on that group
```
sudo usermod -a -G dialout pi
sudo chgrp dialout /etc/hosts /etc/hostname
sudo chmod g+w /etc/hosts /etc/hostname
```
* Create a ser2sock config folder owned by pi in etc and add config and update it
```
sudo mkdir -p /etc/ser2sock && sudo cp /opt/ser2sock/etc/ser2sock/ser2sock.conf /etc/ser2sock/ && sudo chown -R pi:pi /etc/ser2sock
sudo sed -i 's/raw_device_mode = 0/raw_device_mode = 1/g' /etc/ser2sock/ser2sock.conf
sudo sed -i 's/device = \/dev\/ttyAMA0/device = \/dev\/serial0/g' /etc/ser2sock/ser2sock.conf
```
* Set ser2sock to start at boot as user pi
```
sudo cp /opt/ser2sock/init/ser2sock /etc/init.d/
sudo sed -i 's/EXTRA_START_ARGS=/#EXTRA_START_ARGS=/g' /etc/init.d/ser2sock
sudo sed -i 's/#RUN_AS=.*/RUN_AS=pi:pi/g' /etc/init.d/ser2sock
sudo update-rc.d ser2sock defaults
```  
* Enable the avahi service
```
cat <<EOF | sudo tee /etc/avahi/services/alarmdecoder.service
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
```
* Create nginx ssl folder
```
sudo mkdir -p /etc/nginx/ssl
```
* Remove all default web content
```
sudo rm -r /var/www/html/
```
* Enable gunicorn service and tuning for Alarmdecoder webapp
```
echo -e '[Unit]\nDescription=gunicorn daemon\nAfter=network.target\n\n[Service]\nPIDFile=/run/gunicorn/pid\nUser=pi\nGroup=dialout\nWorkingDirectory=/opt/alarmdecoder-webapp\nExecStart=/usr/bin/gunicorn --worker-class=socketio.sgunicorn.GeventSocketIOWorker --timeout=120 --env=POLICY_SERVER=0 --log-level=debug wsgi:application\nExecReload=/bin/kill -s HUP $MAINPID\nExecStop=/bin/kill -s TERM $MAINPID\nPrivateTmp=true\n\n[Install]\nWantedBy=multi-user.target\n' | sudo tee /etc/systemd/user/gunicorn.service > /dev/null
```
* Enable gunicorn server and set to start at boot
```
sudo ln -s /etc/systemd/user/gunicorn.service /etc/systemd/system/multi-user.target.wants/gunicorn.service
sudo ln -s /etc/systemd/user/gunicorn.service /etc/systemd/system/gunicorn.service
```
* Enable log rotate for webapp and gunicorn
```
echo -e '/opt/alarmdecoder-webapp/instance/logs/*.log {\nweekly\nmissingok\nrotate 5\ncompress\ndelaycompress\nnotifempty\ncreate 0640 pi pi\nsharedscripts\n\ }' > /etc/logrotate.d/alarmdecoder
sudo echo -e '/var/log/gunicorn/*.log {\nweekly\nmissingok\nrotate 5\ncompress\ndelaycompress\nnotifempty\ncreate 0640 www-data www-data\nsharedscripts\npostrotate\n[ -s /run/gunicorn/alarmdecoder.pid ] && kill -USR1 `cat /run/gunicorn/alarmdecoder.pid`\nendscript\n}' | sudo tee /etc/logrotate.d/gunicorn > /dev/null
```
* Create gunicorn app config directory and add our app configuration
```
sudo mkdir /etc/gunicorn.d/
sudo cp /opt/alarmdecoder-webapp/contrib/gunicorn.d/alarmdecoder /etc/gunicorn.d/
```
* Generate an ssl certificate for the webapp
```
sudo openssl req -x509 -nodes -sha256 -days 3650 -newkey rsa:4096 -keyout /etc/nginx/ssl/alarmdecoder.key -out /etc/nginx/ssl/alarmdecoder.crt -subj '/CN=AlarmDecoder.local/O=AlarmDecoder.com/C=US'
```
* Add nginx service configuration for the webapp
```
sudo cp /opt/alarmdecoder-webapp/contrib/nginx/nginx.service /lib/systemd/system/nginx.service
```
* Remove the default site and add the alarmdecoder nginx site configuration and enable it
```
sudo rm /etc/nginx/sites-enabled/default
sudo cp /opt/alarmdecoder-webapp/contrib/nginx/alarmdecoder /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/alarmdecoder /etc/nginx/sites-enabled/
```
* Init the AD2Web database as pi user
```
cd /opt/alarmdecoder-webapp/ && python manage.py initdb
```

## Support

Please visit our [forums](http://www.alarmdecoder.com/forums/).

## Contributing

We love the open-source community and welcome any contributions!  Just submit a pull request through [Github](http://github.com).
