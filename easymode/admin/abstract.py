from django.db import models

class AbstractOrderedModel(models.Model):    
    """
    This model includes functionality for ordering.
    """
    order = models.AutoField()
            
    class Meta:
        abstract = True
        ordering = ('order',)
    


    

        