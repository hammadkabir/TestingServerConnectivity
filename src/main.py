"""
Write test codes.            [Particularly test for failures]
Implement modular code.
Shall be scalable to large number of URLs.
Even for simultaneous queries.

------------
Push the code on GitHub as you work with it.
Signal handler to handle interrupt is needed.
Commented code, important lines and Function definitions.

Run instructions:
    Run as a shell script, with least effort needed from the user.

TBD:
    Signal Handler support, such that you perform cleanup actions.

Look at online WebCrawler codes in Python. 
Document:
    The need to install 'requests' library
    
Now:
    - Periodicity
    - Writes a log that contains the progress of the periodic checks.

Write Unit tests.
Write test cases:
    Servers whose domain name doesn't exist
    Servers that refuse connection,    
    Test HTTP and HTTPS separately

Move timing of HTTP request against the requests.get() 

Test URLS:
    {"url": "https://www.york.ac.uk/teaching/cws/wws/webpage1.html",         "content_requirement": "simple" },   - Content successfully match
    {"url": "https://www.savolahti.com",    "content_requirement": "Here we go again" },                          - Website found but content does not matche
    {"url": "http://123gadha.com/",    "content_requirement": "simple" }                                          - Website can't be reached.  
    {"url": "https://www.savolahti.com/myWish",    "content_requirement": "I wish" },                             - Page/Resource not found
    {"url": "https://www.savolahti.com/myWish",    "content_requirement": "Not found" },                          - Search NotFound content in the returned webpage 
    {"url": "http://151.101.193.69/",    "content_requirement": "Not found" },                                    - Accessing website based on IP address     
    
"""

import json
import random
import time
import logging
import traceback
import sys
import requests



def setup_logging(filename='ServerTest.log', log_level=logging.INFO):
    logging.basicConfig(filename=filename,  level=log_level, \
                        format='%(asctime)s   %(levelname)-8s   %(message)s',
                        filemode='w')

class ServerStatusTest:
    def __init__(self, config_file, name="ServerStatusTest"):
        self.config_file    = config_file
        self._logger        = logging.getLogger(name)
        self.read_config()
        self.run_app()
    
    def read_config(self):
        """ Reading the configuration file """
        c = json.load(open(self.config_file))
        if "checking_period" in c:
            self.checking_period = c["checking_period"]
        if "Test_Servers" in c:
            self.test_servers    = c["Test_Servers"]
    
    def run_app(self):
        for srv in self.test_servers:
            url, content_req = srv["url"], srv["content_requirement"]
            resp = self.process_request(url, content_req)
            #time.sleep(0.1)
    
    def process_request(self, url, content_req, timeout=1.0):       # possible to give a timeout as configuration parameter
        failure_reason = None
        start_time = time.time()
        resp = self.do_get(url, timeout=timeout)
        time_lapsed = time.time() - start_time                      # time calculation should be around --- requests.get(url, timeout=timeout)
        time_ms     = time_lapsed * 1000                            # time in milliseconds
        
        if resp is None:
            self._logger.info("Checked URL='{}' \t response-time={:.2f} ms \t content_requirement='{}', \t status={}".format(url, time_ms, content_req, "Error connecting the server"))
            return

        #print("Response status: ", resp.status_code)
        failure_reason = self.analyze_response(resp)
        if failure_reason is not None:
            self._logger.info("Checked URL='{}' \t response-time={:.2f} ms \t content_requirement='{}', \t status={}".format(url, time_ms, content_req, failure_reason))
            return
        
        found = resp.text.find(content_req)                         # Can additionally count the number of times the "required content" appeared.
        if found==-1:
            self._logger.info("Checked URL='{}' \t response-time={:.2f} ms \t content_requirement='{}', \t status='{}'".format(url, time_ms, content_req, "Required Content Not found"))
        else:
            self._logger.info("Checked URL='{}' \t response-time={:.2f} ms \t content_requirement='{}', \t status='{}'".format(url, time_ms, content_req, "Content requirement met"))

    def do_get(self, url, timeout=None):
        try:
            resp = requests.get(url, timeout=timeout)
            return resp
        except Exception as ex:
            #self._logger.warning("Exception in HTTP GET towards url=<{}>".format(ex))
            return None
    
    def analyze_response(self, resp):
        """ 
        Based on HTTP status code 4xx or 5xx determines if the error is related to client's HTTP request, or Web server's (internal) problem etc.
        Note: Another possible approach could be to search for the content_requirement on the HTML error page returned (alongwith the status codes).
        """
        reason = None
        if 400<= resp.status_code <500:
            reason = "Client's Request specific error"
        elif 500<= resp.status_code <600:
            reason = "Server specific error"

        return reason
        

if __name__=="__main__":
    try:
        setup_logging()
        config_file = "config2.json"                     # TBD: provide as input parameter
        main_log = logging.getLogger("Main")
        s = ServerStatusTest(config_file)
    except KeyboardInterrupt:
        main_log.warning("\nKeyboard interrupt")
    except Exception as ex:
        #print("Exception << {} >>'".format(ex))
        main_log.error("\nException found .. Printing Traceback \n")
        traceback.print_exc(file=sys.stdout)
        print()
    finally:
        print("Closing App .. Bye!!")
    