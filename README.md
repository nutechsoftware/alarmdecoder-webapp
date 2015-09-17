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

If you'd rather do it by hand you can follow these steps:

1. sudo apt-get install gunicorn sendmail libffi-dev python-dev build-essential libssl-dev curl libpcre3-dev libpcre++-dev zlib1g-dev libcurl4-openssl-dev minicom telnet python2.7 autoconf automake avahi-daemon screen locales dosfstools vim python2.7-dev sendmail sqlite3
2. wget https://bootstrap.pypa.io/get-pip.py
3. sudo python get-pip.py
4. VERSION=1.7.4
5. curl http://nginx.org/download/nginx-$VERSION.tar.gz | tar zxvf -
6. cd nginx-$VERSION
7. ./configure --sbin-path=/usr/sbin/nginx --conf-path=/etc/nginx/nginx.conf --pid-path=/var/run/nginx.pid --error-log-path=/var/log/nginx/error.log --http-log-path=/var/log/nginx/access.log --with-http_ssl_module --with-ipv6
8. make
9. sudo make install
10. sudo mkdir -p /var/www
11. sudo mkdir -p /etc/nginx/ssl
11. sudo cp html/* /var/www
12. sudo service nginx start
13. sudo pip install gunicorn --upgrade
14. sudo ln -s /usr/local/bin/gunicorn /usr/bin/gunicorn
15. cd /opt/
16. sudo git clone http://github.com/nutechsoftware/alarmdecoder-webapp.git
17. cd alarmdecoder-webapp
18. sudo pip install -r requirements.txt
19. sudo python manage.py initdb
20. sudo cp contrib/nginx/alarmdecoder /etc/nginx/sites-available/
21. sudo ln -s /etc/nginx/sites-available/alarmdecoder /etc/nginx/sites-enabled/
22. sudo rm /etc/nginx/sites-enabled/default
23. sudo cp contrib/gunicorn.d/alarmdecoder /etc/gunicorn.d/
24. Edit /etc/gunicorn.d/alarmdecoder and change the user/group you'd like it to run as.
25. Change permissions on /opt/alarmdecoder-webapp to grant permissions for your chosen user.
26. Optionally install and set permissions for [ser2sock](http://github.com/alarmdecoder/ser2sock.git)
27. Create self-signed SSL certificate for HTTPS - sudo openssl req -x509 -nodes -days 365 -newkey rsa:4096 -keyout /etc/nginx/ssl/alarmdecoder.key -out /etc/nginx/ssl/alarmdecoder.crt
28. sudo service nginx restart
29. sudo service gunicorn restart

## Support

Please visit our [forums](http://www.alarmdecoder.com/forums/).

## Contributing

We love the open-source community and welcome any contributions!  Just submit a pull request through [Github](http://github.com).
