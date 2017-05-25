"""
Flask-GnosisDB
-------------

This is the description for that library
"""
from setuptools import setup

setup(
    name='Flask-GnosisDB',
    version='1.0',
    url='https://github.com/gnosis/gnosisdb/',
    license='BSD',
    author='Giacomo Licari, Denis Granha, Stefan George',
    author_email='giacomo.licari@gnosis.pm, denis@gnosis.pm, stefan@gnosis.pm',
    description='A GnosisDB extension for Flask',
    long_description=__doc__,
    py_modules=['flask_gnosisdb'],
    # if you would be using a package instead use packages instead
    # of py_modules:
    # packages=['flask_mongo'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=['flask', 'pymongo'],
    classifiers=[
        'Environment :: Database Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)