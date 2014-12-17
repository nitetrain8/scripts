# from os import startfile
# from os.path import exists
# from subprocess import Popen
from urllib.request import urlopen
from officelib.nsdbg import npp_open
from pysrc.snippets import unique_name


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


def init_hello_server():
    from hello.mock.server import HelloServer
    from threading import Thread
    global s, t
    s = HelloServer()
    t = Thread(None, s.serve_forever)
    t.daemon = True
    t.start()
