#!/usr/bin/env python

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

setup(
    name='backupcpy',
    version='1.0.0',
    description='Backupcpy is a tiny and elegant backup archive assembler',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Addvilz',
    author_email='mrtreinis@gmail.com',
    url='https://github.com/Addvilz/backupcpy',
    download_url='https://github.com/Addvilz/backupcpy',
    license='Apache 2.0',
    platforms='UNIX',
    packages=find_packages(),
    install_requires=[
        'pyyaml>=3.13'
    ],
    entry_points={
        'console_scripts': [
            'backupcpy = backupcpy.main:main',
        ]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: System :: Archiving :: Backup'
    ],
)
