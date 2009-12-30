#!/usr/bin/env python
# encoding: utf-8

"""
Module providing functions commonly used in shell scripting; requires
Python 2.5

The functions are as follows:

  - ffind(): finds files in a directory tree
  - ffindgrep(): finds files in a directory tree and matches their
    content to regular expressions
  - freplace(): in-place search/replace of files in a directory tree
    with regular expressions
  - printr(): prints the results of the ffind()/ffindgrep() functions

Please see the documentation strings of the particular functions for
detailed information.
"""

# Copyright: (c) 2007 Muharem Hrnjadovic
# created: 15/04/2007 09:31:25

__version__ = "$Id:$"
# $HeadURL $

import os, sys, types, re, functools

class ScriptError(Exception): pass

def ffind(path, namefs=None, relative=True):
    """
    Finds files in the directory tree starting at 'path' (filtered by the
    functions in the optional 'namefs' sequence); if the 'relative'
    flag is not set, the result sequence will contain absolute paths.

    Returns a sequence of paths for files found.
    """
    if not os.access(path, os.R_OK):
        raise ScriptError("cannot access path: '%s'" % path)

    fileList = [] # temporary files list
    try:
        for dir, subdirs, files in os.walk(path):
            fileList.extend('%s%s%s' % (dir, os.sep, f) for f in files)
        if not relative: fileList = map(os.path.abspath, fileList)
        if namefs:
            for ff in namefs: fileList = filter(ff, fileList)
    except Exception, e: raise ScriptError(str(e))
    return(fileList)

def ffindgrep(path, regexl, namefs=None, relative=True):
    """
    Finds files in the directory tree starting at 'path' (filtered by the
    functions in the optional 'namefs' sequence); if the 'relative'
    flag is not set, the result sequence will contain absolute paths.

    Additionaly, the file content will be filtered by the regular
    expressions in the 'regexl' sequence. Each entry in the latter
    is a
    
      - either a string (with the regex definition)
      - or a tuple with arguments accepted by re.compile() (the
        re.M and re.S flags will have no effect though)

    For all the files that pass the file name/content tests the function
    returns a dictionary where the

      - key is the file name and the
      - value is a string with lines filtered by 'regexl'
    """
    fileList = ffind(path, namefs=namefs, relative=relative)
    if not fileList: return dict()

    result = dict()

    try:
        # first compile the regular expressions
        ffuncs = []
        for redata in regexl:
            if type(redata) == types.StringType:
                ffuncs.append(re.compile(redata).search)
            elif type(redata) == types.TupleType:
                ffuncs.append(re.compile(*redata).search)
        # now grep in the files found
        for file in fileList:
            # read file content
            fhandle = open(file, 'r')
            fcontent = fhandle.read()
            fhandle.close()
            # split file content in lines
            lines = fcontent.splitlines()
            for ff in ffuncs:
                lines = filter(ff, lines)
                # there's no point in applying the remaining regular
                # expressions if we don't have any matching lines any more
                if not lines: break
            else:
                # the loop terminated normally; add this file to the
                # result set if there are any lines that matched
                if lines: result[file] = '\n'.join(map(str, lines))
    except Exception, e: raise ScriptError(str(e))
    return(result)

def freplace(path, regexl, namefs=None, bext='.bak'):
    """
    In-place search/replace of the content of all files (whose names
    pass the optional tests specified in 'namefs') in the directory
    tree starting with 'path' using the regular expressions in 'regexl'.

    Please note: 'regexl' is a sequence of 3-tuples, each having the
    following elements:

      - search string (Python regex syntax)
      - replace string (Python regex syntax)
      - regex flags or 'None' (re.compile syntax)

    Copies of the modified files are saved in backup files using the
    extension specified in 'bext'.

    The function returns the total number of files modified.
    """
    fileList = ffind(path, namefs=namefs)
    if not fileList: return 0

    filesChanged = 0
    cffl = []

    try:
        for searchs, replaces, reflags in regexl:
            if reflags is not None: regex = re.compile(searchs, reflags)
            else: regex = re.compile(searchs)
            # curry the regex.subn() function to supply the first
            # argument (the replacement string)
            cffl.append(functools.partial(regex.subn, replaces))
        for file in fileList:
            # read file content
            fhandle = open(file, 'r')
            text = fhandle.read()
            fhandle.close()
            substitutions = 0
            for cff in cffl:
                text, numOfChanges = cff(text)
                substitutions += numOfChanges
            if substitutions:
                # first move away the original file
                bakFileName = '%s%s' % (file, bext)
                if os.path.exists(bakFileName): os.unlink(bakFileName)
                os.rename(file, bakFileName)
                # now write the new file content
                fhandle = open(file, 'w')
                fhandle.write(text)
                fhandle.close()
                filesChanged += 1
    except Exception, e: raise ScriptError(str(e))

    # return the number of files that had some of their content changed
    return(filesChanged)

def printr(results):
    """
    prints the results of ffind()/ffindgrep() in a manner similar to
    the UNIX find utility
    """
    if type(results) == types.DictType:
        for f in sorted(results.keys()):
            sys.stdout.write("%s\n%s\n" % (results[f],f))
    else:
        for f in sorted(results):
            sys.stdout.write("%s\n" % f)

if __name__ == '__main__':
    pass

