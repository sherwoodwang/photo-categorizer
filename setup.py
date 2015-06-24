#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(name='photo-categorizer',
      version='0.1',
      classifiers=[
          "Programming Language :: Python",
      ],
      author='Sherwood Wang',
      author_email='sherwood@wang.onl',
      packages=find_packages(),
      install_requires=[
          'ExifRead',
          'pytz',
      ])
