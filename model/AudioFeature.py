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


def trim_start_end_file(audioIn, sr, secs):
    start_time = secs  # seconds
    end_time = audioIn.shape[0] / sr - secs  # seconds

    # Trim the audio
    start_sample = int(start_time * sr)
    end_sample = int(end_time * sr)
    y_trimmed = librosa.util.fix_length(data=audioIn[start_sample:end_sample], size=end_sample - start_sample)
    return y_trimmed

class AudioFeature:

    def __init__(self, audio_file, trimSecs=0):
        self.audio_file = audio_file
        self.trimSecs = trimSecs;

    def checkFile(self):
        if not self.audio_file.endswith('.wav'):
            return "Dosya .wav dosyasi olmali"
        audio_data, sr = librosa.load(self.audio_file, sr=None,mono=True)
        duration = librosa.get_duration(y=audio_data, sr=sr)
        if duration > 120:
            return 'Wav dosyayi max 120 saniye olabilir'
        return ''
    # Function to extract features from a list of audio files
    def extract_features_one_file(self):

        # Load the audio data using Librosa
        audio_data, sr = librosa.load(self.audio_file, sr=None,mono=True)
        # audio_data, index = librosa.effects.trim(audio_data, top_db=20)
        if self.trimSecs > 0:
            audio_data = trim_start_end_file(audioIn=audio_data, sr=sr, secs=self.trimSecs)

        # Calculate the audio duration in seconds
        duration = librosa.get_duration(y=audio_data, sr=sr)

        # Calculate the root mean square (RMS) energy of the audio signal
        rms = librosa.feature.rms(y=audio_data)

        # Calculate the zero crossing rate (ZCR) of the audio signal
        zcr = librosa.feature.zero_crossing_rate(y=audio_data)

        # Calculate the spectral centroid of the audio signal
        spec_cent = librosa.feature.spectral_centroid(y=audio_data, sr=sr)

        # Calculate the spectral bandwidth of the audio signal
        spec_bw = librosa.feature.spectral_bandwidth(y=audio_data, sr=sr)

        # Calculate the mel-frequency cepstral coefficients (MFCCs) of the audio signal
        mfccs = librosa.feature.mfcc(y=audio_data, sr=sr,n_mfcc=30)
        mfcc_means = mfccs.mean(axis=1).T
        mfcc_stds = mfccs.std(axis=1).T
        # mfcc_kurtosis = kurtosis(mfccs,axis=1).T
        # mfccs_flat = mfccs.flatten()

        #filter bank energy
        n_fft = 2048  # window size
        hop_length = 512  # hop length
        mel_spec = librosa.feature.melspectrogram(y=audio_data, sr=sr, n_mels=128, fmax=8000)
        log_mel_spec = librosa.power_to_db(mel_spec, ref=np.max)
        filterBankEng = log_mel_spec
        # fbes = filterBankEng.mean(axis=1).T

        #skewness
        # Compute skewness of each MFCC coefficient
        skewness = librosa.feature.mfcc(S=log_mel_spec, n_mfcc=30, axis=1, stat='skew')
        skewness_means = skewness.mean(axis=1).T

        #special contrast
        spec_con = librosa.feature.spectral_contrast(y=audio_data, sr=sr, n_bands=3)
        spec_con_mean = spec_con.mean(axis=1).T
        spec_con_std = spec_con.std(axis=1).T

        #chroma_stft
        stft = np.abs(librosa.stft(y=audio_data))
        chroma_stft = librosa.feature.chroma_stft(S=stft, sr=sr)
        chroma_mean = chroma_stft.mean(axis=1).T
        chroma_std = chroma_stft.std(axis=1).T

        #
        # Find silent segments
        threshold = 30
        intervals = librosa.effects.split(y=audio_data, top_db=threshold,
                                          hop_length=hop_length)
        silence_intervals = [[intervals[i - 1][1], intervals[i][0]] for i in range(1, len(intervals))]
        # Get the number of silent segments
        num_silence_segments = len(silence_intervals)

        head, tail = os.path.split(self.audio_file)
        file_name_as_index = tail.split(".")[0]
        if file_name_as_index.find('_') != -1:
            file_name_as_index = file_name_as_index.split('_')[0]
        elif file_name_as_index.find('-') != -1:
            file_name_as_index = file_name_as_index.split('-')[0]

        # Create a dictionary with the feature values
        features = {
            'file': file_name_as_index,
            'duration': duration,
            'rms': np.mean(rms),
            'zcr': np.mean(zcr),
            'spec_cent': np.mean(spec_cent),
            'spec_bw': np.mean(spec_bw),
            'spec_con_mean': np.mean(spec_con_mean),
            'spec_con_std': np.mean(spec_con_std),
            'num_silence_segments' : num_silence_segments
        }

        # for i in range(40):
        #     features[f'mfcc_{i}'] = mfccs_flat[i]

        for i in range(30):
            # features[f'mfcc{i}'] = np.mean(mfccs[i])
            features[f'mfcc_mean{i}'] = mfcc_means[i]
            features[f'mfcc_std_{i}'] = mfcc_stds[i]
            # features[f'mfcc_kurtosis_{i}'] = mfcc_kurtosis[i]
            features[f'skewness_mean_{i}'] = skewness_means[i]

        # for i in range(40):
        #     features[f'mfcc_fbe{i}'] = fbes[i]

        return features


