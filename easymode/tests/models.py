from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models

from easymode.admin.models.fields import DiocoreTextField, DiocoreHTMLField, FlashUrlField, DiocoreCharField
from easymode.i18n.decorators import I18n
from easymode.tree.decorators import toxml
from easymode.easypublisher.models import EasyPublisherModel


@toxml
@I18n('charfield')
class TestModel(models.Model):
    """test model"""

    charfield = models.CharField(max_length=255, unique=True)
    tags = models.ManyToManyField('TagModel', related_name='testmodels')
    
    def __unicode__(self):
        return u"%s%s - %s" % (self.__class__.__name__, self.pk, self.charfield)

    def natural_key(self):
        return (self.charfield,)
    

class TestSubModel(models.Model):
    """hangs onto testmodel"""

    testmodel = models.ForeignKey(TestModel, related_name='submodels')
    subcharfield = models.CharField(max_length=255)
    subintegerfield = models.IntegerField()

    def __unicode__(self):
        return u"%s%s - %s" % (self.__class__.__name__, self.pk, self.subcharfield)


class TestSecondSubmodel(models.Model):
    """hangs on to TestModel as well"""
    
    testmodel = models.ForeignKey(TestModel, related_name='secondsubmodels')
    ultrafield = models.TextField()
    
    def __unicode__(self):
        return self.ultrafield


class TestSubSubModel(models.Model):
    """Even subier sub model"""
    
    testsubmodel = models.ForeignKey(TestSubModel, related_name="subsubmodels")
    subsubcharfield = models.CharField(max_length=255)
    
    def __unicode__(self):
        return self.subsubcharfield


@I18n('value')
class TagModel(models.Model):
    
    value = models.CharField(max_length=23)


@toxml
@I18n('title', 'description')
class TestL10nModel(models.Model):

    title = DiocoreCharField(max_length=200, font="arial")
    description = DiocoreTextField(font="arial")
    body = DiocoreHTMLField(default='hi i am an error', font="arial")
    price = models.FloatField()

    def __unicode__(self):
        return u"%s%s" % (self.__class__.__name__, self.pk)


class GenericRelatedModel(models.Model):
    """it is used in a generic relation"""

    content_type = models.ForeignKey(ContentType)
    parent_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'parent_id')

    name = models.CharField(max_length=100)

    def __unicode__(self):
        return u"%s%s" % (self.__class__.__name__, self.pk)


@toxml
class TestGenericFkModel(models.Model):
    """it is used for testing"""

    name = models.CharField(max_length=100)
    relateds = generic.GenericRelation(GenericRelatedModel, content_type_field='content_type', object_id_field='parent_id')

    def __unicode__(self):
        return u"%s%s" % (self.__class__.__name__, self.pk)

class TestEasypublisherModel(EasyPublisherModel):
    label = models.CharField(max_length=200)
    nogeenlabel = models.CharField(max_length=200)
    def __unicode__(self):
        return "%s" % self.label
    
class TestEasypublisherRelatedModel(models.Model):
    parent = models.ForeignKey(TestEasypublisherModel)
    
    extra = models.CharField(max_length=200)
    def __unicode__(self):
        return "%s" % self.extra

@I18n('a', 'b')
class ManagerErrorModel(models.Model):
    a = models.CharField(max_length=255)
    b = models.ImageField(upload_to='uploads')
    c = models.TextField()

    def __unicode__(self):
        return u"%s %s %s %s" % (self.pk, self.a, self.b, self.c)

@I18n('number', 'another')
class FormTestModel(models.Model):
    number = models.IntegerField()
    other = models.CharField(max_length=255)
    another = models.CharField(max_length=255)
    