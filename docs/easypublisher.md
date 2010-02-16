Easy Publisher
==============

Easy publisher is a very simple approval application. It uses
`django-reversion <http://code.google.com/p/django-reversion/>`_ to store drafted
content. This has the very nice side effect that all drafts are in your history.

There is only one layer of approval, either you've got publishing rights or you
don't. Anyone with publisher right move content from draft to published, as lang 
as they've got permission to modify the content.