from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

PUBLICATION_STATUSSES = (
    ('published', _('Published')),
    ('draft', _('Draft')),
    ('needs_work', _('Needs work')),
    ('updated', _('Updated')),
)

class EasyPublisherMetaData(models.Model):
    """
    A model for adding metadata to a reversion version.
    """
    
    class Meta:
        permissions = (('can_approve_for_publication', 'Can approve for publication'),)
    
    revision = models.ForeignKey("reversion.Revision")
    status = models.CharField(_('Publication Status'), max_length=10, choices=PUBLICATION_STATUSSES, default='draft')
    language = models.CharField(_('Language'), max_length=5, choices=settings.LANGUAGES, default=settings.LANGUAGE_CODE)
    
    def __unicode__(self):
        return u"revision: %s status: %s language: %s" % (self.revision, self.status, self.language)
    