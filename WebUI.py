# Michael Rich, 2020

# basic imports
import logging
logger = logging.getLogger('WebUI')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(name)s:%(levelname)s:%(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

import http.server
import webbrowser
import threading
import time
import sys


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

##### HandlerSubclass #####
class WebUIHandler(http.server.BaseHTTPRequestHandler):

class WebUI():
    """
    Threaded daemon code from:
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
        logger.debug("httpd thread started")
        self.httpdserver.serve_forever()

    def waitForStop(self):
        logger.debug("waitForStop")
        try:
            while True:
                time.sleep(0.5)
        except:
            # probably keyboard interrupt
            logger.debug("Graceful shutdown")
            self.httpdserver.shutdown()
            sys.exit()

    def go(self):
        # This starts the server and then calls the web browser to it
        self.httpdserver = http.server.HTTPServer(self.kwargs["serverAddress"],self)
        daemon = threading.Thread(name='daemon_server',
                                  target=self.serverThreadTarget)
        daemon.setDaemon(True) # Set as a daemon so it will be killed once the main thread is dead.
        daemon.start()
        # Just give a second for it to start
        time.sleep(1)
        url = "http://%s:%i/" % self.kwargs["serverAddress"]
        webbrowser.open(url)
        self.waitForStop()

    ##### Verbs #####
    def do_GET(self, handlerObject):
        logger.debug("do_GET")
        return "Does this work"



    ##### HandlerSubclass #####
    class WebUIHandler(http.server.BaseHTTPRequestHandler):

        def setVerbSource(self, verbSourceObj):
            self.VSO = verbSourceObj

        def do_GET(self):
            logger.debug("WebUIHandler.do_GET")
            return self.VSO.do_GET(self)
            
