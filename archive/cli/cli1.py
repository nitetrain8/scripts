"""

Created by: Nathan Starkweather
Created on: 01/08/2015
Created in: PyCharm Community Edition


"""
__author__ = 'Nathan Starkweather'

from hello.mock.server import HelloServer

def main():
    server = HelloServer()
    server.serve_forever()


if __name__ == '__main__':
    main()
