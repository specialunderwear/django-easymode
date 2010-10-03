from types import NoneType
from django.utils.text import capfirst

__all__ = ('standin_for',)

_defined_standins = dict()
    
def standin_for(obj, **attrs):
    """
    Returns an object that can be used as a standin for the original object.
    
    The standin object will have extra attrs, which you can define passed as keyword arguments.
    
    Use standin like this:
    
    >>> a = u'I am E.T.'
    >>> b = standin_for(a, origin='outerspace', package='easymode.utils.standin')
    >>> b
    u'I am E.T.'
    >>> b == a
    True
    >>> b.origin
    'outerspace'
    >>> b.package
    'easymode.utils.standin'
    >>> isinstance(b, unicode)
    True
    >>> type(b)
    <class 'easymode.utils.standin.unicodeStandInWithOriginAndPackageAttributes'>
    >>> import pickle
    >>> b_pickle = pickle.dumps(b, pickle.HIGHEST_PROTOCOL)
    >>> c = pickle.loads(b_pickle)
    >>> b == c
    True
    >>> c
    u'I am E.T.'
    >>> c.origin
    'outerspace'
    >>> c.package
    'easymode.utils.standin'
    
    Some types are not supported by standin_for. This is because these types are often used in statements like::
        
        a = True
        if a is True:
            print 'hi'
    
    The *is* keyword checks for equal memory adress, and in case of a standin that can never be *True*.
    Also, since it is impossible to extend :class:`bool` and :class:`~types.NoneType` you can never get::
    
        isinstance(standin, bool)
        isinstance(standin, NoneType)
    
    To work with anything else but the real thing.
    This is why :class:`bool` and :class:`~types.NoneType` instances are returned unmodified:
    
    >>> a = False
    >>> b = standin_for(a, crazy=True)
    >>> b
    False
    >>> b.crazy
    Traceback (most recent call last):
        ...
    AttributeError: 'bool' object has no attribute 'crazy'
        
    :param obj: An instance of some class
    :param **attrs: Attributes that will be added to the standin for *obj*
    :rtype: A new object that can be used where the original was used. However it has extra attributes.
    """
    
    obj_class = obj.__class__
    if obj_class is bool or obj_class is NoneType:
        # we can not have a standing for bool or NoneType
        # because too many code uses a is True or a is None.
        # Also you can never get isinstance(standin, bool) and
        # isinstance(standin, NoneType) to work because you can
        # never extend these types.
        return obj
    
    attr_names  = attrs.keys()
    attr_names.sort()

    # Contruct __reduce__ method, so the resulting class can be pickled
    attrs_org = attrs.copy() # Create a copy to be used for the recude method
    def __reduce__(self, ignore=None):
        return (_standin_with_dict_for, (obj, attrs_org))
    attrs['__reduce__'] = __reduce__
    attrs['__reduce_ex__']= __reduce__

    # create a readable class name eg. unicodeStandinWithTitleAndDescriptionAttributes
    additions = 'And'.join(map(capfirst, attr_names))
    id = "%sStandInWith%sAttributes" % (obj_class.__name__, additions.encode('ascii', 'ignore'))
    
    # if we allready know this type don't create it again.
    cached_type = _defined_standins.get(id, None)
    if not cached_type:
        cls_attrs = dict([(attr_name, None) for attr_name in attr_names])
        cached_type = type(id, (obj_class,), cls_attrs)
        _defined_standins[id] = cached_type
    
    # create new object based on original and copy all properties
    try:
        stand_in = cached_type(obj)
    except (AttributeError, TypeError):
        try:
            stand_in = cached_type()
            stand_in.__dict__.update(obj.__dict__)
        except (AttributeError, TypeError):
            stand_in = obj

    # add extra attrs
    try:
        for (key, value) in attrs.iteritems():
            setattr(stand_in, key, value)
    except AttributeError:
        # if nothing works return original object
        return obj
    
    return stand_in
    
def _standin_with_dict_for(obj, attrs):
    return standin_for(obj, **attrs)