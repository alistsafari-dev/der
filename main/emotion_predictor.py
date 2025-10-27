import numpy as np
import librosa
import pickle
from tensorflow.keras.models import load_model

# Load the trained model
MODEL_PATH = 'emotion_model.h5'
LABEL_ENCODER_PATH = 'label_encoder.pkl'

try:
    model = load_model(MODEL_PATH)
    with open(LABEL_ENCODER_PATH, 'rb') as f:
        le = pickle.load(f)
    print("Model and label encoder loaded successfully.")
except Exception as e:
    print(f"Error loading model or label encoder: {e}")
    model = None
    le = None

def extract_features(file_path):
    """Extracts MFCC features from an audio file."""
    try:
        audio, sample_rate = librosa.load(file_path, res_type='kaiser_fast')
        mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=40)
        mfccs_processed = np.mean(mfccs.T, axis=0)
        return mfccs_processed
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def predict_emotion(file_path):
    """Predicts the emotion of an audio file."""
    if model is None or le is None:
        return {"error": "Model not loaded."}

    feature = extract_features(file_path)
    if feature is None:
        return {"error": "Could not process audio file."}

    feature = np.expand_dims(feature, axis=0) # Reshape for the model

    predictions = model.predict(feature)[0]

    # Get the probabilities for each class
    results = {}
    for i, emotion in enumerate(le.classes_):
        results[emotion] = round(float(predictions[i]) * 100, 2)

    return results
