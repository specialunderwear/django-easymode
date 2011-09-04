from django.contrib import admin
from django.http import HttpResponseRedirect

from easymode.tree.admin.forms import RecursiveInlineFormSet
from easymode.tree.admin.relation import _CanFindParentLink

__all__ = ('LinkInline', 'LinkedItemAdmin')

class LinkInline(admin.StackedInline):
    formset = RecursiveInlineFormSet
    template = 'tree/admin/edit_inline/link_inline.html'
    extra = 1

class LinkedItemAdmin(admin.ModelAdmin, _CanFindParentLink):
    
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
    
    