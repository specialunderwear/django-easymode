"""
Generic django admin extensions.
"""

from django.contrib import admin

__all__ = ('DragAndDropAdmin', 'abstract', 'fields', 'forms', 'models', 'utils')

class DragAndDropAdmin(admin.ModelAdmin):
    """
    Admin class that allows dragging and dropping of items
    in the admin listing.
    
    Go to http://jqueryui.com/download, deselect all and then select sortable.
    Download the js and include it in the Media of your derived class::
        
        class Media:
            js = (
                'js/jquery-ui-1.8.14.custom.js',
            )
    
    Also make sure jquery itself is loaded.
    """
    ordering = ('order',)
    list_display = ('id', 'order')
    list_editable = ('order',)
    
    class Media:
        js = (
            'easymode/js/menu-sort.js',            
        )
        
        
