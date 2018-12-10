class Testlogin(HelloServerTestBase, unittest.TestCase):
        
    def test_login1(self):

        call = "login"
        params = (
            ("val1", "user1"),
            ("val2", "12345"),
        )
        mode = self.real_mode
        self.real_mode = False
        self.do_call_expect_xml(call, params, None)
        self.real_mode = mode
        
    def test_login2(self):

        call = "login"
        params = (
            ("val1", "pbstech"),
            ("val2", "727246"),
        )
        mode = self.real_mode
        self.real_mode = False
        self.do_call_expect_xml(call, params, None)
        self.real_mode = mode
        

class Testgetmainvalues(HelloServerTestBase, unittest.TestCase):
        
    def test_getmainvalues1(self):

        call = "getmainvalues"
        params = (
            ("json", "True"),
        )
        mode = self.real_mode
        self.real_mode = False
        self.do_call_expect_json(call, params, None)
        self.real_mode = mode
        

class Testgetmaininfo(HelloServerTestBase, unittest.TestCase):
        
    def test_getmaininfo1(self):

        call = "getmaininfo"
        params = (
            ("json", "True"),
        )
        mode = self.real_mode
        self.real_mode = False
        self.do_call_expect_json(call, params, None)
        self.real_mode = mode
        

