from flask import Flask, request, jsonify,render_template
from pymongo import MongoClient
from flask_cors import CORS
import cv2
import numpy as np
import time
from datetime import datetime

app = Flask(__name__,template_folder='public/', static_url_path='/static', static_folder='public')
CORS(app)

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client.aslmjp
collection = db.creds
collection1=db.detclgs
last_save_time = time.time()
@app.route('/dashb')
def index():
    return render_template('./dash.html')

@app.route('/upload', methods=['POST'])
def upload():
    try:
        data_url = request.json['frame']
        username = request.json.get('username')

        # Save the received frame to collection1 in MongoDB
        save_frame_to_mongodb(data_url, username)

        return jsonify({'message': 'Frame received and saved successfully'})
    except Exception as e:
        return jsonify({'error': str(e)})

def save_frame_to_mongodb(data_url,username):
    # Process the data (you can save it to a file, perform further processing, etc.)
    # For demonstration, let's print the length of the received data.
    print("Received data length:", len(data_url))

    # Save the data to MongoDB collection1
    frame_data = {
        'timestamp': time.time(),
        'data_url': data_url,
        'username': username
    }

    collection1.insert_one(frame_data)


@app.route('/sign-up', methods=['POST'])
def sign_up():
    try:
        # Get the JSON payload from the request
        data = request.get_json()

        # Extract data from the payload
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        # Check if the username already exists
        existing_user = collection.find_one({'username': username})
        if existing_user:
            return jsonify({'status': 'error', 'message': 'Signup failed. Username already exists.', 'code': 117}), 200

        # Save the data to MongoDB
        user_data = {
            'username': username,
            'email': email,
            'password': password
        }

        result = collection.insert_one(user_data)

        # Check if the data was successfully inserted
        if result.inserted_id:
            return jsonify({'status': 'success', 'message': 'Signup successful', 'code': 113}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Signup failed', 'code': 500}), 500

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e), 'code': 500}), 500

@app.route('/lgn', methods=['POST'])
def login():
    try:
        # Get the JSON payload from the request
        data = request.get_json()

        # Extract data from the payload
        username = data.get('username')
        password = data.get('password')

        # Check if the username exists
        user_data = collection.find_one({'username': username})

        if user_data:
            # Check if the provided password matches the stored password
            if user_data['password'] == password:
                return jsonify({'status': 'success', 'message': 'Login successful', 'code': 200}), 200
            else:
                return jsonify({'status': 'error', 'message': 'Login failed. Incorrect password.', 'code': 401}), 401
        else:
            return jsonify({'status': 'error', 'message': 'Login failed. User not found.', 'code': 404}), 404

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e), 'code': 500}), 500

if __name__ == '__main__':
    app.run(port=2819)
