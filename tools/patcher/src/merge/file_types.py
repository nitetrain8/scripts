"""
Originally I was going to use this file to allow modules
to dynamically load themselves, so that the main file
(merge.py) would never have to be updated for new handlers,
but i realized that I'd have to write a loader that searched
for modules to load and import at runtime, so this file could
really just be part of merge.py but oh well. 
"""


_file_types = {}

def register(type, function):
    """ Register a function as a handler for 
    a type specified in a patch file. 
    `function` must accept a single argument of type Options.
    """
    _file_types[type] = function


def load_function(type):
    return _file_types[type]


def get_types():
    return list(_file_types)