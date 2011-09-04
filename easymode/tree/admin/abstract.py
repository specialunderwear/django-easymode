from django.contrib import admin
from django.http import HttpResponseRedirect

from easymode.tree.admin.forms import RecursiveInlineFormSet
from easymode.tree.admin.relation import _CanFindParentLink

__all__ = ('LinkInline', 'LinkedItemAdmin')

class LinkInline(admin.StackedInline):
    """
    A base class for an admin inline that will render as links to the change_view.
    This means you have to also register the model you are inlining with a non-inline
    ModelAdmin::
        
        class BottomAdmin(InvisibleModelAdmin):
            parent_link = 'top'
        
        class BottomLinkInline(LinkInline):
            fields = ('top',)
            model = BottomModel
    
    .. attribute:: fields
        
        It is mandatory to set the fields or fieldsets attribute of a class extending
        ``LinkInline``. If you don't, all the fields will be show, instead of only
        the change or add button. Ofcourse it can't hurt to add some ``read_only_fields``
        to add some context.
    """
    formset = RecursiveInlineFormSet
    template = 'tree/admin/edit_inline/link_inline.html'
    extra = 1

class LinkedItemAdmin(admin.ModelAdmin, _CanFindParentLink):
    """
    This class should be used as the base class for all admin classes that have
    :class:`~easymode.tree.admin.abstract.LinkInline` inlines::
    
        class TopAdmin(LinkedItemAdmin):
            inlines = [BottomLinkInline]
        
    Also it can be used
    to make save return to a parent model in a tree context. You could also use
    :class:`~easymode.tree.admin.relation.InvisibleModelAdmin`, and then it would
    also not be shown in the admin app list.
    
    .. attribute:: parent_link
        
        To have sane breadcrumbs if the :class:`~easymode.tree.admin.abstract.LinkedItemAdmin`
        is used as child of another :class:`~easymode.tree.admin.abstract.LinkedItemAdmin`
        and make the save button return to the parent instead of the app listing, the
        ``parent_link`` should be set.
        
        It must be set to the *name* of the ``ForeignKey`` that points to the parent.
    
    """
    change_form_template = 'tree/admin/change_form_with_parent_link.html'
    
    def change_view(self, request, object_id, extra_context=None):
        
        # retrieve link to parent for breadcrumb path
        defaults = self._get_parent_link(object_id)
        
        if extra_context:
            defaults.update(extra_context)
        
        response = super(LinkedItemAdmin, self).change_view(request, object_id, defaults)
        
        if response.get('Location', False) == '../':
            return HttpResponseRedirect(defaults.get('parent_model', '../'))
        
        return response
    
    class Media:
        js = (
            'easymode/js/adminoverride.js',
        )
    
    