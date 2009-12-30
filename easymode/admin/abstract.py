from django.db import models

class AbstractOrderedModel(models.Model):    
    """
    This model includes functionality for ordering.
    """
    order = models.PositiveIntegerField()
    
    def save(self, force_insert=False, force_update=False):
        # this is the last model in the list except if there are 10000000 models.
        order = 99999999
        super(AbstractOrderedModel, self).save(False, False)
        
    class Meta:
        abstract = True
        ordering = ('order',)
    


    

        