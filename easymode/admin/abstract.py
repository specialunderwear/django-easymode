from django.utils.translation import ugettext_lazy as _
from django.db import models

class AbstractOrderedModel(models.Model):
    """
    This model includes functionality for ordering.
    """
    
    order = models.PositiveIntegerField(_('Order'), default=99999999)
    
    def save(self, force_insert=False, force_update=False):
        # this is the last model in the list except if there are 10000000 models.
        self.order = 99999999
        super(AbstractOrderedModel, self).save(False, False)
        
    class Meta:
        abstract = True
        ordering = ('order',)