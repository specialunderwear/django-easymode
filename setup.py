#!/usr/bin/env python
import os
from distutils.core import setup
from distutils.command.install import INSTALL_SCHEMES

description="""Easymode is an aspect oriented toolkit that helps making xml based flash websites easy.
The tools included in the toolkit to help you make these kind of sites include:

* Internationalization of models, with admin support
* Translation of model data using gettext
* Automatic generation of xml from model trees using xslt
* Admin support for model trees with more than 2 levels of related items
* Basic approval support for models

documentation at http://packages.python.org/django-easymode/"""

version = '0.5.6'
packages = []
data_files = []

for scheme in INSTALL_SCHEMES.values():
    scheme["data"] = scheme["purelib"]

def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

for dirpath, dirnames, filenames in os.walk('easymode'):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))
    elif filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])

setup(name='django-easymode',
    version=version,
    description='Toolkit to ease development of internationalized xml based (flash) websites with django',
    author='L. van de Kerkhof',
    maintainer='L. van de Kerkhof',
    maintainer_email='specialunderwear@gmail.com',
    long_description=description,
    url='http://github.com/LUKKIEN/django-easymode',
    packages=packages,
    data_files=data_files,
    platforms = "any",
    install_requires=['Django==1.1.1', 'lxml>=2.2.2', 'polib>=0.5.1','django-reversion>=1.2'],
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
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Topic :: Software Development :: Localization',
    ],
)
