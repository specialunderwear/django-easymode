from django import template
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

from reversion.models import Revision

from easymode.utils.languagecode import strip_language_code

register = template.Library()

#todo admin site is hardcoded, should get current admin name from somewhere
@register.tag
def draft_list_items(parser, token):
    """displays a list of all drafts, without the enclosing <ul>"""
    return DraftListItems()

class DraftListItems(template.Node):
    def render(self, context):
        request = context['request']

        #select revisions
        revisions = Revision.objects.filter(
            easypublishermetadata__status='draft',
            easypublishermetadata__language=request.LANGUAGE_CODE
        ).select_related().distinct()
    
        output = u''
        for revision in revisions:
            # select version and make list item
            version = revision.version_set.all().order_by('revision')[0]
            opts = version.content_type.model_class()._meta
            info = opts.app_label, opts.module_name
            name = 'admin:%s_%s_draft' % info
            url = reverse(name, args=[version.object_id, version.id])
            url = strip_language_code(url)
            output += u"<li><a href=\"%s\">%s</a></li>" % (url, version.object_repr)
    
        return mark_safe(output)
