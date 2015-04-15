#! /usr/bin/env python
# -*- coding: utf-8 -*-


__authors__ = ['Justin Bayer, bayer.justin@googlemail.com']


from setuptools import setup, find_packages


setup(
    name="emg",
    version="pre-0.1",
    description="emg toolbox from BRML",
    keywords="emg Machine Learning",
    packages=find_packages(exclude=['examples', 'docs']),
    include_package_data=True,
)

