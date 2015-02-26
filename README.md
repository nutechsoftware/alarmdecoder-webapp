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

1. sudo apt-get install nginx gunicorn sendmail libffi-dev python-dev
2. cd /opt/
3. sudo git clone http://github.com/nutechsoftware/alarmdecoder-webapp.git
5. cd alarmdecoder-webapp
6. sudo pip install -r requirements.txt
7. sudo python manage.py initdb
8. sudo cp contrib/nginx/alarmdecoder /etc/nginx/sites-available/
9. sudo ln -s /etc/nginx/sites-available/alarmdecoder /etc/nginx/sites-enabled/
10. sudo rm /etc/nginx/sites-enabled/default
11. sudo cp contrib/gunicorn.d/alarmdecoder /etc/gunicorn.d/
12. Edit /etc/gunicorn.d/alarmdecoder and change the user/group you'd like it to run as.
13. Change permissions on /opt/alarmdecoder-webapp to grant permissions for your chosen user.
14. Optionally install and set permissions for [ser2sock](http://github.com/alarmdecoder/ser2sock.git)
15. sudo service nginx restart
16. sudo service gunicorn restart

## Support

Please visit our [forums](http://www.alarmdecoder.com/forums/).

## Contributing

We love the open-source community and welcome any contributions!  Just submit a pull request through [Github](http://github.com).
