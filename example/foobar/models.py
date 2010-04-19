from django.db import models
from django.utils.translation import ugettext_lazy as _

from easymode.i18n.decorators import I18n
from easymode.tree.decorators import toxml

# Create your models here.

KINDS = (
    ('cow' , _("An animal that produces milk")),
    ('horse' , _("A unit used to measure car engine power")),
)

@toxml
@I18n('city', 'date')
class Foo(models.Model):
    bar = models.CharField(max_length=255, unique=True)
    barstool = models.TextField(max_length=4)
    website = models.URLField()
    address = models.CharField(max_length=32)
    city = models.CharField(max_length=40)
    date = models.DateField()
    
    def __unicode__(self):
        return u"%d. %s" % (self.id, self.bar)
        
    class Meta:
        ordering = ('id',)
        
class Bar(models.Model):
    foo = models.ForeignKey(Foo, related_name='bars')
    
    label = models.CharField(max_length=255)
    date = models.DateField()

    def __unicode__(self):
        return u"%d. %s" % (self.id, self.label)

    class Meta:
        ordering = ('id',)

class Baz(models.Model):
    """I am an independent global model"""
    baz = models.CharField(max_length=255)
    independancy_level = models.IntegerField()
    kind = models.CharField(max_length=255, choices=KINDS)
    
    def __unicode__(self):
        return u"%d. %s" % (self.id, self.baz)
    
    class Meta:
        ordering = ('id',)
    