from django import http
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist

from easymode.utils.languagecode import fix_language_code

@staff_member_required
def preview(request, content_type_id, object_id):
    """
    This is an override for django.views.default.shortcut.
    It assumes that get_absolute_url returns an absolute url, so
    it does not do any of the very elaborate link checking that shortcut does.
    
    This version adds the language code to the url. (/en/blaat/).
    """
    
    try:
        content_type = ContentType.objects.get(pk=content_type_id)
        obj = content_type.get_object_for_this_type(pk=object_id)
    except ObjectDoesNotExist:
        raise http.Http404("Content type %s object %s doesn't exist" % (content_type_id, object_id))
    try:
        absolute_url = obj.get_absolute_url(format='flash')
    except AttributeError:
        raise http.Http404("%s objects don't have get_absolute_url() methods" % content_type.name)
        
    if absolute_url.startswith('http://') or absolute_url.startswith('https://'):        
        http.HttpResponseRedirect(absolute_url)        
    else:
        absolute_url = fix_language_code("/%s" % absolute_url, request.LANGUAGE_CODE)                
        return http.HttpResponseRedirect(absolute_url)