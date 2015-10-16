#! /usr/bin/env python
# -*- coding: utf-8 -*-


__author__ = 'Patrick Kalmbach, patrick.kalmbach@tum.de'


from setuptools import setup, find_packages


setup(
    name="emgframework",
    version="0.9",
    description="Framework for working with data from biological signals in a ML context",
    license="BSD",
    keywords="Machine Learning, EMG, EEG",
    packages=find_packages(exclude=['tests*', 'doc*', 'nanomsg*, notebooks*']),
    #data_files=[('/usr/local/etc/hyperflex', ['hyperflexcore/config.cfg'])],
    include_package_data=True,
)
