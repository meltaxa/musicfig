#!/usr/bin/env python

from app import webhook
from flask import Flask, render_template
from logging.config import dictConfig
import os
import logging

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

app = Flask(__name__,
            static_url_path='', 
            static_folder='templates')

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

app.config.from_object('config')
if app.config['USAGE']:
    webhook.Requests.post("https://maker.ifttt.com/trigger/usage/with/key/%s" % app.config['USAGE_API'],
                          {'value1': app.config['VERSION'],
                           'value2': 'started.'})

with app.app_context(), app.test_request_context():
    from app.spotify import spotify as spotify_module
    app.register_blueprint(spotify_module)
    logger.info('Application started.')
