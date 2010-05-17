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