from django.db import models
from easymode.i18n.decorators import I18n

# Create your models here.

@I18n('city')
class Foo(models.Model):
    bar = models.CharField(max_length=255, unique=True)
    barstool = models.TextField(max_length=4)
    website = models.URLField()
    address = models.CharField(max_length=32)
    city = models.CharField(max_length=40)

