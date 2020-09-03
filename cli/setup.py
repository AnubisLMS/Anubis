#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

requirements = ['Click>=7.0', 'requests','pyyaml','docker']

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="John McCann Cunniff Jr.",
    author_email='johncunniff1248@gmail.com',
    python_requires='>=3.5',
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
            'anubis=anubis.cli:main',
        ],
    },
    install_requires=requirements,
    long_description=readme + '\n',
    include_package_data=True,
    keywords='anubis',
    name='anubis',
    packages=find_packages(include=['anubis', 'anubis.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    version='v2.0.0',
    zip_safe=False,
)
