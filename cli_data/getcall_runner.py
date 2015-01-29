"""

Created by: Nathan Starkweather
Created on: 01/16/2015
Created in: PyCharm Community Edition


"""
__author__ = 'Nathan Starkweather'


import unittest
from hello.func_test import server_calls
from hello.old import dummy2
import threading


def main():

    """
    I wanted to use the existing server_calls.py file to run the dummy response
    generator in dummy2, but didn't want to have to add code to the server_calls.py
    file for a task that was completely unrelated. Since server_calls uses pycharm's
    unittest framework (with python's unittest module), this was a bit awkward.
    This module should work fine, just running the basic unittest framework without
    the pycharm support. Also, need to hack the auto-generated test list to ensure
    that the appropriate server ipv4 address is used.
    """

    t = s = None

    def setup():

        nonlocal t, s
        s = dummy2.server_with_getcall()
        t = threading.Thread(None, s.serve_forever)
        t.daemon = True
        t.start()

    def teardown():
        s.shutdown()
        with open("C:\\.replcache\\getcalls_unittest.py", 'w') as f:
            s.caller.dump(f)

    test_classes = {cls_name: getattr(server_calls, cls_name)
                    for cls_name in dir(server_calls) if "TestServerCalls" in cls_name}

    TestServerCalls = test_classes.pop("TestServerCalls", None)
    # todo- finish hijack code
    # if TestServerCalls

    # server_calls.setUpModule = setup
    # server_calls.tearDownModule = teardown
    setup()
    try:
        unittest.main(server_calls)
    finally:
        teardown()

if __name__ == '__main__':
    main()
