from geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
from flask import request, current_app, Flask
import gevent
import gevent.monkey
gevent.monkey.patch_all()
from app import cdx_app

from bokeh.server.app import bokeh_app
from bokeh.server.start import prepare_app as bokeh_prepare_app
from bokeh.server.start import prepare_local as bokeh_prepare_local
from redisutils import RedisProcess
import logging

PORT = 5006
REDIS_PORT = 6379
HEM_PORT = 9394
NB_PORT = 10010
log = logging.getLogger(__name__)

def prepare_app(bokehhost='127.0.0.1',
                bokehport='5006',
                rhost='127.0.0.1', rport=REDIS_PORT,
                debug=True, debugjs=True,
                username='defaultuser',
                userapikey='nokey',
                ):
    app = Flask("cdx")
    prepare_bokeh(app, rhost=rhost, rport=rport,
                  debug=debug, debugjs=debugjs)
    #FIXME - serverloc should be computed
    cdx_app.username = username
    cdx_app.userapikey = userapikey
    import views
    cdx_app.hem_port = HEM_PORT
    app.register_blueprint(cdx_app)
    if debug:
        app.debug = True
        cdx_app.debug = True
        bokeh_app.debug = True
    if debugjs:
        app.debugjs = True
        cdx_app.debugjs = True
        bokeh_app.debugjs = True
    return app

def prepare_bokeh(app, rhost='127.0.0.1', rport=REDIS_PORT,
                  debug=True, debugjs=True):
    bokeh_prepare_app(rhost=rhost, rport=rport)
    bokeh_app.hem_port = HEM_PORT
    app.register_blueprint(bokeh_app)
    if debug:
        bokeh_app.debug = True
    if debugjs:
        bokeh_app.debugjs = True

def start_app(app, verbose=False):
    global http_server
    if verbose:
        print "Starting server on port %d..." % PORT
    http_server = WSGIServer(('', PORT), app,
                             handler_class=WebSocketHandler,
                             )
    http_server.serve_forever()

def prepare_local():
    bokeh_prepare_local()

        
    