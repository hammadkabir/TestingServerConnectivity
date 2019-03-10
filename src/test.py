import unittest
import json
import srv_app
import requests
from srv_app import ServerStatusTest

class TestCode(unittest.TestCase):
    def setUp(self):
        config_file     = "config.json"
        self.srv        = ServerStatusTest(config_file)

    def test_evaluate_valid_sleep_period(self):
        time_lapsed = 5
        sleep_time = self.srv._evaluate_sleep_period(time_lapsed)
        
        self.assertEqual(sleep_time, self.srv.checking_period-time_lapsed,
                         'test_evaluate_valid_sleep_period()')
    
    def test_unreachable_url(self):
        url = "http://123gadha.com/"
        resp = self.srv.do_get(url, timeout=2)
        self.assertEqual(resp, None, msg="test_unreachable_url() failed")
        
    def test_invalid_url(self):
        url = "http333333://123gadha.com/"
        resp = self.srv.do_get(url, timeout=2)
        self.assertEqual(resp, None, msg="test_invalid_url() failed")
        
    def test_valid_url(self):
        url  = "https://www.york.ac.uk/teaching/cws/wws/webpage1.html"
        resp = self.srv.do_get(url, timeout=2)
        self.assertEqual(type(resp), type(requests.models.Response()), msg="test_valid_url() failed")

    def test_find_content_success(self):
        txt = "let's test servers"
        content_req = "server"
        res = self.srv.find_content(txt, content_req)
        self.assertEqual(res, True, msg="test_find_content() failed")
    
    def test_find_content_failure(self):
        txt = "let's test servers"
        content_req = "server22"
        res = self.srv.find_content(txt, content_req)
        self.assertEqual(res, False, msg="test_find_content() failed")
    
    """
    def tearDown(self):
        self.srv.config_file.close()
        
    def test_split(self):
        self.assertRaises(TypeError)
    """

if __name__ == '__main__':
    unittest.main()