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
        listOfMandatoryKwargs = ["requestHandler", # this is the BaseHTTPRequestHandler to be passed to http.server
                                ]
        checkMandatoryKwargs(listOfMandatoryKwargs, kwargs)
        defaultKwargsDict = {"serverAddress":('localhost',8000),
                            "browser":"default", # This can be any of https://docs.python.org/3/library/webbrowser.html.  Default opens system default
                             "startpage":"",
                             }
        checkKwargsWithDefaults(defaultKwargsDict, kwargs)
        self.kwargs = kwargs
        self.webbrowser = webbrowser.get()
        if self.kwargs["browser"] != "default":
            self.webbrowser = webbrowser.get(self.kwargs["browser"])
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
        url = "http://%s:%i/" % self.kwargs["serverAddress"] + self.kwargs["startpage"]
        self.webbrowser.open(url)
        self.waitForStop()

from os import path
import json

class WebUIHandler(http.server.BaseHTTPRequestHandler):

    GLOBAL_COOKIES = False

    def sendResponse(self, type, data, additionalHeadersList = False, responseCode = 200):
        # additionalHeadersList is list of header tuples
        # Need some sort of static cookies sender here so different requests
        # can send/access the same cookies
        self.send_response(responseCode)
        self.send_header("Content-Type", type)
        self.send_header("Content-Length", len(data))
        if additionalHeadersList:
            for hdr in additionalHeadersList:
                self.send_header(hdr[0], hdr[1])
        if WebUIHandler.GLOBAL_COOKIES:
            # This expects GLOBAL_COOKIES to be a http.cookies object
            # This call will throw if it isn't
            self.send_header(WebUIHandler.GLOBAL_COOKIES.output())
        self.end_headers()
        self.wfile.write(data)

    def sendTextResponse(self, textToSend, additionalHeadersList = False):
        # I should probably uuencode?
        self.sendResponse("text/plain", textToSend.encode(), additionalHeadersList)

    def sendJSONResponse(self, jsonToSend, additionalHeadersList = False):
        # Do i need to encode?
        self.sendResponse("application/json", jsonToSend.encode(), additionalHeadersList)

    def sendHTMLPage(self, htmlToSend, additionalHeadersList = False):
        self.sendResponse("text/html", htmlToSend.encode(), additionalHeadersList)

    def sendHTMLPageFromFile(self, filename, additionalHeadersList = False):
        self.sendHTMLPage(self.getFileContent(filename), additionalHeadersList)

    def sendErrorPageWithMessage(self, errorCode, errorMessage):
        htmlsnippet = "<html><head><title>WebUI Error</title></head>\n"
        htmlsnippet += "<body><h3>Error: {}<br></h3>\n".format(errorCode)
        htmlsnippet += "<h5>{}</h5></body></html\n".format(errorMessage)
        self.sendResponse("text/html", htmlsnippet.encode(), False, errorCode)


    def getFileContent(self, filename, binary=False):
        # need to be prepared for bundling
        # Code taken from pyinstaller docs
        # https://pyinstaller.readthedocs.io/en/stable/runtime-information.html#run-time-information
        bundle_dir = getattr(sys, '_MEIPASS', path.abspath(path.dirname(__file__)))
        path_to_file = path.join(bundle_dir, filename)

        readstring = "r"
        if binary:
            readstring = "rb"

        try:
            with open(path_to_file, readstring) as f:
                return f.read()
        except FileNotFoundError as filebadnews:
            self.sendErrorPageWithMessage(404, "Couldn't find {}".format(filename))
            raise filebadnews
        except Exception as badnews:
            self.sendErrorPageWithMessage(500, "Oops: {}".format(badnews))
            raise badnews

    def do_GET(self):
        logger.debug("WebUIHandler.do_GET at {}".format(time.asctime()))
        # This is meant to be overridden, but may want to call the super first to handle some basic calls
        # Will return FALSE if it did not handle the call

        # specific handlers first
        if self.path == "/favicon.ico":
            logger.debug("favicon.ico response requested")
            self.sendResponse("image/x-icon", self.getFileContent("favicon.ico", binary=True))
            return True

        # general handlers for relative file paths
        if self.path.endswith(".js"):
            logger.debug("asked for js file {}".format(self.path))
            self.sendResponse("text/javascript", self.getFileContent(self.path[1:], binary=True))
            return True
        if self.path.endswith(".html"):
            logger.debug("asked for html file {}".format(self.path))
            self.sendHTMLPageFromFile(self.path[1:])
            return True
        if self.path.endswith(".css"):
            logger.debug("asked for css file {}".format(self.path))
            self.sendResponse("text/css", self.getFileContent(self.path[1:], binary=True).encode())
            return True

        return False

    def decodeDataAsJSON(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        logger.debug("POST data received: {}".format(data))
        try:
            toreturn = json.loads(data)
            return toreturn
        except json.JSONDecodeError as badjson:
            self.sendErrorPageWithMessage(400, "Can't parse following data as JSON:<br><pre>{}</pre>".format(data))
            raise badjson
        except Exception as badnews:
            self.sendErrorPageWithMessage(500, "Oops: {}".format(badnews))
            raise badnews

    def do_POST(self):
        logger.debug("WebUIHandler.do_POST at {}".format(time.asctime()))
        # This is meant to be overridden, but may want to call the super first to handle some basic calls
        # Will return FALSE if it did not handle the call

        # specific handlers first
        if self.path == "/opscheck.html":
            # find the "returnthis" data and return it
            received = self.decodeDataAsJSON()
            toreturn = received["returnthis"]
            self.sendTextResponse(toreturn)
            return True

        return False
