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
    rv = c.echo("hi")
    c.close()

if __name__ == '__main__':
    run_150203()
