#!/usr/bin/env python
import os
from distutils.core import setup
from distutils.command.install import INSTALL_SCHEMES

version = '0.5.4'
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
      description='A toolkit for making xml based flash websites with django',
      author='L. van de Kerkhof',
      url='http://github.com/LUKKIEN/django-easymode',
      packages=packages,
      data_files=data_files,
      install_requires=['Django==1.1.1', 'lxml>=2.2.2', 'polib>=0.5.1','django-reversion>=1.2'],
     )
