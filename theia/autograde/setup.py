#!/usr/bin/env python

"""The setup script."""

import os
from setuptools import setup, find_packages

if os.path.exists('README.md'):
    with open('README.md') as readme_file:
        readme = readme_file.read()
else:
    readme = ''


# Read requirements line by line, ignoring empty lines and comments
with open('requirements.txt') as f:
    requirements = [
        line.strip() for line in f
        if line.strip() and not line.startswith('#')
    ]

setup_requirements = []
test_requirements = []

setup(
    author="John McCann Cunniff Jr.",
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="CLI component to the Anubis autograder.",
    entry_points={
        'console_scripts': [
            'anubis-autograde=anubis_autograde.__main__:main',
        ],
    },
    install_requires=requirements,
    include_package_data=True,
    keywords='anubis',
    name='anubis-autograde',
    packages=find_packages(include=['anubis_autograde', 'anubis_autograde.*']),
    setup_requires=setup_requirements,
    # test_suite='tests',
    # tests_require=test_requirements,
    version='1.0.0',
    zip_safe=False,
)
