"""
Overrides django's subclassing.py because it breaks everything when trying to inspect
the model objects with inspect. This is because subclassing.Creator throws an exception
when it is accesses with no context. It SHOULD return the descriptor object
instead. And now it does.
"""
from django.db.models.fields.subclassing import LegacyConnection

class SubfieldBaseFix(LegacyConnection):
    """
    A metaclass for custom Field subclasses. This ensures the model's attribute
    has the descriptor protocol attached to it.

    MONKEYPATCHED by easymode
    
    The original SubfieldBase throws an exception when it's descriptor is accesses 
    with no context. It SHOULD return the descriptor object instead. And now it does.
    """
    def __new__(cls, base, name, attrs):
        new_class = super(SubfieldBaseFix, cls).__new__(cls, base, name, attrs)
        new_class.contribute_to_class = make_contrib(
                attrs.get('contribute_to_class'))
        return new_class

class CreatorFix(object):
    """
    A placeholder class that provides a way to set the attribute on the model.
    
    MONKEYPATCHED by easymode
    
    The original Creator throws an exception when it is accesses with no 
    context. It SHOULD return the descriptor object instead. And now it does.
    """
    def __init__(self, field):
        self.field = field

    def __get__(self, obj, typ=None):
        if obj is None:
            return self
        return obj.__dict__[self.field.name]        

    def __set__(self, obj, value):
        obj.__dict__[self.field.name] = self.field.to_python(value)

def make_contrib(func=None):
    """
    Returns a suitable contribute_to_class() method for the Field subclass.

    If 'func' is passed in, it is the existing contribute_to_class() method on
    the subclass and it is called before anything else. It is assumed in this
    case that the existing contribute_to_class() calls all the necessary
    superclass methods.
    """
    def contribute_to_class(self, cls, name):
        if func:
            func(self, cls, name)
        else:
            super(self.__class__, self).contribute_to_class(cls, name)
        setattr(cls, self.name, CreatorFix(self))

    return contribute_to_class
