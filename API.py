import datetime
from flask import Flask, request, jsonify,render_template
from pymongo import MongoClient
from flask_cors import CORS
import time
import random
import string
import threading
app = Flask(__name__,template_folder='public/', static_url_path='/static', static_folder='public')
CORS(app)

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client.aslmjp
collection = db.creds
collection1=db.detclgs
collection2=db.stlgs
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
        # save_frame_to_mongodb(data_url, username)

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

@app.route('/clhs', methods=['POST'])
def clear_session():
    try:
        stkey = request.json.get('stkey')
        print(stkey)
        session_data = collection2.find_one({'stkey': stkey})
        if session_data:
            collection2.delete_one({'stkey': stkey})
            return jsonify({'status': 'success', 'message': 'Session cleared successfully'}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Invalid stkey', 'code': 404}), 404

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e), 'code': 500}), 500

@app.route('/gusn', methods=['POST'])
def get_username_by_stkey():
    try:
        stkey = request.json.get('stkey')

        # Check if the stkey exists in collection2
        session_data = collection2.find_one({'stkey': stkey})
        if session_data:
            username = session_data['username']
            return jsonify({'status': 'success', 'username': username}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Invalid stkey', 'code': 404}), 404

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e), 'code': 500}), 500

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

def remove_old_sessions():
    current_time = time.strftime('%H:%M:%S', time.localtime())
    threshold_time = (datetime.datetime.strptime(current_time, '%H:%M:%S') - datetime.timedelta(minutes=20)).strftime('%H:%M:%S')
    collection2.delete_many({'timestamp': {'$lt': threshold_time}})
    # print(datetime.datetime.strptime(current_time, '%H:%M:%S'))

# Periodically check for and remove old sessions
def check_and_remove_old_sessions():
    while True:
        remove_old_sessions()
        time.sleep(600)  # Check every 10 minutes (adjust as needed)
session_cleanup_thread = threading.Thread(target=check_and_remove_old_sessions)
session_cleanup_thread.start()

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
                stkey = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
                current_time = time.strftime('%H:%M:%S', time.localtime())
                session_data = {
                    'username': username,
                    'stkey': stkey,
                    'timestamp': current_time
                }
                collection2.insert_one(session_data)
                return jsonify({'status': 'success', 'message': 'Login successful', 'code': 200,'stkey': stkey}), 200
            else:
                return jsonify({'status': 'error', 'message': 'Login failed. Incorrect password.', 'code': 401}), 401
        else:
            return jsonify({'status': 'error', 'message': 'Login failed. User not found.', 'code': 404}), 404

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e), 'code': 500}), 500

if __name__ == '__main__':
    collection2.delete_many({})
    app.run(port=2819)
