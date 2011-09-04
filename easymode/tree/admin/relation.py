"""
Contains a modeladmin class that shows links to all related items in its change_view.

If you want to use :class:`InvisibleModelAdmin` make sure easymode comes before
``django.contrib.admin`` in the ``INSTALLED_APPS`` because it has to 
override admin/index.html to make it work.
"""
from django.http import HttpResponseRedirect
from django.forms.models import  modelformset_factory
from django.core import urlresolvers
from django.conf import settings
from django.utils.encoding import force_unicode

from easymode.tree.introspection import get_foreign_key_desciptors
from easymode.tree.admin.formsets import VisiblePrimaryKeyFormset
from easymode.utils.languagecode import strip_language_code

if 'reversion' in settings.INSTALLED_APPS:
    from reversion.admin import VersionAdmin
    AdminBase = VersionAdmin
else:
    from django.contrib import admin
    AdminBase = admin.ModelAdmin

class _CanFindParentLink(object):
    """Adds function to find a link to a parent model"""
        
    def _get_parent_link(self, object_id):
        parent_link_data = {}
        if hasattr(self, 'parent_link'):
            parent_link = getattr(self.model, self.parent_link)
            instance = self.model.objects.get(pk=object_id)

            parent = parent_link.__get__(instance)
            parent_type_name = parent._meta.object_name.lower()
            parent_name = parent
            parent_id = str(parent_link.field.value_from_object(instance))

            info = (self.admin_site.name, parent._meta.app_label, parent_type_name)
            
            parent_link_data['parent_model'] = strip_language_code(urlresolvers.reverse("%s:%s_%s_change" % info, args=[parent_id]))
            parent_link_data['parent_name'] = "%s %s" % (force_unicode(parent._meta.verbose_name), parent_name)
        
        return parent_link_data


class ForeignKeyAwareModelAdmin(AdminBase, _CanFindParentLink):
    """
    An admin class that display links to related items.
    
    This class is deprecated, please use :class:`easymode.tree.admin.abstract.LinkInline`,
    :class:`easymode.tree.admin.abstract.LinkedItemAdmin` instead.
    
    This can be used for hierarchies of object deeper then 3
    levels, where :class:`InlineModelAdmin` can not be used anymore, but
    the parent/child relation is still there.
    
    usage::
    
        from easymode.tree.admin.relation import ForeignKeyAwareModelAdmin
        
        class SomeAdmin(ForeignKeyAwareModelAdmin):
            children = [SomeModelThatPointsToUs, AnotherModelThatPointsTous]
            invisible_in_admin = False
        
        admin.site.register(SomeModelWithLotsOfRelations, SomeAdmin)
    
    This will add the ``SomeModelThatPointsToUs`` and ``AnotherModelThatPointsTous`` to
    the ``SomeModelWithLotsOfRelations`` admin interface and you can add these children
    or edit them there.
    
    See :class:`InvisibleModelAdmin` if you want to hide the admin interface for ``SomeModelThatPointsToUs``
    and ``AnotherModelThatPointsTous`` admin interface from the admin listing.
    
    .. attribute:: auto_aware
    
        If ``auto_aware`` is true, the admin will find out for itself which
        models are child nodes, by inspecting it's managers.
        
    .. attribute:: parent_link
        
        To have sane breadcrumbs if the :class:`~easymode.tree.admin.relation.ForeignKeyAwareModelAdmin`
        is used as child of another :class:`~easymode.tree.admin.relation.ForeignKeyAwareModelAdmin`
        and make the save button return to the parent instead of the app listing, the
        ``parent_link`` should be set.
        
        It must be set to the *name* of the ``ForeignKey`` that points to the parent.
    
    .. attribute:: children
        
        If the order of the children should be changed or not all children should be
        displayed, you can specify the children manually.
        
        children should be set to a list of models that are child nodes of the model
        class that this admin class makes editable:
            
    .. attribute:: invisible_in_admin
    
        The :class:`~easymode.tree.admin.relation.ForeignKeyAwareModelAdmin` will not
        be shown in the admin listing if this value is ``True``. The default is ``True``.
    
    """
    change_form_template = 'tree/admin/change_form_with_related_links.html'
    
    invisible_in_admin = True
    auto_aware = True
    children = []
    
    _descriptor_cache = {}

    class Media:
        js = (
            'easymode/js/adminoverride.js',
        )
    
    def __init__(self, model, admin_site):
        super(ForeignKeyAwareModelAdmin, self).__init__(model, admin_site)

        # look up all foreign key descriptors
        descriptors = get_foreign_key_desciptors(self.model)
        self._descriptor_cache = dict([(x[1].related.model, x[0]) for x in descriptors])
        
        # if no children are set and autoaware is true, 
        # set the children
        if not self.children and self.auto_aware:
            self.children = [x[1].related.model for x in descriptors]
        
    def get_model_perms(self, request):
        perms = super(ForeignKeyAwareModelAdmin, self).get_model_perms(request)
        perms['invisible_in_admin'] = self.invisible_in_admin
        return perms
        
    def change_view(self, request, object_id, extra_context=None):
        inline_links = {}
        inline_links['extra_forms'] = self.extra_forms(object_id)

        # retrieve link to parent for breadcrumb path
        inline_links.update(self._get_parent_link(object_id))
        if extra_context:
            inline_links.update(extra_context)
            
        return super(ForeignKeyAwareModelAdmin, self).change_view(request, object_id, inline_links)

    def extra_forms(self, object_id):

        instance = self.model.objects.get(pk=object_id)
                
        extra_formsets = []

        for child in self.children:
            factory = modelformset_factory(child, extra=0, fields=['id'], formset=VisiblePrimaryKeyFormset)
            descriptor_name = self._descriptor_cache[child]
            descriptor = getattr(instance, descriptor_name)
            
            # create formset
            form = factory(queryset=descriptor.all())

            # this will find the name of the property in the model
            # the descriptor's inverse references
            try:
                field_name = descriptor.core_filters.keys().pop().split('__')[0]
            except Exception:
                field_name = instance._meta.object_name.lower()
            
            # find url for the + button
            url_descriptor = (self.admin_site.name, child._meta.app_label, child._meta.object_name.lower())
            url_pattern = '%s:%s_%s_add' % url_descriptor
            url = urlresolvers.reverse(url_pattern)
                
            #add properties to the formset            
            form.parent = instance            
            form.name = child.__name__.lower()
            form.title = child._meta.verbose_name_plural            
            form.addurl = "%s?%s=%s" % (strip_language_code(url), field_name, object_id)
            
            extra_formsets.append( form )            

        return extra_formsets
        


class InvisibleModelAdmin(AdminBase, _CanFindParentLink):
    """
    An admin class that can be used as admin for children
    of :class:`~easymode.tree.admin.relation.ForeignKeyAwareModelAdmin`. 
    
    This way they will be hidden in 
    the admin interface so they can only be accessed via ``ForeignKeyAwareModelAdmin``.
    usage::
        
        from django.db import models
        from django.contrib import admin
        from easymode.tree.admin.relation import *
        
        class Bar(models.Model):
            foo = models.ForeignKey(Foo, related_name='bars')
            label = models.CharField(max_length=255)
            
        class BarAdmin(InvisibleModelAdmin):
            model = Bar
            parent_link = 'foo'
    
        admin.site.register(Bar, BarAdmin)
        
    .. attribute:: parent_link
        
        When :class:`~easymode.tree.admin.relation.InvisibleModelAdmin` is used, it is nolonger
        displayed in the admin listing as an editable model. To have sane breadcrumbs
        and make the save button return to the parent instead of the app listing, the
        ``parent_link`` should be set.
        
        It must be set to the *name* of the ``ForeignKey`` that points to the parent.
    """
    change_form_template = 'tree/admin/change_form_with_parent_link.html'
    invisible_in_admin = True

    def get_model_perms(self, request):
        perms = super(InvisibleModelAdmin, self).get_model_perms(request)
        perms['invisible_in_admin'] = self.invisible_in_admin
        return perms
        
    def change_view(self, request, object_id, extra_context=None):

        # retrieve link to parent for breadcrumb path
        defaults = self._get_parent_link(object_id)

        if extra_context:
            defaults.update(extra_context)
        
        response = super(InvisibleModelAdmin, self).change_view(request, object_id, defaults)
        if response.get('Location', False) == '../':
            return HttpResponseRedirect(defaults.get('parent_model', '../'))
            
        return response
