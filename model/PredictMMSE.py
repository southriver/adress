

from pathlib import Path
import pickle

import pandas as pd

from model.AudioFeature import AudioFeature

class PredictMMSEProcess:

    def __init__(self):
        pass

    def predict(self, audio_file):
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