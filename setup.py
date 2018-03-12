import os

from setuptools import find_packages, setup

# from pip.req import parse_requirements

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

# requirements
# install_reqs = parse_requirements('requirements.txt', session='hack')
# reqs = [str(ir.req) for ir in install_reqs]

requirements = [
    'djangorestframework',
    'django-eth-events==2.0.6',
    'ethereum==1.6.1',
    'eth-abi==1.0.0',
    'eth-utils==0.7.4'
]

setup(
    name='django_gnosisdb',
    version='1.0.1',
    packages=find_packages(exclude=["*.tests",
                                    "*.tests.*",
                                    "tests.*",
                                    "tests"]),
    include_package_data=True,
    install_requires=requirements,
    license='BSD License',  # example license
    description='The Gnosisdb django app',
    url='https://github.com/gnosis/gnosisdb',
    author='Gnosis Inc.',
    author_email='giacomo.licari@gnosis.pm, denis@gnosis.pm, stefan@gnosis.pm, uxio@gnosis.pm',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: X.Y',  # replace "X.Y" as appropriate
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',  # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        # Replace these appropriately if you are stuck on Python 2.
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
