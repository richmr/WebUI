import logging
logger = logging.getLogger('SimpRevProxy')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
formatter = logging.Formatter('%(name)s:%(levelname)s:%(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

import WebUI

from http.client import parse_headers
import argparse
import requests


class SimpleProxyHandler(WebUI.WebUIHandler):

    # Do not overide __init__ unless you pay close attention to the
    # requirements of http.server.BaseHTTPRequestHandler
    destinationHost = '127.0.0.1'

    def do_GET(self, body=True):
        try:
            # Parse request
            hostname = SimpleProxyHandler.destinationHost
            url = 'http://{}{}'.format(hostname, self.path)
            logger.debug("Got request, forwarding to: {}".format(url))
            #req_header = parse_headers(self.headers)

            # Call the target service
            resp = requests.get(url, headers=self.headers, verify=False)
            logger.debug("Response from server received, forwarding")

            # Respond with the requested data
            self.send_response(resp.status_code)
            for akey in resp.headers.keys():
                self.send_header(akey, resp.headers[akey])
            self.end_headers()
            self.wfile.write(resp.content)

        except Exception as badnews:
            self.sendErrorPageWithMessage(500, "Error: {}".format(badnews))
            logger.error("Error: {}".format(badnews))


description = 'Simple Reverse Proxy v0.1 Beta\n'
description = 'Proxies inbound HTTP Get Requests\n'

parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("destinationHost", type=str, help="Host or IP address of destination host.  Include port with IP:PORT if needed")
parser.add_argument("ProxyPort", type=int, help="Port to open the forward proxy on")
#parser.add_argument("userDataFile", type=str, help="Filename of the CSV with user data")
#parser.add_argument("numberOfSubmittals", type=int, help="Number of submittals to attempt")
#parser.add_argument("numberOfThreads", type=int, help="Number of threads to run")
#parser.add_argument("-p", "--proxy", type=str, help="Set proxy like 127.0.0.1:8080")

args = parser.parse_args()
SimpleProxyHandler.destinationHost = args.destinationHost

kargs = {"requestHandler":SimpleProxyHandler,
        "browser":False,    # Prevent opening a browser
        "serverport":args.ProxyPort,
        }
SimpleAppServer = WebUI.WebUI(**kargs)
SimpleAppServer.go()
