import json
from flask import Flask, request, jsonify
import hmac
import hashlib
from hook_handler import PushHandler, TeamHandler, RepoHandler


class AnomalyServer:
    """
    The basic server object that holds sets up the route and deals with all the web hook post events.
    Uses various handlers to call handle the different events.
    """
    def __init__(self):
        self.secret = self.get_secret()
        self.handlers = {
            "push": PushHandler(),
            "team": TeamHandler(),
            "repository": RepoHandler()
        }
        self.app = Flask(__name__)
        self.setup_routes()

    def get_secret(self):
        # Load configuration
        with open('private_config.json') as config_file:
            config = json.load(config_file)
        return config['GITHUB_SECRET']

    def setup_routes(self):
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
        mac = hmac.new(self.secret.encode(), payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(f'sha256={mac}', signature)


if __name__ == '__main__':
    server = AnomalyServer()
    server.app.run(port=5000)
