# -*- coding: utf-8 -*-

from setuptools import setup

project = "ad2web"

setup(
    name=project,
    version='0.1',
    url='https://github.com/nutechsoftware/ad2web',
    description='AD2Web is a web interface for your AlarmDecoder device.',
    author='Scott Petersen',
    author_email='ad2usb@support.nutech.com',
    #packages=["ad2web"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Flask',
        'Flask-SQLAlchemy',
        'Flask-WTF',
        'Flask-Script',
        'Flask-Babel',
        'Flask-Testing',
        'Flask-Mail',
        'Flask-Cache',
        'Flask-Login',
        'Flask-OpenID',
        'nose',
        'alarmdecoder',
        'pyopenssl',
        'gevent-socketio'
    ],
    test_suite='tests',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries'
    ]
)
