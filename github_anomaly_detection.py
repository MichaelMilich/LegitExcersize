import json
from flask import Flask, request, jsonify
import hmac
import hashlib
import time

from hook_handler import PushHandler

# Load configuration
with open('private_config.json') as config_file:
    config = json.load(config_file)

GITHUB_SECRET = config['GITHUB_SECRET']

app = Flask(__name__)

def verify_signature(payload, signature):
    mac = hmac.new(GITHUB_SECRET.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(f'sha256={mac}', signature)

@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.get_data()
    signature = request.headers.get('X-Hub-Signature-256')

    if not verify_signature(payload, signature):
        return 'Signature mismatch', 401

    handlers={"push":PushHandler()}

    event = request.headers.get('X-GitHub-Event')
    data = request.json

    print(f"event is = {event}")

    timestr = time.strftime("%Y%m%d-%H%M%S")
    file_name= f"{timestr}.json"

    if event == 'issues':
        file_name = f"issues_{timestr}.json"
    elif event == 'team':
        file_name = f"team_{timestr}.json"
    elif event == 'repository':
        file_name = f"repository_{timestr}.json"
    elif event == 'push':
        file_name = f"push_{timestr}.json"

    if event in handlers:
        handlers[event].check_post(event,data)

    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    return jsonify({'status': 'received'}), 200



if __name__ == '__main__':
    app.run(port=5000)