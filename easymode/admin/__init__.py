"""
Generic django admin extensions.
"""

from django.contrib import admin

class DragAndDropAdmin(admin.ModelAdmin):
    """
    Admin class that allows dragging and dropping of items
    in the admin listing.
    """
    ordering = ('order',)
    list_display = ('id', 'order')
    list_editable = ('order',)
    
    class Media:
        js = (
            'js/lib/jquery.js',
            'js/lib/ui.core.js',
            'js/lib/ui.sortable.js',
            'easymode/js/menu-sort.js',            
        )
        
        
