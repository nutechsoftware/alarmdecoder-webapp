# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name="alarmdecoder-webapp",
    version='0.5.0',
    url='https://github.com/nutechsoftware/alarmdecoder-webapp',
    description='AlarmDecoder-webapp provides a web interface for your AlarmDecoder device.',
    author='Nu Tech Software Solutions, Inc.',
    author_email='ad2usb@support.nutech.com',
    packages=["ad2web"],
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
        'alarmdecoder>=0.9',
        'pyopenssl',
        'gevent-socketio',
        'jsonpickle',
        'sleekxmpp',
        'psutil>=2.0.0',
        'sh',
        'alembic',
        'netifaces',
    ],
    test_suite='tests',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries'
        'Topic :: Communications',
        'Topic :: Home Automation',
        'Topic :: Security',
    ]
)
