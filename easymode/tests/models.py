from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.db import models

from easymode.admin.models.fields import SafeTextField, SafeHTMLField
from easymode.i18n.decorators import I18n
from easymode.tree.xml.decorators import toxml


@toxml
@I18n('charfield')
class TestModel(models.Model):
    "Used in lots of test"

    charfield = models.CharField(max_length=255, unique=True)
    tags = models.ManyToManyField('TagModel', related_name='testmodels')
    
    def __unicode__(self):
        return u"%s%s - %s" % (self.__class__.__name__, self.pk, self.charfield)

    def natural_key(self):
        return (self.charfield,)
    

class TestSubModel(models.Model):
    "Used in lots of test"

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
    "Used in lots of test"
    
    testsubmodel = models.ForeignKey(TestSubModel, related_name="subsubmodels")
    subsubcharfield = models.CharField(max_length=255)
    
    def __unicode__(self):
        return self.subsubcharfield


@I18n('value')
class TagModel(models.Model):
    "Used in test_generic_relations_also_work (easymode.tests.testcases.testtoxml.RecursiveSerializerTest)"
    value = models.CharField(max_length=23)

    def __serialize__(self, stream):
        stream.startElement('taggy', {})
        stream.characters(self.value)
        stream.endElement('taggy')

@toxml
@I18n('title', 'description')
class TestL10nModel(models.Model):
    """
    Used in easymode.tests.testcases.testi18n.Testi18n and
    easymode.tests.testcases.testsafefields.TestSafeFields.
    """
    title = models.CharField(max_length=200)
    description = SafeTextField()
    body = SafeHTMLField(default='hi i am an error')
    price = models.FloatField()

    def __unicode__(self):
        return u"%s%s" % (self.__class__.__name__, self.pk)


class GenericRelatedModel(models.Model):
    "Used in test_generic_relations_also_work (easymode.tests.testcases.testtoxml.RecursiveSerializerTest)"

    content_type = models.ForeignKey(ContentType)
    parent_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'parent_id')

    name = models.CharField(max_length=100)

    def __unicode__(self):
        return u"%s%s" % (self.__class__.__name__, self.pk)


@toxml
class TestGenericFkModel(models.Model):
    "Used in used in test_generic_relations_also_work (easymode.tests.testcases.testtoxml.RecursiveSerializerTest)"

    name = models.CharField(max_length=100)
    relateds = generic.GenericRelation(GenericRelatedModel, content_type_field='content_type', object_id_field='parent_id')

    def __unicode__(self):
        return u"%s%s" % (self.__class__.__name__, self.pk)


@I18n('a', 'b')
class ManagerErrorModel(models.Model):
    "used in easymode.tests.testcases.testintrospection.TestIntrospection"
    a = models.CharField(max_length=255)
    b = models.ImageField(upload_to='uploads')
    c = models.TextField()

    def __unicode__(self):
        return u"%s %s %s %s" % (self.pk, self.a, self.b, self.c)

@I18n('number', 'another')
class FormTestModel(models.Model):
    "Used in test_form_is_overridden (easymode.tests.testcases.testforms.TestL10nForm"
    number = models.IntegerField()
    other = models.CharField(max_length=255)
    another = models.CharField(max_length=255)


class TopModel(models.Model):
    title = models.CharField('The title', max_length=255)
    subtitle = SafeTextField('The subtitle')
    
    def __unicode__(self):
        return self.title
    
class BottomModel(models.Model):
    top = models.ForeignKey(TopModel)
    
    comment = SafeTextField('Some comment')
    
    def __unicode__(self):
        return self.comment
    
