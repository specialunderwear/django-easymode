from django.db import models
from easymode.i18n.decorators import I18n
from easymode.tree.decorators import toxml

# Create your models here.

@toxml
@I18n('city')
class Foo(models.Model):
    bar = models.CharField(max_length=255, unique=True)
    barstool = models.TextField(max_length=4)
    website = models.URLField()
    address = models.CharField(max_length=32)
    city = models.CharField(max_length=40)

class Bar(models.Model):
    foo = models.ForeignKey(Foo, related_name='bars')
    
    label = models.CharField(max_length=255)
