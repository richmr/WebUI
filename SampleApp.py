"""
WARNING (AND I CANT STRESS THIS ENOUGH): WebUI is NOT designed to be a public server
It is designed to provide a cross-platform UI for applications
WebUI, as is, is not secure.  If you serve a public page with this you will be vulnerable
to much of the OWASP Top 10.
DO NOT USE THIS TO PROVIDE A PUBLIC SERVICE!!

This is a sample WebUI App to illustrate use of WebUI
There are two main parts:
- subclass the WebUI handler
- Call the WebUI "server"
- If using the
"""
import logging
logger = logging.getLogger('SampleAPP')
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(name)s:%(levelname)s:%(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
import WebUI

class SampleAppHandler(WebUI.WebUIHandler):

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
            if self.realpath == "/SampleApp.html":
                params = self.parseGetParameters()
                templateData = {"user":"Dave"}
                if "user" in params.keys():
                    templateData["user"] = ",".join(params["user"])
                self.sendTemplatedHTMLPageFromFile("SampleApp.html",templateData)
                return
        else:
            # Super did it, we need to exit
            return

        self.sendErrorPageWithMessage(404, "{} not found".format(self.realpath))

# Now we call the WebUI
kargs = {"requestHandler":SampleAppHandler,
        "browser":"firefox",
        "startpage":"SampleApp.html"}
SampleAppServer = WebUI.WebUI(**kargs)
SampleAppServer.go()
