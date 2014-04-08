#!/usr/bin/env python

"""
ToyServer, a dumb little basic WSGI server to listen to your calls.
"""

from gevent.monkey import patch_all
patch_all()

import logging
from optparse import OptionParser
import os
import re

from gevent import pywsgi

from wsgi_util.router import router
from wsgi_util.http import SuperSimple
from wsgi_util.post_util import read_postdata, read_querydata

def _initialize_logging():
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)-6s %(name)-11s: %(message)s')
    handler.setFormatter(formatter)
    logging.root.addHandler(handler)

    if 'TOYSERVER_LOG_DEBUG' in os.environ:
        logging.root.setLevel(logging.DEBUG)
    else:
        logging.root.setLevel(logging.INFO)

def _parse_cmdline():
    parser = OptionParser()
    parser.add_option("-a", dest="address", help="Address to listen on.", metavar="ADDR")
    parser.add_option("-p", dest="port", type="int", help="Port to listen on.", metavar="PORT")

    (options, _, ) = parser.parse_args()

    if not options.address:
        options.address = "127.0.0.1"
    if not options.port:
        options.port = 80

    return options

@read_querydata
def get_target(environ, start_response):
    '''
    Simple target to get your GET queries.
    It will log your query data if possible.
    Returns DEADBEEF to all GET queries.
    '''
    log = logging.getLogger("get_target")

    query_data = environ.get('query_data', None)
    if query_data is not None:
        log.info("query data: %s" % (query_data,))

    return SuperSimple("DEADBEEF")(environ, start_response)
    

@read_querydata
@read_postdata
def post_target(environ, start_response):
    '''
    Simple target to post your POST queries.
    It will log your query and post data if possible.  We're currently expecting POST data to be in the form of key=value.  We'll change this up later.
    Returns DEADBEEF to all POST queries.
    '''
    log = logging.getLogger("post_target")

    query_data = environ.get('query_data', None)
    if query_data is not None:
        log.info("query data: %s" % (query_data,))

    post_data = environ.get('post_data', None)
    if post_data is not None:
        log.info("post data: %s" % (post_data,))

    return SuperSimple("DEADBEEF")(environ, start_response)

def app_factory():
    '''
    Define the regular expressions, methods, and handling functions
    for each URL you want the server to respond to.
    '''
    urls = [
        (re.compile(r'/'), ('GET', 'HEAD',), get_target),
        (re.compile(r'/'), ('POST'), post_target),
    ] 
    return router(urls)

def main():
    _initialize_logging()
    options = _parse_cmdline()
    log = logging.getLogger("main")
    web_server = pywsgi.WSGIServer((options.address, options.port), app_factory())
    log.info("ToyServer now serving on %s port %s" % (options.address, options.port, ))
    web_server.serve_forever()

if __name__ == "__main__":
    main()
