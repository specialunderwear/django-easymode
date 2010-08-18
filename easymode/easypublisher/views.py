from django.contrib.admin.views.decorators import staff_member_required

from easymode.utils import url_add_params
from easymode.views import preview


@staff_member_required
def preview_draft(request, content_type_id, object_id, revision_id):
    """
    A shortcut view that redirects to the absolute url of the object that the
    *content_type_id* and *object_id* define uniquely. An extra parameter is added
    to this absolute url;
    
    ?preview=*revision_id*
    
    Which can be used to show the data which is in revision *revision_id* in your
    view instead of the regular data.
    """
    response = preview(request, content_type_id, object_id)
    response['Location'] = url_add_params(response['Location'], preview=revision_id)
    return response
