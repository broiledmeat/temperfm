#!/usr/bin/env python3
import setuptools
from distutils.core import setup

base_package = 'temperfm'

version = __import__('temperfm').__version__
packages = [base_package] + ['{}.{}'.format(base_package, package)
                             for package in setuptools.find_packages(base_package)]

setup(
    name='temperfm',
    description='Plugin based static content generator',
    url='https://github.com/broiledmeat/temperfm',
    license='Apache License, Version 2.0',
    author='Derrick Staples',
    author_email='broiledmeat@gmail.com',
    version=version,
    packages=packages,
    requires=['requests'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)

