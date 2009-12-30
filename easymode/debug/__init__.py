from StringIO import StringIO
import inspect

def stack_trace(depth=None):
    """returns a stack trace"""
    frames = inspect.stack()[2:]
    if depth:
        frames = frames[:depth]
        
    result = StringIO()
    result.write("----------------------------------------------------\n")
    for (frame, file, line, context, code, status) in frames:
        result.write("In %s from %s\n%s %s" % (context, file, line, "\n".join(code)))
        result.write("----------------------------------------------------\n")        
    return result.getvalue()
