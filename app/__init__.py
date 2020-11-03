#!/usr/bin/env python

from app import webhook
from flask import Flask, render_template
from logging.config import dictConfig
import os
import logging
import requests
import threading

logging.config.dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})
logging.getLogger('werkzeug').disabled = True
logger = logging.getLogger(__name__)
os.environ['WERKZEUG_RUN_MAIN'] = 'true'

# Check for updates
stream = os.popen('git tag | tail -n 1')
app_version = stream.read().split('\n')[0]

VERSION_URL = "https://api.github.com/repos/meltaxa/jukebox-portal/releases"
try:
    url = requests.get(VERSION_URL)
    latest_version = url.json()[0]['tag_name']

    if latest_version != app_version:
      logger.warn('Update %s available. Run install.sh to update.' % latest_version)
except Exception:
    pass

app = Flask(__name__,
            static_url_path='', 
            static_folder='templates')

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

app.config.from_object('config')

with app.app_context(), app.test_request_context():
    from app.spotify import spotify as spotify_module
    app.register_blueprint(spotify_module)
    logger.info('Application started.')
    if app.config['CLIENT_ID']:
        logger.info('To activate Spotify visit: %s' % app.config['REDIRECT_URI'].replace('callback',''))
