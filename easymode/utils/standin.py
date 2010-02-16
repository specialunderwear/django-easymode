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
    Returns a type that can be used as a standin for some other type.
    
    However it will have extra attrs, which you can define passed as keyword arguments.
    """
    base_type = obj.__class__
    if base_type is bool:
        base_type = BoolStandin
    
    attr_names  = attrs.keys()
    attr_names.sort()

    additions = 'And'.join(map(capfirst, attr_names))
    id = "%s%s" % (base_type.__name__, additions.encode('ascii', 'ignore'))
    
    cached_type = _defined_standins.get(id, None)
    if not cached_type:
        cls_attrs = dict([(attr_name, None) for attr_name in attr_names])
        cached_type = type("%sStandIn" % id, (base_type,), cls_attrs)
        _defined_standins[id] = cached_type
    
    stand_in = cached_type(obj)
    for (key, value) in attrs.iteritems():
        setattr(stand_in, key, value)
    
    return stand_in