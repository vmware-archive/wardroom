#!/usr/bin/env python3

from setuptools import setup

setup(name="Wardroom packer helpers",
      version="0.1",
      description="Python utils for uploading and copying AMIs",
      author="Heptio",
      url="https://github.com/heptiolabs/wardroom",
      scripts=["copy-ami"],
      install_requires=['boto3 >= 1.5']
)
