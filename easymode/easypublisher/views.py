from django.contrib.admin.views.decorators import staff_member_required

from easymode.utils import url_add_params
from easymode.views import preview


@staff_member_required
def preview_draft(request, content_type_id, object_id, revision_id):
    response = preview(request, content_type_id, object_id)
    response['Location'] = url_add_params(response['Location'], preview=revision_id)
    return response
