from django.utils.text import capfirst

_defined_standins = dict()

class BoolStandin(int):
    def __nonzero__(self):
        return self != 0
    def __repr__(self):
        if self == 0:
            return 'False'
        else:
            return 'True'

def standin_for(obj, **attrs):
    """
    Returns an object that can be used as a standin for the original object.
    
    The standin object will have extra attrs, which you can define passed as keyword arguments.
    
    This will be used in the __future__ to pass info about the origin of a value to
    a widget. The origin of a value can either be the database or the gettext catalog.
    You will be able to change the origin. This is very usefull if for example you
    saved a model without realising all fields will be committed to the database and
    you made changes to the gettext catalog afterwards.
    
    See :ref:`database_rules_all`
    """
    
    obj_class = obj.__class__
    if obj_class is bool:
        obj_class = BoolStandin
    
    attr_names  = attrs.keys()
    attr_names.sort()

    # create a readable class name eg. unicodeAndTitleAndDescription
    additions = 'And'.join(map(capfirst, attr_names))
    id = "%s%s" % (obj_class.__name__, additions.encode('ascii', 'ignore'))
    
    # if we allready know this type don't create it again.
    cached_type = _defined_standins.get(id, None)
    if not cached_type:
        cls_attrs = dict([(attr_name, None) for attr_name in attr_names])
        cached_type = type("%sStandIn" % id, (obj_class,), cls_attrs)
        _defined_standins[id] = cached_type
    
    # create new object based on original and add extra attrs.
    stand_in = cached_type(obj)
    for (key, value) in attrs.iteritems():
        setattr(stand_in, key, value)
    
    return stand_in