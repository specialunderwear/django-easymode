#!/usr/bin/env python
import os
import re
from distutils.core import setup
from distutils.command.install import INSTALL_SCHEMES

description="""With easymode you can create backends for dynamic flash/flex
websites.Easymode makes internationalization simple and outputs xml by
default. To tailor the xml to your application, you can transform
it using xslt templates, which easymode integrates.

For more info, look at http://packages.python.org/django-easymode/details.html

documentation at http://packages.python.org/django-easymode/

release notes at http://packages.python.org/django-easymode/changes.html"""

version = '0.14.4'
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

PYC = re.compile(r'.*\.py[co]$')

for dirpath, dirnames, filenames in os.walk('easymode'):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))
    elif filenames:
        data_files.append([dirpath, 
            [os.path.join(dirpath, f) for f in filenames if not PYC.match(f)]
        ])

setup(name='django-easymode',
    version=version,
    description='Quickly build backends for flash/flex websites with django',
    author='L. van de Kerkhof',
    author_email='easymode@librelist.com',
    maintainer='L. van de Kerkhof',
    maintainer_email='easymode@librelist.com',
    keywords='adobe flex flash xml xslt',
    long_description=description,
    url='http://github.com/LUKKIEN/django-easymode',
    packages=packages,
    data_files=data_files,
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
