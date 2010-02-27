import types

try:
    from rosetta import polib
except ImportError:
    import polib

def po_to_unicode(po_obj):
    po_text = po_obj.__str__()
    if type(po_text) != types.UnicodeType:
        po_text = po_text.decode('utf-8')
    
    return po_text
    
class PoStream(polib._POFileParser):
    """
    Create a POFile object from a StringIO::
    
    >>> import codecs
    >>> from StringIO import StringIO
    >>> 
    >>> po_string = codecs.open('sompofile.po', 'r', 'utf-8').read()
    >>> po_file_from_string = PoStream(None, StringIO(po_string)).parse()
    >>> 
    >>> unicode(po_file_from_string)
    
    """
    
    def __init__(self, stream, fpath=None, encoding='utf-8', wrapwidth=78):
        """a pofileparser that can read from a stream"""
        self.fhandle = stream
        self.instance = polib.POFile(fpath=fpath, encoding=encoding)
        self.instance.wrapwidth = wrapwidth
        self.transitions = {}
        self.current_entry = polib.POEntry()
        self.current_state = 'ST'
        self.current_token = None
        self.msgstr_index = 0
        self.entry_obsolete = 0
        all_ = ['ST', 'HE', 'GC', 'OC', 'FL', 'TC', 'MS', 'MP', 'MX', 'MI']

        self.add('TC', ['ST', 'HE'],                                     'HE')
        self.add('TC', ['GC', 'OC', 'FL', 'TC', 'MS', 'MP', 'MX', 'MI'], 'TC')
        self.add('GC', all_,                                             'GC')
        self.add('OC', all_,                                             'OC')
        self.add('FL', all_,                                             'FL')
        self.add('MI', ['ST', 'HE', 'GC', 'OC', 'FL', 'TC', 'MS', 'MX'], 'MI')
        self.add('MP', ['TC', 'GC', 'MI'],                               'MP')
        self.add('MS', ['MI', 'MP', 'TC'],                               'MS')
        self.add('MX', ['MI', 'MX', 'MP', 'TC'],                         'MX')
        self.add('MC', ['MI', 'MP', 'MS', 'MX'],                         'MC')
