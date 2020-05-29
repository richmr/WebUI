# Michael Rich, 2020

# basic imports
import logging
logger = logging.getLogger('WebUI')
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(name)s:%(levelname)s:%(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

import http.server
import webbrowser
import threading
import time

def checkMandatoryKwargs(listOfMandatoryKwargs, kwargDict):
    for arg in listOfMandatoryKwargs:
        if arg not in kwargDict.keys():
            raise Exception("checkMandatoryKwargs: {} kwarg not found".format(listOfMandatoryKwargs))
    return True

def checkKwargsWithDefaults(dictionaryOfDefaultKwargs, kwargDict):
    for arg in dictionaryOfDefaultKwargs.keys():
        if arg in kwargDict.keys():
            # basically do nothing
            pass
        else:
            kwargDict[arg] = dictionaryOfDefaultKwargs[arg]
    return kwargDict

class WebUI(http.server.BaseHTTPRequestHandler):
"""
https://riptutorial.com/python/example/8570/start-simple-httpserver-in-a-thread-and-open-the-browser
from http.server import HTTPServer, CGIHTTPRequestHandler
import webbrowser
import threading

def start_server(path, port=8000):
    '''Start a simple webserver serving path on port'''
    os.chdir(path)
    httpd = HTTPServer(('', port), CGIHTTPRequestHandler)
    httpd.serve_forever()

# Start the server in a new thread
port = 8000
daemon = threading.Thread(name='daemon_server',
                          target=start_server,
                          args=('.', port)
daemon.setDaemon(True) # Set as a daemon so it will be killed once the main thread is dead.
daemon.start()

# Open the web browser
webbrowser.open('http://localhost:{}'.format(port))
"""

    def __init__(self, **kwargs):
        defaultKwargsDict = {"serverAddress":('localhost',8000)}
        checkKwargsWithDefaults(defaultKwargsDict, kwargs)
        self.kwargs = kwargs
        pass

    def serverThreadTarget(self):
        self.httpdserver.serve_forever()

    def go(self):
        # This starts the server and then calls the web browser to it
        self.httpserver = httpserver.HTTPServer(self.kwargs["serverAddress"],self)
        daemon = threading.Thread(name='daemon_server',
                                  target=self.serverThreadTarget,
                                  args=None)
        daemon.setDaemon(True) # Set as a daemon so it will be killed once the main thread is dead.
        daemon.start()
        # Just give a second for it to start
        time.sleep(1)
        url = "http://%s:%i" % self.kwargs["serverAddress"]
        webbrowser.open()


    ##### VERB HANDLERS #####
    def do_GET(self):
        return "This worked?"
