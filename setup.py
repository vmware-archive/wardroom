#/usr/bin/env python3

from setuptools import setup

setup(
    name="Wardroom",
    version="0.1",
    description="Python utility for building and managing wardroom artifacts",
    author="Heptio",
    url="https://github.com/heptiolabs/wardroom",
    packages=['wardroom'],
    entry_points={
        'console_scripts': [
            'wardroom=wardroom.cli:cli'
        ]
    },
    install_requires=[
        'boto3>=1.5',
        'click>=6.0'
    ]
)
