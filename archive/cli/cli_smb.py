"""

Created by: Nathan Starkweather
Created on: 02/03/2015
Created in: PyCharm Community Edition


"""
__author__ = 'Nathan Starkweather'


from smb.SMBConnection import SMBConnection


def cnx():
    c = SMBConnection("nstarkweather", "Nate9914#", "PBS-TOSHIBA", "integritysvr01")
    assert c.connect('192.168.1.99')
    return c


def run_150203():
    c = cnx()
    # shares = c.listShares()
    # for s in shares:
    #     print("===")
    #     print(s.name)
    #     print(s.comments)
    #     print(s.isSpecial)
    #     print(s.isTemporary)
    #     print(s.type)
    #     print("===")
    #     print()
    # rv = c.listPath("Mfg Released", "\\IF\\IF00102")
    # print(rv)
    # for f in rv:
    #     print(f.filename)
    import io
    rv = c.echo(io.BytesIO(b"hi"))
    c.close()


import socket


class SimpleFTP():
    def __init__(self, root="C:\\.replcache\\", host='', port=12345):
        self.host = host
        self.port = port
        self.root = root

    def connect(self):
        self.sock = socket.socket()
        self.sock.bind((self.host, self.port))


if __name__ == '__main__':
    run_150203()
