"""
TBD:
    Signal Handler support, such that you perform cleanup actions.
    Simultaneous processing of HTTP queries - scalable to many requests.
    Strict enforcement of configuration file parameters.
    Moving of time() strictly around requests.get() 
    Displaying exact error message against each HTTP status code. 
    More test cases

Document:
    Programmed in python3
    The need to install 'requests' library

Perhaps a more user-friendly configuration file possible via YAML language.

Test URLs:
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
                        format='%(asctime)s   %(name)s   %(levelname)-8s   %(message)s',
                        filemode='w')

class ServerStatusTest:
    def __init__(self, config_file, name="ServerStatusTest"):
        self.config_file    = config_file
        self._logger        = logging.getLogger(name)
        self.read_config()
    
    def read_config(self):
        """ Reading the configuration file """
        c = json.load(open(self.config_file))                       # Can be read periodically as well
        if "checking_period" in c:
            self.checking_period = float(c["checking_period"])
        if "Test_Servers" in c:
            self.test_servers    = c["Test_Servers"]
    
    def run_app(self):
        """ Main function that periodically executes the loop"""
        i = 1
        while True:
            print("Round#{} of testing URLs".format(i))
            start_time = self._now()
            self._run()
            time_lapsed = self._now() - start_time
            self.schedule_next_cycle(time_lapsed)
            self._logger.info("Round#{} of testing URLs".format(i+1))
            i += 1

    def schedule_next_cycle(self, time_lapsed):
        """ Schedules periodic checks to webservers - by putting the code execution to sleep """
        sleep_time = self._evaluate_sleep_period(time_lapsed)
        time.sleep(sleep_time)
    
    def _evaluate_sleep_period(self, time_lapsed):
        """ Returns the sleep time, until next execution cycle """
        sleep_time = self.checking_period - time_lapsed
        
        if sleep_time < 0:
            sleep_time = random.randint(5, 20)
            self._logger.info("checking period > URL processing period ... Randomly choosing a sleep time of '{}' sec".format(sleep_time))
            
        return sleep_time
    
    def _now(self):
        """ Returns current time """
        return time.time()

    def _run(self):
        """ Goes over the list of URLs and searches corresponding content requirement """
        for srv in self.test_servers:
            url, content_req = srv["url"], srv["content_requirement"]
            self.process_request(url, content_req)

            
    def process_request(self, url, content_req, timeout=1.0):       # possible to give a timeout as configuration parameter
        failure_reason = None
        start_time = time.time()
        resp = self.do_get(url, timeout=timeout)
        time_lapsed = time.time() - start_time                      # time calculation should be around --- requests.get(url, timeout=timeout)
        time_ms     = time_lapsed * 1000                            # time in milliseconds
        self._analyze_response(url, time_ms, resp, content_req)
    
    def _analyze_response(self, url, time_ms, resp, content_req):
        """ Evaluates the response and Records it to Log file """
        if resp is None:
            self._logger.info("Checked URL='{}' \t response-time={:.2f} ms \t content_requirement='{}', \t status={}".format(url, time_ms, content_req, "Server down (or Unreachable)"))
            return

        #print("Response status: ", resp.status_code)
        failure_reason = self.analyze_status_codes(resp)
        if failure_reason is not None:
            self._logger.info("Checked URL='{}' \t response-time={:.2f} ms \t content_requirement='{}', \t status={}".format(url, time_ms, content_req, failure_reason))
            return
        
        found = self.find_content(resp.text, content_req)
        if found:
            self._logger.info("Checked URL='{}' \t response-time={:.2f} ms \t content_requirement='{}', \t status='{}'".format(url, time_ms, content_req, "Required Content Not found"))
        else:
            self._logger.info("Checked URL='{}' \t response-time={:.2f} ms \t content_requirement='{}', \t status='{}'".format(url, time_ms, content_req, "Content requirement met"))


    def do_get(self, url, timeout=None):
        """ Performs actual GET request to web servers """
        try:
            resp = requests.get(url, timeout=timeout)
            return resp
        except Exception as ex:
            #self._logger.warning("Exception in HTTP GET towards url=<{}>".format(ex))
            return None
    
    def find_content(self, txt, content_req):
        """ Returns True or False, depending on if the content is found """
        found = txt.find(content_req)                          # Might additionally return the count of "required content" in text.
        if found == -1:
            return False
        else:
            return True
    
    def analyze_status_codes(self, resp):
        """ 
        Based on HTTP status code 4xx or 5xx determines if the error is related to client's HTTP request, or Web server's (internal) problem etc.
        Note: Another possible approach could be to search for the content_requirement on the HTML error page returned (alongwith the status codes).
        """
        reason = None
        if 400<= resp.status_code <500:
            reason = "Client's Request error (i.e. NotFound/Forbidden/BadRequest etc.)"
        elif 500<= resp.status_code <600:
            reason = "Server specific error"

        return reason
        

if __name__=="__main__":
    try:
        if len(sys.argv) != 2:
            print("Run program using     'python3 main.py config.json' ")
            sys.exit(1)
        
        print("Starting the App")
        config_file = sys.argv[1]
        setup_logging()
        main_log = logging.getLogger("Main")
        s = ServerStatusTest(config_file)
        s.run_app()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt")
    except Exception as ex:
        #print("Exception << {} >>'".format(ex))
        main_log.error("\nException found .. Printing Traceback \n")
        traceback.print_exc(file=sys.stdout)
        print()
    finally:
        print("Closing App .. Bye!!")
    