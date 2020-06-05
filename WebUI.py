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
        defaultKwargsDict = {"serverhost":'localhost',
                            "serverport":8000,
                            "browser":"default", # This can be any of https://docs.python.org/3/library/webbrowser.html.  Default opens system default
                             "startpage":"", # Where does the browser open to
                             "numberPortTries":100, # Number of times WebUI will increment port number looking for an open port before failing
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
        port = self.kwargs["serverport"]
        maxport = self.kwargs["serverport"] + self.kwargs["numberPortTries"]
        started = False
        while not started:
            if port <= maxport:
                serverAddress = (self.kwargs["serverhost"],port)
                try:
                    self.httpdserver = WebUIHTTPServer(serverAddress,self.kwargs["requestHandler"])
                    started = True
                except:
                    logger.debug("Failed to open on port {}".format(port))
                    port += 1
            else:
                raise Exception("Unable to start server at port {} with {} tries".format(self.kwargs["serverport"], self.kwargs["numberPortTries"]))

        logger.debug("Serving on {}".format(self.httpdserver.socket))
        daemon = threading.Thread(name='daemon_server',
                                  target=self.serverThreadTarget)
        daemon.setDaemon(True) # Set as a daemon so it will be killed once the main thread is dead.
        daemon.start()
        # Just give a second for it to start
        time.sleep(1)
        url = "http://%s:%i/" % serverAddress + self.kwargs["startpage"]
        self.webbrowser.open(url)
        self.waitForStop()

#--------------------------------------

import socketserver
import socket

class WebUIHTTPServer(http.server.HTTPServer):
    # Need to overide server_bind to catch Windows inability to block already in use sockets
    # Code from: https://stackoverflow.com/questions/51090637/running-a-python-web-server-twice-on-the-same-port-on-windows-no-port-already

    def server_bind(self):
        # This tests if the socket option exists (i.e. only on Windows), then
        # sets it.
        if hasattr(socket, 'SO_EXCLUSIVEADDRUSE'):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
            # Also need to change the value of allow_reuse_address
            WebUIHTTPServer.allow_reuse_address = 0

        # The rest is from: https://github.com/python/cpython/blob/3.8/Lib/http/server.py
        """Override server_bind to store the server name."""
        socketserver.TCPServer.server_bind(self)
        host, port = self.server_address[:2]
        self.server_name = socket.getfqdn(host)
        self.server_port = port

#--------------------------------------

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
