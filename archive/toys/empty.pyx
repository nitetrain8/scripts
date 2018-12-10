
cdef class A:
    pass

cdef class Empty:
    def __init__(self):
        pass
    cpdef dummy(self, int a, double b, char *c, A d):
        return a + b

