import logging
logger = logging.getLogger('SimpleAPP')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(name)s:%(levelname)s:%(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
import WebUI

class SimpleAppHandler(WebUI.WebUIHandler):

    # Do not overide __init__ unless you pay close attention to the
    # requirements of http.server.BaseHTTPRequestHandler

    def do_GET(self):
        # You do not need to overide do_GET if you are only expecting static
        # html, css, js files.  They are handled by the super class
        # The super class has the ability to handle templated pages.
        # See sendTemplatedHTMLPageFromFile()
        # If you are passing get parameters, you can parse them with:
        # parseGetParameters()
        superHandledIt = super().do_GET()
        if not superHandledIt:
            # handle the remaining requests
            if self.realpath == "/cgi-bin/aw_ptz":
                params = self.parseGetParameters()
                if "cmd" in params.keys():
                    logger.debug("Got aw_ptz command, sending response {}".format(params["cmd"][0]))
                    self.sendTextResponse("{}".format(params["cmd"][0]))
                else:
                    logger.debug("aw_ptz called with no command, sending blank response")
                    self.sendTextResponse("blank")
                return
        else:
            # Super did it, we need to exit
            return

        self.sendErrorPageWithMessage(404, "{} not found".format(self.realpath))

# Now we call the WebUI
kargs = {"requestHandler":SimpleAppHandler,
        "browser":"firefox",
        "startpage":"cgi-bin/aw_ptz?cmd=HelloWorld"}
SimpleAppServer = WebUI.WebUI(**kargs)
SimpleAppServer.go()
