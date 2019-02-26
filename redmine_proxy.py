import requests
import pickle
import socket
import select
import threading

class BaseProtocol():
    def __init__(self, socket):
        self.sock = socket
        self.wfile = socket.makefile("wb")
        self.rfile = socket.makefile("rb")

    def _send(self, message, payload=None):
        obj = (message, payload)
        try:
            pickle.dump(obj, self.wfile)
            self.wfile.flush()
        except OSError:
            print("Error occurred sending response to %s"%repr(self.sock.getpeername()))

    def _recv(self):
        r, w, l = select.select([self.sock], [], [], 30)
        if r:
            msg, data = pickle.load(self.rfile)
        else:
            msg, data = "TIMEOUT", None
        return msg, data

    def close(self):
        if self.wfile:
            self.wfile.flush()
            self.wfile.close()
            self.wfile = None
        if self.rfile:   
            self.rfile.flush()
            self.rfile.close()
            self.rfile = None
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()


class ServerProtocol(BaseProtocol):
    def __init__(self, socket, sess, cache, lock):
        super().__init__(socket)
        self.sess = sess
        self.cache = cache
        self.lock = lock

    def get(self, url, kw):
        kws = " ".join('%r=%r'%i for i in kw.items())
        key = (url, kws)
        with self.lock:
            if key in self.cache:
                print("returning cached value for '%s'"%(repr(url)))
                return self.cache[key]
        print('requesting new value for "%s"'%(repr(key)))
        timeout = kw.pop('timeout', 40)
        rsp = self.sess.get(url, timeout=timeout, **kw)
        rsp.content  # trigger actual read
        with self.lock:
            self.cache[key] = rsp
        return "SUCCESS", rsp

    def process(self):
        msg, data = self._recv()
        if msg == "GET_URL":
            url, kw = data
            msg, rsp = self.get(url, kw)
            self._send(msg, rsp)
        elif msg == "CLEAR_CACHE":
            with self.lock:
                self.cache.clear()
            print("cleared internal cache")
            self._send("SUCCESS", "CLEAR_CACHE")
        else:
            self._send("UNKN_CMD", msg)

class ClientProtocol(BaseProtocol):

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self._init()

    def _init(self):
        self.close()
        sock = socket.socket()
        sock.connect((self.host, self.port))
        super().__init__(sock)

    def clear_cache(self):
        self._send("CLEAR_CACHE", None)
        msg, rsp = self._recv()
        if msg != "SUCCESS":
            raise ValueError(rsp)

    def get(self, url, **kw):
        self._send("GET_URL", (url, kw))
        rsp, data = self._recv()
        if rsp == "SUCCESS":
            return data
        elif rsp == "ERR_RAISE_EXC":
            raise data
        else:
            raise ValueError("Unknown result returned: (%r, %r)"%(rsp, data))


class HandleIt(threading.Thread):
    def __init__(self, sock, cache, sess, lock):
        super().__init__(daemon=True)
        self.sock = sock
        self.cache = cache
        self.sess = sess
        self.lock = lock
        self.start()

    def run(self):
        proto = ServerProtocol(self.sock, self.sess, self.cache, self.lock)
        proto.process()
        proto.close()

class Server():
    def __init__(self, host, port=0):
        self.serv = socket.socket()
        self.serv.bind((host, port))
        self.serv.listen(20)
        self.cache = {}
        self.sess = requests.Session()
        self.running = False
        self.lock = threading.Lock()

    def mainloop(self):
        self.running = True
        while self.running:
            rl, wl, xl = select.select([self.serv], [], [], 0.1)
            client, addr = self.serv.accept()
            print("Got connection from %r"%str(addr))
            HandleIt(client, self.cache, self.sess, self.lock)

    def stop(self):
        self.running = False

def main():
    print("Initializing server at (%r, %r)"%("localhost", 9876))
    s = Server("localhost", 9876)
    s.mainloop()

if __name__ == "__main__":
    try:
        main()
    except Exception:
        input()