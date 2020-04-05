import os
import sys

import dotenv
from flask import abort, Flask, jsonify, request
import hashlib
import hmac
from slackeventsapi import SlackEventAdapter

dotenv.load_dotenv()

app = Flask(__name__)

slack_signing_secret = os.environ["SLACK_SIGNING_SECRET"]
event_adapter = SlackEventAdapter(slack_signing_secret, "/slack/events", app)


def is_request_valid(request):
    is_token_valid = request.form["token"] == os.environ["VERIFICATION_TOKEN"]
    is_team_id_valid = request.form["team_id"] == os.environ["SLACK_TEAM_ID"]

    return is_token_valid and is_team_id_valid


def verify_signature(signing_secret, timestamp, signature):
    # Verify the request signature of the request sent from Slack
    # Generate a new hash using the app's signing secret and request data

    # Compare the generated hash and incoming request signature
    # Python 2.7.6 doesn't support compare_digest
    # It's recommended to use Python 2.7.7+
    # noqa See https://docs.python.org/2/whatsnew/2.7.html#pep-466-network-security-enhancements-for-python-2-7
    req = str.encode("v0:" + str(timestamp) + ":") + request.get_data()
    request_hash = (
        "v0=" + hmac.new(str.encode(signing_secret), req, hashlib.sha256).hexdigest()
    )
    # Compare byte strings for Python 2
    print(request_hash)
    return hmac.compare_digest(request_hash, signature)
    print("fail")


@app.route("/slash", methods=["POST"])
def hello_there():
    if not event_adapter.server.verify_signature(
        request.headers.get("X-Slack-Request-Timestamp"),
        request.headers.get("X-Slack-Signature"),
    ):
        print("Did not make it?")
        abort(400)

    print("Made it!")
    # 1: parse the command 
    # 2: get list of saved phrases 
    print(request.form)
    return jsonify(
        response_type="in_channel",
        text="<https://youtu.be/frszEJb0aOo|General Kenobi!>",
    )
