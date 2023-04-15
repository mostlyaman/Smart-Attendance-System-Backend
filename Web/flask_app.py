from flask import Flask
from flask import request, session
from model import face_search
import cv2
import numpy as np
from werkzeug.security import generate_password_hash, check_password_hash
from utils import run_query
import dotenv
import os

dotenv.load_dotenv(os.path.join(os.getcwd(), '.env'))
db_name = os.getenv('DB_NAME')

import json

app = Flask(__name__)

@app.route('/api/v1/test', methods=['GET'])
def test_server():
    return "Server is running."


@app.route('/api/v1/face_recognition', methods=['POST'])
def face_recognition():
    try:
        if 'image' in request.files:
            image = request.files['image']
            frame = cv2.imdecode(np.frombuffer(image.read(), np.uint8), cv2.IMREAD_COLOR)
            return json.dumps({"status": "ok", "result": face_search(frame)})
        else:
            return json.dumps({"status":"error", "message": "No Image Selected."}), 400
    except Exception as e:
        return json.dumps({"status":"error", "message":"Something went wrong.", "error": str(e)}), 500


@app.route('/api/v1/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data['email']
        password = data['password']

        query = f'select email, password, name from {db_name}.users where email="{email}"'
        res, code = run_query(query)
        if code != 200:
            return res, code
        
        if len(res) == 0:
            return json.dumps({"status":"error", "message": "No user found for this email. Please sign up instead."}), 400
        else:
            if check_password_hash(res[0][1], password):
                session["email"] = email
                session["name"] = res[0][2]
                return json.dumps({"status": "ok"}), 200
            
            return json.dumps({"status":"error", "message":"Wrong Password."}), 400

    except Exception as e:
        return json.dumps({"status":"error", "message":"Something went wrong.", "error": e}), 500




@app.route('/api/v1/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        email = data['email']
        password = generate_password_hash(data['password'])
        name = data['name']

        query = f'select email from {db_name}.users where email="{email}"'
        res, code = run_query(query)
        if code != 200:
            return res, code
        
        if len(list(res)) > 0:
            return json.dumps({"status":"error", "message": "This email is already taken. Please login instead."}), 400

        query = f'insert into {db_name}.users(name, email, password) values("{name}", "{email}", "{password}")'
        res, code = run_query(query)
        if code != 200:
            return res, code
        
        session["name"] = name
        session["email"] = email
        return json.dumps({"status": "ok"}), 200
    
    except Exception as e:
        return json.dumps({"status":"error", "error": str(e)}), 500

