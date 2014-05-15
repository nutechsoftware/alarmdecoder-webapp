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

### Pre-installed Image

If you're running on a Raspberry Pi the easiest way to get started is to download our pre-configured Raspbian image.  The image can be found at [here](http://www.alarmdecoder.com/wiki/index.php/Raspberry_Pi).

### Manual Installation

If you'd rather do it by hand you can follow these steps:

1. sudo apt-get install nginx gunicorn
2. cd /opt/
3. sudo git clone http://github.com/nutechsoftware/alarmdecoder-webapp.git
4. sudo chown -R \`whoami\` alarmdecoder-webapp
5. cd alarmdecoder-webapp
6. sudo pip install -r requirements.txt
7. sudo cp contrib/nginx/alarmdecoder /etc/nginx/sites-available/
8. sudo ln -s /etc/nginx/sites-available/alarmdecoder /etc/nginx/sites-enabled/
9. sudo rm /etc/nginx/sites-enabled/default
10. sudo cp contrib/gunicorn.d/alarmdecoder /etc/gunicorn.d/
11. Optionally configure (ser2sock)[http://github.com/alarmdecoder/ser2sock.git]
12. sudo service nginx restart
13. sudo service gunicorn restart

## Support

Please visit our (forums)[http://www.alarmdecoder.com/forums/].

## Contributing

We love the open-source community and welcome any contributions!  Just submit a pull request through [Github](http://github.com).
