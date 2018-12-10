"""

Created by: Nathan Starkweather
Created on: 04/04/2016
Created in: PyCharm Community Edition


"""
__author__ = 'Nathan Starkweather'

import logging

logger = logging.getLogger(__name__)
_h = logging.StreamHandler()
_f = logging.Formatter("%(created)s %(name)s %(levelname)s (%(lineno)s): %(message)s")
_h.setFormatter(_f)
logger.addHandler(_h)
logger.propagate = False
logger.setLevel(logging.DEBUG)
del _h, _f


ctypes = {}


def add_ctype(typ):
    assert typ not in ctypes
    ctypes[typ] = CType(typ)


class CType():
    """ Basic C Type"""
    def __init__(self, typ, const=False, modifiers=None, includes=None):
        self.modifiers = modifiers
        self.const = const
        self.includes = includes
        self._typ = typ
        add_ctype(self)

    def write(self, f):
        f.write(self._typ)

    def __call__(self, const=False):
        pass


class CInt(CType):
    """ C integer types. """
    def __init__(self, typ, byts, signed, includes=None):
        if typ is None:
            typ = "%sint%d_t" % ("" if signed else "u", byts * 8)
        super().__init__(typ, includes)
        self._bytes = byts
        self.signed = signed


class CStruct(CType):
    def __init__(self, name, fields=(), includes=None):
        """ C Structure. Fields defaults to empty, representing
        an opaque type.
        """
        super().__init__(name, includes)
        self.fields = fields


void = CType("void")


int8_t = CInt("int8_t", 1, True, "<stdint.h>")
int16_t = CInt("int16_t", 2, True, "<stdint.h>")
int32_t = CInt('int32_t', 4, True, "<stdint.h>")
int64_t = CInt('int64_t', 8, True, "<stdint.h>")
uint8_t = CInt("uint8_t", 1, False, "<stdint.h>")
uint16_t = CInt("uint16_t", 2, False, "<stdint.h>")
uint32_t = CInt('uint32_t', 4, False, "<stdint.h>")
uint64_t = CInt('uint64_t', 8, False, "<stdint.h>")

char = int8_t
uchar = uint8_t

PyObject = CStruct('PyObject', ())


class CPointer(CType):
    def __init__(self, pointee, level=1):
        typ = "%s %s" % (pointee, "*"*level)
        super().__init__(typ)


class CompleteType():
    def __init__(self, basetyp, modifiers=()):
        self.basetyp = basetyp
        self.modifiers = modifiers


class CVar():
    def __init__(self, typ, name):
        self.typ = typ
        self.name = name


class FuncSig():
    def __init__(self, name, rtype, *args):
        self.name = name
        self.rtype = rtype
        if args is None:
            args = [void]
        self.args = args

    def write(self, f, proto=False):
        w = f.write
        w(self.rtype)
        w(" ")
        w(self.name)
        w("(")
        w(", ".join(self.args))
        w(")")
        if proto:
            w(";")


class Function():
    def __init__(self, sig):
        self.sig = sig

    def write(self, f):
        self.sig.write(f)


tps = [
    "tp_name",
    "tp_itemsize",
    "tp_basicsize",
    "tp_dealloc",
    "tp_print",
    "tp_getattr",
    "tp_setattr",
    "tp_reserved",
    "tp_repr",
    "tp_as_number",
    "tp_as_sequence",
    "tp_as_mapping",
    "tp_hash",
    "tp_call",
    "tp_str",
    "tp_getattro",
    "tp_setattro",
    "tp_as_buffer",
    "tp_flags",
    "tp_doc",
    "tp_traverse",
    "tp_clear",
    "tp_richcompare",
    "tp_weaklistoffset",
    "tp_iter",
    "tp_iternext",
    "tp_methods",
    "tp_members",
    "tp_getset",
    "tp_base",
    "tp_dict",
    "tp_descr_get",
    "tp_descr_set",
    "tp_dictoffset",
    "tp_init",
    "tp_alloc",
    "tp_new",
    "tp_free",
    "tp_is_gc",
    "tp_bases",
    "tp_mro",
    "tp_cache",
    "tp_subclasses",
    "tp_weaklist",
    "tp_del",
    "tp_version_tag",
    "tp_finalize",
]

tps_empty_tmpl = "0,              /* %s */"
tps_empty = [tps_empty_tmpl % tp for tp in tps]
tps_empty_str = '\n'.join(tps_empty)

ex = """0,                   /* tp_name */
0,                   /* tp_itemsize */
0,                   /* tp_dealloc */
0,                   /* tp_print */
0,                   /* tp_getattr */
0,                   /* tp_setattr */
0,                   /* tp_reserved */
0,                   /* tp_repr */
0,                   /* tp_as_number */
0,                   /* tp_as_sequence */
0,                   /* tp_as_mapping */
0,                   /* tp_hash */
0,                   /* tp_call */
0,                   /* tp_str */
0,                   /* tp_getattro */
0,                   /* tp_setattro */
0,                   /* tp_as_buffer */
0,                   /* tp_flags */
0,                   /* tp_doc */
0,                   /* tp_traverse */
0,                   /* tp_clear */
0,                   /* tp_richcompare */
0,                   /* tp_weaklistoffset */
0,                   /* tp_iter */
0,                   /* tp_iternext */
0,                   /* tp_methods */
0,                   /* tp_members */
0,                   /* tp_getset */
0,                   /* tp_base */
0,                   /* tp_dict */
0,                   /* tp_descr_get */
0,                   /* tp_descr_set */
0,                   /* tp_dictoffset */
0,                   /* tp_init */
0,                   /* tp_alloc */
0,                   /* tp_new */
0,                   /* tp_free */
0,                   /* tp_is_gc */
0,                   /* tp_bases */
0,                   /* tp_mro */
0,                   /* tp_cache */
0,                   /* tp_subclasses */
0,                   /* tp_weaklist */
0,                   /* tp_del */
0,                   /* tp_version_tag */
0,                   /* tp_finalize */
"""



class ExtensionObject():
    def traverse(self, visit, arg):
        pass


class ExtensionType():
    def __new__(cls):
        pass

    def __init__(self):
        pass


if __name__ == '__main__':
    fs = FuncSig("printf", "char *", 'int32_t', 'char')
