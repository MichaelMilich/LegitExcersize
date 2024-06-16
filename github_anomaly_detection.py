"""
A script that starts a server that saves and notifies any anomalies in the github using web hooks

Usage:
    python github_anomaly_detection.py <port_number> <save_file_name>
    arguments are:
    MUST ->
        port_number : the number of the port for the server.
    OPTION ->
        save_file_name : the .csv file to which we save the data, default is log.csv, write None for no logging.

Dependencies:
    - Flask server - pip3 install flask - for the server
    - Pandas - pip3 install pandas - for the logger

Constrains:
    - Requires that a private_config.json containing GITHUB_SECRET string be present in the project directory
    - Currently the logging is very basic, only prints and saves to another file


Written by:
    - Michael Millich 16.06.2024
"""

import json
import sys
from flask import Flask, request, jsonify
import hmac
import hashlib

from hook_handler import PushHandler, TeamHandler, RepoHandler
from basic_logger import BasicLogger


class AnomalyServer:
    """
    The basic server object that holds sets up the route and deals with all the web hook post events.
    Uses various handlers to call handle the different events.
    """

    def __init__(self, log_file_name=None):
        self.secret = self.get_secret()
        self.logger = None
        if log_file_name is not None and ".csv" in log_file_name:
            self.logger = BasicLogger(log_file_name)
        self.handlers = {
            "push": PushHandler(self.logger),
            "team": TeamHandler(self.logger),
            "repository": RepoHandler(self.logger)
        }
        self.app = Flask(__name__)
        self.setup_routes()

    def get_secret(self):
        """
        Loads the GITHUB secret string that is not pushed to github.
        :return: None
        """
        with open('private_config.json') as config_file:
            config = json.load(config_file)
        return config['GITHUB_SECRET']

    def setup_routes(self):
        """
        starts the routes that receives the web hooks and handles them.
        :return: None
        """

        @self.app.route('/webhook', methods=['POST'])
        def webhook():
            payload = request.get_data()
            signature = request.headers.get('X-Hub-Signature-256')

            if not self.verify_signature(payload, signature):
                return 'Signature mismatch', 401

            event = request.headers.get('X-GitHub-Event')
            data = request.json

            if event in self.handlers:
                self.handlers[event].check_post(event, data)

            return jsonify({'status': 'received'}), 200

    def verify_signature(self, payload, signature):
        """
        verifies that the signature is as stated in the secret file
        :param payload: payload provided from the webhook
        :param signature: signature provided from the webhook
        :return: True if the signature is the same as our secret signature
        """
        mac = hmac.new(self.secret.encode(), payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(f'sha256={mac}', signature)


def main(port, log_file_name):
    server = AnomalyServer(log_file_name)
    server.app.run(port=port)


if __name__ == '__main__':
    args = sys.argv
    port = 5000
    log_file_name = "data.csv"

    if len(args) > 1 and args[1].isnumeric():
        port = int(args[1])
    if len(args) > 2 and (".csv" in args[2] or args[2] == "None"):
        log_file_name = args[2]

    main(port, log_file_name)
