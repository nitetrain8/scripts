import socket
import pickle
import select
import time

class ProxyError(OSError):
    pass

class ProxyTimeout(ProxyError):
    pass


class BaseProtocol():
    """ Mixin / common code for client & server side 
    protocols. 
    """
    SOCK_TIMEOUT = 30
    RECV_TIMEOUT = 30
    
    def __init__(self):
        self._queue = {}
        
    def _makefiles(self):
        self._wfile = self._sock.makefile("wb")
        self._rfile = self._sock.makefile("rb")
        self._sock.settimeout(self.SOCK_TIMEOUT)
    
    def close(self):
        if self._wfile:
            self._wfile.flush()
            self._wfile.close()
            self._wfile = None
        if self._rfile:
            self._rfile.close()
            self._rfile = None
            
        self._sock.shutdown(socket.SDRW)
        self._sock.close()
        self._sock = None
        
    def send(self, data):
        pickle.dump(data, self._wfile)
        self._wfile.flush()
        
    def recv_one_msg(self):
        r, w, x = select.select([self._sock], [], [], self.SOCK_TIMEOUT)
        if r:
            data = msg_load(self._rfile)
            if data.msg == "INTERNAL_ERROR":
                raise ProxyError("Internal error: '%s'"%data)
            return data
        else:
            raise ProxyTimeout("Socket read timeout")
        
    def recv(self, id, timeout=-1, hard_timeout=None):
        data = self._queue.pop(id, None)
        if data is not None:
            return data
        
        if timeout < 0:
            timeout = self.RECV_TIMEOUT
        end = time.time() + timeout
        
        if hard_timeout is not None:
            hard_end = max(end, time.time() + hard_timeout)
            
        while True:
            data = self.recv_one_msg()
            if data.msg == "HEARTBEAT":
                end = time.time() + timeout
                if end > hard_end:
                    end = hard_end
                continue
                
            if data.id != id:
                self._queue[data.id] = data
            else:
                return data

            if time.time() > end:
                raise ProxyTimeout("Took too long to get confirmation for result")

        
class MessageData():
    def __init__(self):
        self.id = None
        self.msg = None
        self.data = None
    
class MyUnpickler(pickle.Unpickler):

    def find_class(self, module, name):
        if module == "__main__" and name == "MessageData":
            return MessageData
        return super().find_class(module, name)

def msg_load(f):
    return MyUnpickler(f).load()
    
    
class ClientProtocol(BaseProtocol):
    _instance = 0
    def __new__(cls, *args, **kw):
        cls._instance += 1
        self = super().__new__(cls)
        self._instance = cls._instance
        return self
    
    def __init__(self, host, port, *, connect=True):
        super().__init__()
        self.host = host
        self.port = port
        self._connected = False
        
        self._sock = None
        self._wfile = None
        self._rfile = None
        
        if connect:
            self.connect()
            
        self._msg = 0
            
    def connect(self):
        if self._connected:
            self.close()
        self._sock = socket.socket()
        self._sock.connect((self.host, self.port))
        self._makefiles()
        
    def _new_message_data(self):
        m = MessageData()
        m.id = "%d.%d"%(self._instance, self._msg)
        self._msg += 1
        return m
        
    def call(self, fn, *args, **kw):
        data = self._new_message_data()
        data.msg = "CALL_FUNCTION"
        data.data = fn, args, kw
        self.send(data)
        rsp = self.recv(data.id)
        if rsp.msg != "CALL_FUNCTION_SUCCESS":
            if isinstance(rsp.data, Exception):
                raise rsp.data
            else:
                raise ProxyError("Function call failed: %s"%rsp.data)
        return rsp.data
    
    
class ServerProtocol(BaseProtocol):
    """ Server protocol starts differently because 
    the socket is created by an accept() call on a 
    server socket. 
    
    Also, notably, the object is a slave of the server
    protocol, whereas for the client the protocol is the
    slave of the object. 
    """
    def __init__(self, socket, obj):
        self.host, self.port = socket.getpeername()
        self._sock = socket
        self._wfile = self._rfile = None
        self._makefiles()
        self._obj = obj
        
    def process_one(self):
        try:
            data = self.recv_one_msg()
        except ProxyTimeout:
            return False
        rsp = MessageData()
        rsp.id = data.id
        if data.msg == "SHUTDOWN":
            self.close()
            rsp.msg = "SHUTDOWN_SUCCESS"
        elif data.msg == "CALL_FUNCTION":
            fn, args, kw = data.data
            try:
                rsp.data = getattr(self._obj, fn)(*args, **kw)
                rsp.msg = "CALL_FUNCTION_SUCCESS"
            except Exception as e:
                rsp.msg = "CALL_FUNCTION_FAILURE"
                rsp.data = e
        else:
            rsp.msg = "INTERNAL_ERROR"
            rsp.data = "Unknown command: '%s'"%data.msg
        self.send(rsp)
        return True
            