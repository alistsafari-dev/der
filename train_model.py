import os
import numpy as np
import librosa
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, LSTM, Bidirectional
from tensorflow.keras.utils import to_categorical

# Path to the dataset
DATASET_PATH = 'dataset'

# Emotions we want to classify
EMOTIONS = {
    '03': 'happy',
    '04': 'sad',
    '05': 'angry'
}

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

def load_data(dataset_path):
    """Loads data from the dataset folder."""
    features, labels = [], []
    for actor_folder in os.listdir(dataset_path):
        actor_path = os.path.join(dataset_path, actor_folder)
        if os.path.isdir(actor_path):
            for file_name in os.listdir(actor_path):
                try:
                    emotion_code = file_name.split('-')[2]
                    if emotion_code in EMOTIONS:
                        file_path = os.path.join(actor_path, file_name)
                        feature = extract_features(file_path)
                        if feature is not None:
                            features.append(feature)
                            labels.append(EMOTIONS[emotion_code])
                except IndexError:
                    # Ignore files with incorrect naming convention
                    continue
    return np.array(features), np.array(labels)

# 1. Load data
print("Loading data...")
X, y = load_data(DATASET_PATH)
if len(X) == 0:
    print("No data loaded. Please check the dataset path and format.")
    exit()

# 2. Encode labels
le = LabelEncoder()
y_encoded = to_categorical(le.fit_transform(y))

# 3. Split data
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

# Reshape for LSTM layer (if using)
# X_train = np.expand_dims(X_train, axis=2)
# X_test = np.expand_dims(X_test, axis=2)

# 4. Build the model
model = Sequential([
    Dense(256, input_shape=(X_train.shape[1],), activation='relu'),
    Dropout(0.5),
    Dense(128, activation='relu'),
    Dropout(0.5),
    Dense(64, activation='relu'),
    Dropout(0.5),
    Dense(y_train.shape[1], activation='softmax')
])

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
model.summary()

# 5. Train the model
print("\nTraining model...")
history = model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=100, batch_size=32)

# 6. Save the model
model.save('emotion_model.h5')
print("\nModel saved as emotion_model.h5")

# Save the label encoder
import pickle
with open('label_encoder.pkl', 'wb') as f:
    pickle.dump(le, f)
print("Label encoder saved as label_encoder.pkl")
