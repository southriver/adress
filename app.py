from datetime import datetime
from functools import wraps
import os
from pathlib import Path
import pickle
from flask import Flask, jsonify, render_template, request, redirect, url_for, send_from_directory
import pandas as pd
from model.config import Config

from model.AudioFeature import AudioFeature
from model.db.DGJobAccess import DGJobAccess
from model.PredictMMSE import PredictMMSEProcess

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('index.html', bearerToken=Config.BEARER_TOKEN)

# Decorator for verifying bearer token
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            # Extract the token from the "Authorization" header
            auth_header = request.headers['Authorization']
            bearer_token = auth_header.split(' ')
            if len(bearer_token) == 2 and bearer_token[0] == 'Bearer':
                token = bearer_token[1]

        # Replace 'your_bearer_token' with the actual expected bearer token value
        expected_token = Config.BEARER_TOKEN

        if not token or token != expected_token:
            # Token is missing or invalid
            return jsonify({'message': 'Missing or invalid token'}), 401

        # Perform additional token validation if needed
        # ...

        return f(*args, **kwargs)

    return decorated

@app.route('/insertMMSEJob',methods = ['POST'])
@token_required
def insertMMSEJob():
    audioFile = request.files['audioFile']
    userName = request.form['userEmail'];
    response = {
        'status': 'SUCCESS'
    }
    try:
        access = DGJobAccess()
        # check if there are any jobs for user already
        anyPendingAppliedJob =  access.getMostRecentJobForUser(userName , ['PENDING','IN PROGRESS'])
        if (anyPendingAppliedJob != None):
            response = {
                'status': 'FAILURE',
                'message' : 'There is already a PENDING or IN PROGRESS job for user. Try after these are processed'
            }        
            return jsonify(response)   
        filename = datetime.utcnow().strftime('%Y%m%d%H%M%S%f') + '_' + audioFile.filename
               
        THIS_FOLDER = Path(__file__).parent.resolve()
        finalFilename = THIS_FOLDER  / 'MMSE' /  filename
        audioFile.save(finalFilename)

        jobData = { "JobData" : filename,
                    "JobStatus" : "PENDING",
                    "JobOwner" : userName,
                    "JobType" : "MMSE"
                }
        id = access.insertJob(jobData)
        
        return jsonify(response)    
    except Exception as error:
        response = {
            'status': 'FAILURE',
            'message' : str(error)
        }        
        return jsonify(response)    


@app.route('/predictMMSE',methods = ['POST'])
@token_required
def predictMMSE():
    audioFile = request.files['audioFile']
    
    filename = 'file.wav'
    audioFile.save(filename)

    valMsg, duration = validateFile(filename)
    if valMsg != '':
        response = {
            'message': valMsg,
            'duration' : duration
        }
        return jsonify(response)

    process = PredictMMSEProcess()
    mmse = process.predict(audio_file=filename)

    if os.path.exists(filename):
        os.remove(filename)

    response = {
        'message': '',
        'mmse': str(mmse),
        'duration' : duration
    }
    return jsonify(response)

@app.route('/getMMSEJobs',methods = ['POST'])
@token_required
def getMMSEJobs():
    content = request.json
    access = DGJobAccess()
    ptEmail = content["userEmail"]
    jobs = access.getJobsForUser(ptEmail)
    ret = []
    for job in jobs:
        retItem =  {
            'createDate': job["JobCreateDate"],
            'MMSEScore': job["JobResult"],
            'status' : job["JobStatus"]
        }
        ret.append(retItem)    
    return ret

def validateFile(audio_file):
    audioTest = AudioFeature(audio_file=audio_file, trimSecs=3)
    checkMsg = audioTest.checkFile()
    duration = audioTest.get_info()
    if audioTest.checkFile() != '':
        return checkMsg, duration
    return '', duration


if __name__ == '__main__':
   app.run(debug=True)