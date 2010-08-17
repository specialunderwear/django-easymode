from django.utils.translation import ugettext_lazy as _
from django.db import models

class AbstractOrderedModel(models.Model):
    """
    This model includes functionality for ordering.
    """
    
    order = models.PositiveIntegerField(_('Order'), default=99999999)
    
    class Meta:
        abstract = True
        ordering = ('order',)