import librosa
import numpy as np
import pandas as pd
import os

from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from scipy.stats import kurtosis
import pandas as pd
from sklearn.model_selection import GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier

from AudioFeature import AudioFeature
import pickle


def extract_features(audio_files):
    features_list = []
    for audio_file in audio_files:
        audFeature = AudioFeature(audio_file);
        features = audFeature.extract_features_one_file();
        # Add the dictionary to the list of features
        features_list.append(features)

    # Convert the list of features to a pandas DataFrame
    df = pd.DataFrame(features_list)
    return df

def addMMSE(data, path):
    mmses = pd.read_csv(path, delimiter=';')
    mmses = mmses[mmses['mmse'].notna()]
    mmses.set_index('ID', drop=True, inplace=True)
    dict = mmses.to_dict()['mmse']
    data['mmse'] = data['file'].map(dict)
    data.dropna(subset='mmse', inplace=True, axis=0)


def normalizeData(data):
    scaler = StandardScaler()
    data.iloc[:, 0:-1] = scaler.fit_transform(data.iloc[:, 0:-1].to_numpy())

def RFBestParams(data):
    # scaler = StandardScaler()
    # data.iloc[:, 0:-1] = scaler.fit_transform(data.iloc[:, 0:-1].to_numpy())

    rfc = RandomForestClassifier(n_jobs=-1, max_features='sqrt', n_estimators=50, oob_score=True)
    X = data.iloc[:,:-1]
    y = data.iloc[:,-1:]

    param_grid = {
        'n_estimators': [200, 700],
        'max_features': ['auto', 'sqrt', 'log2']
    }

    CV_rfc = GridSearchCV(estimator=rfc, param_grid=param_grid, cv=10)
    CV_rfc.fit(X, y)
    print (CV_rfc.best_params_)

def best_params(data):
    # Load the features extracted from the audio file as a pandas dataframe
    # Split the data into features and labels
    X = data.iloc[:,:-1]
    y = data.iloc[:,-1:]

    # Define the classifiers and hyperparameters to tune
    classifiers = {
        'LR': (LogisticRegression(), {'penalty': ['l1', 'l2'], 'C': [0.01, 0.1, 1, 10, 100]}),
        'RF': (RandomForestClassifier(), {'max_features': ['sqrt', 'log2'],
                                          'n_estimators': [10, 50, 100, 500], 'max_depth': [None, 10, 50, 100]}),
        'NN': (MLPClassifier(), {'hidden_layer_sizes': [(10,), (50,), (100,)], 'alpha': [0.0001, 0.001, 0.01]})
    }

    # Use GridSearchCV to find the best hyperparameters for each classifier
    results = {}
    for name, (model, param_grid) in classifiers.items():
        grid_search = GridSearchCV(model, param_grid, cv=10)
        grid_search.fit(X,np.ravel(y,order="c"))
        results[name] = {
            'best_params': grid_search.best_params_,
            'mean_cv_score': grid_search.best_score_
        }

    # Print the results for each classifier
    for name, result in results.items():
        print(f'{name}:')
        print(f'  Best hyperparameters: {result["best_params"]}')
        print(f'  Mean cross-validation score: {result["mean_cv_score"]:.4f}')


def applyRF(data , saveModel):

    X = data.iloc[:,:-1]
    y = data.iloc[:,-1:]

    # classification_method = RandomForestClassifier(max_features= 'log2', n_estimators= 200)
    classification_method = RandomForestClassifier(max_depth=100,max_features='log2',n_estimators=500)

    # Calculating accuracy for different folds: k-fold stratified8
    classification_scores = cross_val_score(classification_method, X, y, cv=10)
    print(classification_scores)
    print("Accuracy: %0.2f (+/- %0.2f)" % (classification_scores.mean(), classification_scores.std() * 2), "\n")

    # Calculating other scores for different folds:https://scikit-learn.org/stable/modules/model_evaluation.html#scoring-parameter
    classification_scores = cross_val_score(classification_method, X, y, cv=10, scoring="f1_weighted")
    print(classification_scores)
    print("F1 Weighted: %0.2f (+/- %0.2f)" % (classification_scores.mean(), classification_scores.std() * 2))

    classification_method.fit(X,y)

    if saveModel:
        pickle.dump(classification_method, open("adressModel1.pkl", "wb"))

def createModel():
    train_dir = 'C:/Temp/mugla/adress/train3_trimmed/frames2'
    # Get a list of all audio file paths in the train directory
    train_files = [os.path.join(train_dir, f) for f in os.listdir(train_dir) if f.endswith('.wav')]

    train_dir2 = 'C:/Temp/mugla/adress/train3_trimmed/frames'
    train_files2 = [os.path.join(train_dir2, f) for f in os.listdir(train_dir2) if f.endswith('.wav')]

    # Extract features from the train and test audio files
    train_df = extract_features(train_files)
    print("Features extracted")

    addMMSE(train_df, 'C:/Temp/mugla/adress/call_meta_data.txt')
    train_df = train_df.drop('file', axis=1)

    # Print the train and test DataFrames
    print('Train Data:')
    print(train_df)

    # normalizeData(train_df)
    # train_df = feature_select2(train_df)
    print('Train Data after normalize, feature select:')
    print(train_df)

    applyRF(train_df , True)


# createModel()
