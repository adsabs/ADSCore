import os
import sys
import requests
from flask import Flask, request
from flask_minify import minify
from flask_limiter import Limiter
import flask_limiter.util
from adsmutils import ADSFlask
from adscore.flask_redis import FlaskRedisPool
import redis

def get_remote_address():
    return request.headers.get('X-Original-Forwarded-For', flask_limiter.util.get_remote_address())

def create_app(**config):
    opath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if opath not in sys.path:
        sys.path.insert(0, opath)

    if config:
        app = ADSFlask(__name__, static_folder=None, local_config=config)
    else:
        app = ADSFlask(__name__, static_folder=None)

    app.url_map.strict_slashes = False

    if app.config['MINIFY'] and app.config['ENVIRONMENT'] != "localhost":
        minify(app=app, html=True, js=True, cssless=True, caching_limit=0, fail_safe=True, bypass=[])
    
    Limiter(app, key_func=get_remote_address)
    FlaskRedisPool(app)
    
    if app.config['ENVIRONMENT'] == "localhost":
        app.debug = True
    
    return app


# XXX:rca - used anywhere? is that the reasons redis_client variable is instantiated?
app = create_app()
limiter = app.extensions['limiter']
redis_client = app.extensions['redis']