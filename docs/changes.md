Release Notes
=============

v0.6.0
------

- Django 1.2 is required for easymode as of v0.6.0.
- :func:`~easymode.utils.languagecode.get_real_fieldname` now returns 
  a string instead of :class:`unicode`. This way a :class:`dict` can
  be constructed using it's results as keys, and the dict can be turned
  into keyword arguments of ``filter`` when doing a query in a specific
  language.
- Small improvements in error handling when :ref:`auto_catalog` is ``True``

v0.5.7
------

- Added :class:`easymode.admin.fields.SafeTextField`, a textfield which strips
  all cariage returns before saving, which is required when using 
  :ref:`auto_catalog_ref`.
- Updated django requirement to v1.1.2 because python 2.6.5 will otherwise
  make the unit tests fail.

v0.5.6
------

- The example app now has a working fixture.

v0.5.5
------

- Special admin widgets are nolonger discarded by easymode (issue #3)

v0.5.4
------

- Some data files where not installed correctly by setup.py

v0.5.3
------

- Added :ref:`auto_catalog` setting, see :ref:`auto_catalog_ref`.
- Fixed error in :ref:`easy_locale` when two properties in the
  same model have the same value (eg. title and subtitle are the same).