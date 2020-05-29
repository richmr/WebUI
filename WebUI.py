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


class WebUI():
    """
    Threaded daemon code from:
    https://riptutorial.com/python/example/8570/start-simple-httpserver-in-a-thread-and-open-the-browser

    """

    def __init__(self, **kwargs):
        listOfMandatoryKwargs = ["requestHandler" # this is the BaseHTTPRequestHandler to be passed to http.server
                                ]
        checkMandatoryKwargs(listOfMandatoryKwargs, kwargs)
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
            logger.debug("Post http.server.shutdown()")
            sys.exit()

    def go(self):
        # This starts the server and then calls the web browser to it
        self.httpdserver = http.server.HTTPServer(self.kwargs["serverAddress"],self.kwargs["requestHandler"])
        daemon = threading.Thread(name='daemon_server',
                                  target=self.serverThreadTarget)
        daemon.setDaemon(True) # Set as a daemon so it will be killed once the main thread is dead.
        daemon.start()
        # Just give a second for it to start
        time.sleep(1)
        url = "http://%s:%i/" % self.kwargs["serverAddress"]
        webbrowser.open(url)
        self.waitForStop()


class WebUIHandler(http.server.BaseHTTPRequestHandler):

    def sendResponse(self, type, data, additionalHeadersList = False):
        # additionalHeadersList is list of header tuples
        # Need some sort of static cookies sender here so different requests
        # can send/access the same cookies
        self.send_response(200)
        self.send_header("Content-Type", type)
        self.send_header("Content-Length", len(data))
        self.end_headers()
        self.wfile.write(data)

    def sendTextResponse(self, textToSend, additionalHeadersList = False):
        self.sendResponse("text/plain", textToSend.encode(), additionalHeadersList)
        pass


    def do_GET(self):
        logger.debug("WebUIHandler.do_GET at {}".format(time.asctime()))
        self.sendTextResponse("{}: Does this work".format(time.asctime()))
