"""

Created by: Nathan Starkweather
Created on: 12/03/2015
Created in: PyCharm Community Edition


"""
__author__ = 'Nathan Starkweather'


from http.server import HTTPServer, SimpleHTTPRequestHandler


class HelloHandler(SimpleHTTPRequestHandler):
    pass


class HelloHTTPServer(HTTPServer):
    def __init__(self, host='', port=12345):
        HTTPServer.__init__(self, (host, port), HelloHandler)




def main():
    pass


if __name__ == '__main__':
    main()
