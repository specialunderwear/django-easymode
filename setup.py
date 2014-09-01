#!/usr/bin/env python
import os
import re

from setuptools import setup, find_packages


description="""With easymode you can create backends for dynamic flash/flex
websites.Easymode makes internationalization simple and outputs xml by
default. To tailor the xml to your application, you can transform
it using xslt templates, which easymode integrates.

For more info, look at http://packages.python.org/django-easymode/details.html

documentation at http://packages.python.org/django-easymode/

release notes at http://packages.python.org/django-easymode/changes.html"""

version = '1.4b5'
packages = []
data_files = []

setup(name='django-easymode',
    version=version,
    description='Quickly build backends for flash/flex websites with django',
    author='L. van de Kerkhof',
    author_email='easymode@librelist.com',
    maintainer='L. van de Kerkhof',
    maintainer_email='easymode@librelist.com',
    keywords='adobe flex flash xml xslt i18n internationalization translate django',
    long_description=description,
    install_requires=[
        'setuptools',
        'django>=1.4',
        'polib',
    ],
    url='http://github.com/specialunderwear/django-easymode',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    # for avoiding conflict have one namespace for all apc related eggs.
    namespace_packages=[],
    # include non python files
    include_package_data=True,
    zip_safe=False,
    platforms = "any",
    license='GPL',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Topic :: Software Development :: Localization',
    ],
)
