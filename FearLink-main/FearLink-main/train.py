import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import tensorflow as tf
import numpy as np
from scipy.signal import resample
import pickle
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt
import sys

# WESAD path
data_dir = "C:\\Users\\kurno\\Downloads\\WESAD\\WESAD"
log_file = "training_log.txt"

# Log function with UTF-8
def log(msg):
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(msg + '\n')
    except Exception as e:
        print(f"Log file error: {e}")
    try:
        sys.stdout.write(msg + '\n')
        sys.stdout.flush()
    except UnicodeEncodeError:
        sys.stdout.write(msg.encode('ascii', 'ignore').decode('ascii') + '\n')
        sys.stdout.flush()

# Load and preprocess one subject
def load_wesad_subject(subject_file):
    with open(subject_file, 'rb') as f:
        data = pickle.load(f, encoding='latin1')
    
    ppg = data['signal']['wrist']['BVP']
    gsr = data['signal']['wrist']['EDA']
    accel = data['signal']['wrist']['ACC']
    labels = data['label']
    
    ppg = resample(ppg, int(len(ppg) * 10 / 64))
    gsr = resample(gsr, int(len(gsr) * 10 / 4))
    accel = resample(accel, int(len(accel) * 30 / 32), axis=0)
    
    window_size_ppg = 50
    window_size_accel = 150
    step = 25
    
    ppg_windows, gsr_windows, accel_windows, label_windows = [], [], [], []
    for start in range(0, len(ppg) - window_size_ppg, step):
        end = start + window_size_ppg
        if end > len(ppg) or end > len(gsr):
            break
        
        accel_start = start * 3
        accel_end = accel_start + window_size_accel
        if accel_end > len(accel):
            break
        
        label_start = start * 70
        label_end = label_start + 3500
        if label_end > len(labels):
            break
        label_segment = labels[label_start:label_end]
        label = 1 if np.mean(label_segment == 1) > 0.5 else 0
        
        ppg_windows.append(ppg[start:end].reshape(50, 1))
        gsr_windows.append(gsr[start:end].reshape(50, 1))
        accel_windows.append(accel[accel_start:accel_end])
        label_windows.append(label)
    
    return (np.array(ppg_windows, dtype=np.float32), np.array(gsr_windows, dtype=np.float32), 
            np.array(accel_windows, dtype=np.float32), np.array(label_windows, dtype=np.int32))

# Load all subjects
log("Loading data...")
ppg_data, gsr_data, accel_data, labels = [], [], [], []
for subject in range(1, 18):
    file = os.path.join(data_dir, f"S{subject}", f"S{subject}.pkl")
    if not os.path.exists(file):
        log(f"Warning: {file} not found, skipping...")
        continue
    log(f"Loading S{subject}...")
    p, g, a, l = load_wesad_subject(file)
    log(f"S{subject}: PPG shape={p.shape}, GSR shape={g.shape}, ACC shape={a.shape}, Labels shape={l.shape}")
    ppg_data.append(p)
    gsr_data.append(g)
    accel_data.append(a)
    labels.append(l)

# Truncate and stack
min_samples = min(arr.shape[0] for arr in labels)
labels = np.concatenate([arr[:min_samples] for arr in labels])
ppg_data = np.vstack([arr[:min_samples] for arr in ppg_data])
gsr_data = np.vstack([arr[:min_samples] for arr in gsr_data])
accel_data = np.vstack([arr[:min_samples] for arr in accel_data])

# Oversample Fear
log("Oversampling Fear class...")
fear_mask = labels == 1
no_fear_mask = labels == 0
fear_ppg = ppg_data[fear_mask]
fear_gsr = gsr_data[fear_mask]
fear_accel = accel_data[fear_mask]
fear_labels = labels[fear_mask]
no_fear_ppg = ppg_data[no_fear_mask]
no_fear_gsr = gsr_data[no_fear_mask]
no_fear_accel = accel_data[no_fear_mask]
no_fear_labels = labels[no_fear_mask]

repeat_factor = len(no_fear_labels) // len(fear_labels)
fear_ppg = np.tile(fear_ppg, (repeat_factor, 1, 1))
fear_gsr = np.tile(fear_gsr, (repeat_factor, 1, 1))
fear_accel = np.tile(fear_accel, (repeat_factor, 1, 1))
fear_labels = np.tile(fear_labels, repeat_factor)

ppg_data = np.vstack([no_fear_ppg, fear_ppg])
gsr_data = np.vstack([no_fear_gsr, fear_gsr])
accel_data = np.vstack([no_fear_accel, fear_accel])
labels = np.concatenate([no_fear_labels, fear_labels])

# Normalize
def normalize(data):
    min_val = np.min(data)
    max_val = np.max(data)
    return (data - min_val) / (max_val - min_val + 1e-8), min_val, max_val

ppg_data, ppg_min, ppg_max = normalize(ppg_data)
gsr_data, gsr_min, gsr_max = normalize(gsr_data)
accel_data, accel_min, accel_max = normalize(accel_data)

# Diagnostics
log("\n=== Data Diagnostics ===")
log(f"PPG shape: {ppg_data.shape}, GSR: {gsr_data.shape}, Accel: {accel_data.shape}, Labels: {labels.shape}")
log(f"PPG min/max: {ppg_min:.2f}, {ppg_max:.2f}")
log(f"GSR min/max: {gsr_min:.2f}, {gsr_max:.2f}")
log(f"Accel min/max: {accel_min:.2f}, {accel_max:.2f}")
log(f"PPG mean/std: {np.mean(ppg_data):.4f}, {np.std(ppg_data):.4f}")
log(f"GSR mean/std: {np.mean(gsr_data):.4f}, {np.std(gsr_data):.4f}")
log(f"Accel mean/std: {np.mean(accel_data):.4f}, {np.std(accel_data):.4f}")
log(f"Class Balance: No-Fear={np.sum(labels == 0)}, Fear={np.sum(labels == 1)}")

# Split data
X = list(zip(ppg_data, gsr_data, accel_data))
y = labels
X_train, X_temp, y_train, y_temp = train_test_split(X, y, train_size=0.7, shuffle=True, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, train_size=0.5, shuffle=True, random_state=42)

ppg_train = np.array([x[0] for x in X_train], dtype=np.float32)
gsr_train = np.array([x[1] for x in X_train], dtype=np.float32)
accel_train = np.array([x[2] for x in X_train], dtype=np.float32)
ppg_val = np.array([x[0] for x in X_val], dtype=np.float32)
gsr_val = np.array([x[1] for x in X_val], dtype=np.float32)
accel_val = np.array([x[2] for x in X_val], dtype=np.float32)
ppg_test = np.array([x[0] for x in X_test], dtype=np.float32)
gsr_test = np.array([x[1] for x in X_test], dtype=np.float32)
accel_test = np.array([x[2] for x in X_test], dtype=np.float32)
y_train, y_val, y_test = np.array(y_train), np.array(y_val), np.array(y_test)

# Model
layers = tf.keras.layers
Model = tf.keras.Model

def build_on_device_model():
    ppg_input = layers.Input(shape=(50, 1), name="ppg")
    gsr_input = layers.Input(shape=(50, 1), name="gsr")
    accel_input = layers.Input(shape=(150, 3), name="accel")

    ppg_cnn = layers.Conv1D(16, 3, activation="relu", padding="same")(ppg_input)
    ppg_cnn = layers.MaxPooling1D(2)(ppg_cnn)
    gsr_cnn = layers.Conv1D(16, 3, activation="relu", padding="same")(gsr_input)
    gsr_cnn = layers.MaxPooling1D(2)(gsr_cnn)
    accel_cnn = layers.Conv1D(16, 3, activation="relu", padding="same")(accel_input)
    accel_cnn = layers.MaxPooling1D(2)(accel_cnn)

    ppg_flat = layers.Flatten()(ppg_cnn)
    gsr_flat = layers.Flatten()(gsr_cnn)
    accel_flat = layers.Flatten()(accel_cnn)
    combined = layers.Concatenate()([ppg_flat, gsr_flat, accel_flat])

    dense1 = layers.Dense(64, activation="relu")(combined)
    dense2 = layers.Dense(32, activation="relu")(dense1)
    dense2 = layers.Dropout(0.1)(dense2)
    output = layers.Dense(1, activation="sigmoid")(dense2)  # Predicts "no-fear"

    model = Model(inputs=[ppg_input, gsr_input, accel_input], outputs=output)
    return model

# Callbacks
lr_schedule = tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=1e-6, verbose=1)
early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True, verbose=1)

# Train
log("Training model...")
model = build_on_device_model()
model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.0005),
              loss="binary_crossentropy", metrics=["accuracy"])
model.summary(print_fn=lambda x: log(x))

history = model.fit(
    [ppg_train, gsr_train, accel_train], y_train,
    epochs=50,
    batch_size=16,
    validation_data=([ppg_val, gsr_val, accel_val], y_val),
    callbacks=[lr_schedule, early_stopping]
)

# Plot training history
plt.figure(figsize=(12, 4))
plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='Train Acc')
plt.plot(history.history['val_accuracy'], label='Val Acc')
plt.title('Model Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()
plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='Train Loss')
plt.plot(history.history['val_loss'], label='Val Loss')
plt.title('Model Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.savefig('training_history.png')
plt.close()

# Classification report
y_pred = model.predict([ppg_test, gsr_test, accel_test])
y_pred_binary = (y_pred > 0.5).astype(int)
log("\nClassification Report:")
log(classification_report(y_test, y_pred_binary, target_names=["No-Fear", "Fear"]))

# Test fear vs calm
def normalize_test(data, min_val, max_val):
    return (data - min_val) / (max_val - min_val + 1e-8)

ppg_fear = np.linspace(140, 180, 50).reshape(1, 50, 1) / 200  # Stronger stress
gsr_fear = np.linspace(10.0, 15.0, 50).reshape(1, 50, 1) / 20  # Peak GSR
accel_fear = np.random.uniform(1.5, 3.0, (1, 150, 3)) / 4
ppg_fear_norm = normalize_test(ppg_fear, ppg_min, ppg_max).astype(np.float32)
gsr_fear_norm = normalize_test(gsr_fear, gsr_min, gsr_max).astype(np.float32)
accel_fear_norm = normalize_test(accel_fear, accel_min, accel_max).astype(np.float32)

ppg_calm = np.full((1, 50, 1), 70) / 200
gsr_calm = np.full((1, 50, 1), 0.5) / 20
accel_calm = np.random.uniform(0.0, 0.5, (1, 150, 3)) / 4
ppg_calm_norm = normalize_test(ppg_calm, ppg_min, ppg_max).astype(np.float32)
gsr_calm_norm = normalize_test(gsr_calm, gsr_min, gsr_max).astype(np.float32)
accel_calm_norm = normalize_test(accel_calm, accel_min, accel_max).astype(np.float32)

fear_raw = model.predict([ppg_fear_norm, gsr_fear_norm, accel_fear_norm])[0][0]
calm_raw = model.predict([ppg_calm_norm, gsr_calm_norm, accel_calm_norm])[0][0]
fear_score = 1 - fear_raw
calm_score = 1 - calm_raw

log(f"\nKeras Fear Raw (sigmoid): {fear_raw:.4f}")
log(f"Keras Calm Raw (sigmoid): {calm_raw:.4f}")
log(f"Fear Score: {fear_score * 100:.2f}%")
log(f"Calm Score: {calm_score * 100:.2f}%")

# Convert to TFLite
log("Converting to TFLite...")
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.target_spec.supported_types = [tf.float32]
converter.inference_input_type = tf.float32
converter.inference_output_type = tf.float32
tflite_model = converter.convert()
with open("model.tflite", "wb") as f:
    f.write(tflite_model)

size = os.path.getsize("model.tflite") / 1024
log(f"Model Size: {size:.2f} KB")

# TFLite diagnostics
interpreter = tf.lite.Interpreter(model_path="model.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

log("\nTFLite Input Details:")
for i, detail in enumerate(input_details):
    log(f"Input {i}: {detail['name']}, Shape: {detail['shape']}")
log(f"TFLite Output Shape: {output_details[0]['shape']}")

# TFLite predictions with explicit mapping
log("Running TFLite predictions...")
interpreter = tf.lite.Interpreter(model_path="model.tflite")
interpreter.allocate_tensors()
input_map = {detail['name']: i for i, detail in enumerate(input_details)}
interpreter.set_tensor(input_map['serving_default_accel:0'], accel_fear_norm)
interpreter.set_tensor(input_map['serving_default_gsr:0'], gsr_fear_norm)
interpreter.set_tensor(input_map['serving_default_ppg:0'], ppg_fear_norm)
interpreter.invoke()
fear_raw_tflite = interpreter.get_tensor(output_details[0]['index'])[0][0]
fear_score_tflite = 1 - fear_raw_tflite

interpreter = tf.lite.Interpreter(model_path="model.tflite")
interpreter.allocate_tensors()
interpreter.set_tensor(input_map['serving_default_accel:0'], accel_calm_norm)
interpreter.set_tensor(input_map['serving_default_gsr:0'], gsr_calm_norm)
interpreter.set_tensor(input_map['serving_default_ppg:0'], ppg_calm_norm)
interpreter.invoke()
calm_raw_tflite = interpreter.get_tensor(output_details[0]['index'])[0][0]
calm_score_tflite = 1 - calm_raw_tflite

log(f"TFLite Fear Raw (sigmoid): {fear_raw_tflite:.4f}")
log(f"TFLite Calm Raw (sigmoid): {calm_raw_tflite:.4f}")
log(f"TFLite Fear Score: {fear_score_tflite * 100:.2f}%")
log(f"TFLite Calm Score: {calm_score_tflite * 100:.2f}%")