import os

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from easymode.tree.decorators import toxml
from easymode.admin.fields import *
from easymode.i18n.decorators import I18n

@I18n('charfield')
@toxml
class TestModel(models.Model):
    """test model"""

    charfield = models.CharField(max_length=255)
    
    def __unicode__(self):
        return u"%s%s - %s" % (self.__class__.__name__, self.pk, self.charfield)

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

@toxml
class UrlFieldTestModel(models.Model):
    title    = models.CharField(max_length=256)
    revision = models.PositiveIntegerField()
    url      = HtmlFlashUrlField(max_length=256)
# 
# @toxml
# class IncludeFileFieldTestModel(models.Model):
#     title = models.CharField(max_length=256)
#     file  = IncludeFileField(base=os.path.dirname(__file__), relative_path='hax')
# 
# @toxml
# class RemoteIncludeFieldModel(models.Model):
#     title = models.CharField(max_length=256)
#     url   = RemoteIncludeField(interval=60)

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


