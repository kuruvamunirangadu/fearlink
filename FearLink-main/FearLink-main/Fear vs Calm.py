import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import tensorflow as tf
import numpy as np

layers = tf.keras.layers
Model = tf.keras.Model

# Test inputs
# Fear scenario
ppg_fear = np.linspace(80, 120, 50).reshape(1, 50, 1)  # Heart rate spikes
gsr_fear = np.linspace(1.5, 3.0, 50).reshape(1, 50, 1)  # Sweat increases
accel_fear = np.random.uniform(0.5, 1.5, (1, 150, 3))  # Shaking

# Calm scenario
ppg_calm = np.full((1, 50, 1), 70)  # Steady 70 bpm
gsr_calm = np.full((1, 50, 1), 1.0)  # Low sweat
accel_calm = np.random.uniform(0.0, 0.2, (1, 150, 3))  # Barely moving

# Build model
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

    transformer = layers.Dense(64, activation="relu")(combined)
    transformer = layers.LayerNormalization()(transformer)

    output = layers.Dense(1, activation="sigmoid")(transformer)

    model = Model(inputs=[ppg_input, gsr_input, accel_input], outputs=output)
    model.compile(optimizer="adam", loss="binary_crossentropy", metrics=["accuracy"])
    return model

# Test it
model = build_on_device_model()
model.summary()

fear_score = model.predict([ppg_fear, gsr_fear, accel_fear])
calm_score = model.predict([ppg_calm, gsr_calm, accel_calm])

print(f"Fear Score: {fear_score[0][0] * 100:.2f}%")
print(f"Calm Score: {calm_score[0][0] * 100:.2f}%")