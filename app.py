from datetime import datetime
import os
import pickle
from flask import Flask, jsonify, render_template, request, redirect, url_for, send_from_directory
import pandas as pd

from model.AudioFeature import AudioFeature

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('index.html')
    # return "Hello, Flask!"

@app.route('/predictMMSE',methods = ['POST'])
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

    mmse = predict(audio_file=filename)

    if os.path.exists(filename):
        os.remove(filename)

    response = {
        'message': '',
        'mmse': str(mmse),
        'duration' : duration
    }
    return jsonify(response)

def validateFile(audio_file):
    audioTest = AudioFeature(audio_file=audio_file, trimSecs=3)
    checkMsg = audioTest.checkFile()
    duration = audioTest.get_info()
    if audioTest.checkFile() != '':
        return checkMsg, duration
    return '', duration

from pathlib import Path
def predict(audio_file):
    audioTest = AudioFeature(audio_file=audio_file, trimSecs=3)
    features_list = []
    test_feature = audioTest.extract_features_one_file()
    test_feature.pop('file')
    features_list.append(test_feature)
    df = pd.DataFrame(features_list)
    # normalizeData(df)
    THIS_FOLDER = Path(__file__).parent.resolve()
    my_file = THIS_FOLDER / "adressModel1.pkl"
    loaded_model = pickle.load(open(my_file,"rb"))    
    # loaded_model = pickle.load(open("adressModel1.pkl","rb"))
    result = loaded_model.predict(df)
    return result[0]
      
    # if len(request.form) != 0 :
    #     return render_template("result.html",prediction=result)
    # else:
    #     return  result

if __name__ == '__main__':
   app.run(debug=True)