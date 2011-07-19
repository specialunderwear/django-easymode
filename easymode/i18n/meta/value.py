"""
Value objects used by easymode's i18n.meta package.
"""
class GettextVO:
    """
    A value object that contains information about the origin
    of the value in question.
    
    .. attribute:: standin_value_is_from_database

        is True if the value came from the database

    .. attribute:: msgid
    
        The message id that originated the lookup

    .. attribute:: msg
        
        The message that is the result of the lookup
    
    .. attribute:: fallback
    
        the fallback that was found during the lookup
    
    .. attribute:: stored_value
        
        the value as it is stored in the database
    
    """
    
    def __init__(self):
        self.standin_value_is_from_database = False
        self.msgid = None
        self.msg = None
        self.fallback = None
        self.stored_value = None
