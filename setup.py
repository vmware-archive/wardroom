from setuptools import setup

setup(
    name="wardroom",
    version="0.1",
    description="Python utility for managing wardroom artifacts",
    author="Heptio",
    url="https://github.com/heptiolabs/wardroom",
    packages=['wardroom'],
    entry_points={
        'console_scripts': [
            'wardroom=wardroom.shell:main'
        ]
    },
    install_requires=[
        'boto3>=1.5'
    ]
)
