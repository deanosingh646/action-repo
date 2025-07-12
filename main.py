# File: app.py
from flask import Flask, request, render_template, jsonify
from datetime import datetime
from flask_cors import CORS
import os

# Simulated MongoDB replacement using in-memory list for demo/testing
mock_db = []

app = Flask(__name__)
CORS(app)  # Allow frontend to poll from JS


# Webhook endpoint
@app.route('/webhook', methods=['POST'])
def github_webhook():
    data = request.json

    # Identify the action type
    if 'pusher' in data:
        action_type = 'PUSH'
        author = data['pusher']['name']
        to_branch = data['ref'].split('/')[-1]
        from_branch = "N/A"
        timestamp = datetime.utcnow()
        request_id = data['head_commit']['id']

    elif 'pull_request' in data:
        action_type = 'PULL_REQUEST'
        author = data['pull_request']['user']['login']
        from_branch = data['pull_request']['head']['ref']
        to_branch = data['pull_request']['base']['ref']
        timestamp = datetime.strptime(data['pull_request']['created_at'],
                                      "%Y-%m-%dT%H:%M:%SZ")
        request_id = data['pull_request']['id']

    else:
        return jsonify({"message": "Unsupported event"}), 400

    doc = {
        "request_id": str(request_id),
        "author": author,
        "action": action_type,
        "from_branch": from_branch,
        "to_branch": to_branch,
        "timestamp": timestamp
    }

    mock_db.append(doc)
    return jsonify({"message": "Event saved successfully"}), 201


# UI route
@app.route('/')
def index():
    return render_template('index.html')


# Test route to add sample data
@app.route('/test-data', methods=['POST'])
def add_test_data():
    from datetime import datetime
    test_events = [{
        "request_id": "test123",
        "author": "john_doe",
        "action": "PUSH",
        "from_branch": "N/A",
        "to_branch": "main",
        "timestamp": datetime.utcnow()
    }, {
        "request_id": "test456",
        "author": "jane_smith",
        "action": "PULL_REQUEST",
        "from_branch": "feature-auth",
        "to_branch": "main",
        "timestamp": datetime.utcnow()
    }]
    mock_db.extend(test_events)
    return jsonify({"message": "Test data added"}), 200


# API route for polling
@app.route('/events', methods=['GET'])
def get_events():
    sorted_events = sorted(mock_db, key=lambda x: x['timestamp'],
                           reverse=True)[:10]
    output = []
    for event in sorted_events:
        time_str = event['timestamp'].strftime("%d %B %Y - %I:%M %p UTC")
        if event['action'] == 'PUSH':
            msg = f"{event['author']} pushed to {event['to_branch']} on {time_str}"
        elif event['action'] == 'PULL_REQUEST':
            msg = f"{event['author']} submitted a pull request from {event['from_branch']} to {event['to_branch']} on {time_str}"
        else:
            msg = f"{event['author']} performed {event['action']}"
        output.append(msg)
    return jsonify(output)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
