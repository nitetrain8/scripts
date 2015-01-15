# from os import startfile
# from os.path import exists
# from subprocess import Popen
from urllib.request import urlopen
from officelib.nsdbg import npp_open
from pysrc.snippets import unique_name
import sys


ipv4 = '192.168.1.6:80'


def getcall(call, auto=True, **params):
    query = "?&call=%s" % call
    if params:
        query = query + "&" + "&".join("%s=%s" % (k, v) for k, v in params.items())

    if 'json' in params:
        js = params['json']
        if isinstance(js, str):
            js = js.lower()
        if js in {'1', "True", 1, True, 'true'}:
            json = True
        else:
            json = False
    else:
        json = False

    rsp = urlopen(("http://%s/webservice/interface/" % ipv4) + query)
    txt = rsp.read()
    if not auto:
        fname = "C:\\.replcache\\paste%s.txt" % call
    else:
        path = "C:\\Users\\PBS Biotech\\Documents\\Personal\\PBS_Office\\MSOffice\\hello\\test\\test_input\\"
        if json:
            ext = ".json"
        else:
            ext = ".xml"
        fname = path + call + ext

    fname = unique_name(fname)

    with open(fname, 'wb') as f:
        f.write(txt)

    npp_open(fname)


from collections import OrderedDict


class FTest():
    def __init__(self, call):
        self.call = call
        self.fns = []

    def add_fn(self, params, raw_name=None, json=False):
        self.fns.append((params, raw_name, json))

    def write(self, f):

        cdef = """class Test%s(HelloServerTestBase, unittest.TestCase):
        """ % self.call

        f.write(cdef)

        for i, (params, raw_name, json) in enumerate(self.fns, 1):
            s = self.fn_to_str(params, raw_name, i, json)
            f.write(s)
        f.write("\n\n")

    def fn_to_str(self, params, raw_name, nfn=1, json=False):
        fn = """
    def test_%(name)s%(n)d(self):

        call = "%(call)s"
        params = (
            %(pstr)s
        )

        self.do_call_expect_%(json)s(call, params, %(raw_name)s)
        """

        pstr = "\n            ".join("""("%s", "%s"),""" % i for i in params.items())

        return fn % {
            'name': self.call,
            'raw_name': raw_name,
            'n': nfn,
            'call': self.call,
            'pstr': pstr,
            'json': 'json' if json else 'xml'
        }


class CallGetter():

    """Create an instance to collect a series of calls to a hello server
    and collect responses. Responses written to the test input directory for
    hello server. Call getcall() to save a call. Instance also records history
    of all calls and sets of parameters passed to auto generate test code.
    Call dump(f) or dumps() to write the generated code to a file or string."""

    def __init__(self, ipv4=ipv4, file_path=None):
        self.ipv4 = ipv4
        self.calls = OrderedDict()
        if file_path is None:
            self.file_path = "C:\\Users\\PBS Biotech\\Documents\\Personal\\" \
                             "PBS_Office\\MSOffice\\hello\\test\\test_input\\"
        else:
            self.file_path = file_path

    def getcall(self, call, **params):

        if call in self.calls:
            t = self.calls[call]
        else:
            self.calls[call] = t = FTest(call)

        query = "?&call=%s" % call
        if params:
            query = query + "&" + "&".join("%s=%s" % (k, v) for k, v in params.items())

        if 'json' in params:
            js = params['json']
            if isinstance(js, str):
                js = js.lower()
            if js in {'1', "True", 1, True, 'true'}:
                json = True
            else:
                json = False
        else:
            json = False

        assert isinstance(t, FTest)

        t.add_fn(params, None, json)

        rsp = urlopen(("http://%s/webservice/interface/" % self.ipv4) + query)
        txt = rsp.read()

        if json:
            ext = ".json"
        else:
            ext = ".xml"
        fname = self.file_path + call + ext

        with open(fname, 'wb') as f:
            f.write(txt)

    def getcall_with_text(self, call, txt, **params):

        if call in self.calls:
            t = self.calls[call]
        else:
            self.calls[call] = t = FTest(call)

        if 'json' in params:
            js = params['json']
            if isinstance(js, str):
                js = js.lower()
            if js in {'1', "True", 1, True, 'true'}:
                json = True
            else:
                json = False
        else:
            json = False

        assert isinstance(t, FTest)
        t.add_fn(params, None, json)

        if json:
            ext = ".json"
        else:
            ext = ".xml"
        fname = self.file_path + call + ext

        with open(fname, 'wb') as f:
            f.write(txt)

    def dump(self, f):
        for c in self.calls.values():
            c.write(f)

    def dumps(self):
        from io import StringIO
        b = StringIO()
        self.dump(b)
        return b.getvalue()


def init_hello_server():
    from hello.mock.server import HelloServer, HelloHTTPHandler
    from threading import Thread
    global s, t
    s = HelloServer()
    HelloHTTPHandler.allow_json = True
    t = Thread(None, s.serve_forever, None, (0.1,))
    t.daemon = True
    t.start()


def test():
    from os.path import dirname, join, exists

    tpath = join(dirname(__file__), "\\getcall\\")

    if not exists(tpath):
        import os
        os.makedirs(tpath)

    init_hello_server()
    getter = CallGetter('localhost:12345', tpath)
    getter.getcall('login', val1='user1', val2=12345)
    getter.getcall('login', val1='pbstech', val2=727246)
    getter.getcall("getmainvalues", json=True)
    getter.getcall("getmaininfo", json=True)
    import sys
    with open(r"C:\Users\PBS Biotech\Documents\Personal\PBS_Office\MSOffice\scripts\cli_data\foo.py", 'w') as f:
        getter.dump(f)
    getter.dump(sys.stdout)


if __name__ == '__main__':
    test()
