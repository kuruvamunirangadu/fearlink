import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer
from scipy.signal import butter, filtfilt
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import tensorflow as tf
import keras
from keras.models import Sequential
from keras.layers import Dense, Conv1D, LSTM, Flatten, Dropout, Input, concatenate
from keras.utils import to_categorical

# 🟢 Step 1: Data Preprocessing (Sensor & Text)

# Sensor Data Preprocessing
def butter_lowpass_filter(data, cutoff=0.3, fs=700, order=5):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return filtfilt(b, a, data)

def load_wesad_data(file_path):
    df = pd.read_csv(file_path)
    
    # Ensure columns exist and apply filtering
    if 'EDA' in df.columns and 'TEMP' in df.columns and 'Label' in df.columns:
        df['EDA'] = butter_lowpass_filter(df['EDA'])
        df['TEMP'] = butter_lowpass_filter(df['TEMP'])
    
    scaler = StandardScaler()
    features = scaler.fit_transform(df.drop(columns=['Label']).values)
    
    labels = to_categorical(df['Label'].values, num_classes=4)
    
    # Reshape for CNN-LSTM (assuming 100 time steps, 8 features)
    n_samples = len(features) // 100
    features = features[:n_samples * 100].reshape((n_samples, 100, 8))
    
    return features, labels

# Replace with your actual WESAD dataset path
sensor_data, sensor_labels = load_wesad_data('wesad_dataset.csv')

# Text Data Preprocessing
tokenizer = AutoTokenizer.from_pretrained("huawei-noah/TinyBERT_4L_312D")
def preprocess_text(sentences, max_length=128):
    encodings = tokenizer(sentences, padding=True, truncation=True, max_length=max_length, return_tensors="tf")
    return encodings['input_ids'], encodings['attention_mask']

# Example text data (expanded to match sensor data size for demo)
n_samples = len(sensor_data)
text_sentences = ["I feel very anxious today", "I am relaxed and happy"] * (n_samples // 2 + 1)
text_sentences = text_sentences[:n_samples]  # Match sensor data length
text_input_ids, text_attention_masks = preprocess_text(text_sentences)

# 🟢 Step 2: Model Definition

# CNN + LSTM for Sensor Signals
def build_sensor_model(input_shape):
    model = Sequential([
        Input(shape=input_shape),
        Conv1D(64, kernel_size=3, activation='relu', padding='same'),
        Conv1D(128, kernel_size=3, activation='relu', padding='same'),
        LSTM(64, return_sequences=True),
        LSTM(32),
        Flatten(),
        Dense(64, activation='relu'),
        Dropout(0.3),
        Dense(4, activation='softmax')
    ])
    return model

sensor_model = build_sensor_model((100, 8))

# TinyBERT for Text-Based Stress Detection (Keras-compatible wrapper)
def build_text_model():
    input_ids = Input(shape=(128,), dtype=tf.int32)
    attention_mask = Input(shape=(128,), dtype=tf.int32)
    
    # Use TensorFlow-compatible TinyBERT
    bert_model = TFAutoModel.from_pretrained("huawei-noah/TinyBERT_4L_312D")
    bert_output = bert_model(input_ids=input_ids, attention_mask=attention_mask)[0][:, 0, :]
    
    x = Dense(64, activation='relu')(bert_output)
    output = Dense(4, activation='softmax')(x)
    
    return tf.keras.Model(inputs=[input_ids, attention_mask], outputs=output)

text_model = build_text_model()

# Hybrid Fusion Model
def hybrid_model(sensor_input_shape):
    # Sensor branch
    sensor_input = Input(shape=sensor_input_shape)
    sensor_output = build_sensor_model(sensor_input_shape)(sensor_input)
    
    # Text branch
    text_input_ids = Input(shape=(128,), dtype=tf.int32)
    text_attention_mask = Input(shape=(128,), dtype=tf.int32)
    text_output = text_model([text_input_ids, text_attention_mask])
    
    # Merge branches
    merged = concatenate([sensor_output, text_output])
    x = Dense(64, activation='relu')(merged)
    final_output = Dense(4, activation='softmax')(x)
    
    return tf.keras.Model(inputs=[sensor_input, text_input_ids, text_attention_mask], outputs=final_output)

hybrid = hybrid_model((100, 8))
hybrid.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# 🟢 Step 3: Train Hybrid Model
sensor_train, sensor_test, labels_train, labels_test = train_test_split(
    sensor_data, sensor_labels, test_size=0.2, random_state=42
)
text_train_ids, text_test_ids, text_train_masks, text_test_masks = train_test_split(
    text_input_ids, text_attention_masks, test_size=0.2, random_state=42
)

hybrid.fit(
    [sensor_train, text_train_ids, text_train_masks],
    labels_train,
    epochs=10,
    batch_size=32,
    validation_split=0.2
)

# 🟢 Step 4: Evaluation & Classification Report
labels_pred = hybrid.predict([sensor_test, text_test_ids, text_test_masks])
labels_pred_classes = np.argmax(labels_pred, axis=1)
labels_test_classes = np.argmax(labels_test, axis=1)

print("🔹 Classification Report for RKLS-StressDetect AI:")
print(classification_report(labels_test_classes, labels_pred_classes, target_names=["Baseline", "Stress", "Amusement", "Meditation"]))

# 🟢 Step 5: Convert for Edge AI (TFLite)
converter = tf.lite.TFLiteConverter.from_keras_model(hybrid)
tflite_model = converter.convert()
with open('RKLS-StressDetect.tflite', 'wb') as f:
    f.write(tflite_model)

print("✅ RKLS-StressDetect AI is trained and converted for Edge AI!")