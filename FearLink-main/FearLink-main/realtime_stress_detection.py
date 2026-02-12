import sys
import numpy as np
import tensorflow as tf
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QSlider
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QTimer
import random

# Load your trained TensorFlow Lite model
interpreter = tf.lite.Interpreter(model_path="model.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Print input details for debugging
print("Input Details:", input_details)

# Function to generate synthetic PPG data
def generate_ppg():
    """
    Generate synthetic PPG data (50 values) with a periodic waveform.
    """
    t = np.linspace(0, 2 * np.pi, 50)
    ppg_data = 100 + 20 * np.sin(t)  # Simulate a periodic PPG signal
    return ppg_data.tolist()

# Function to generate synthetic GSR data
def generate_gsr():
    """
    Generate synthetic GSR data (50 values) with slow variations.
    """
    gsr_data = [2.0 + 0.1 * np.sin(i * 0.1) for i in range(50)]  # Simulate slow GSR variations
    return gsr_data

# Function to generate synthetic accelerometer data
def generate_accel():
    """
    Generate synthetic accelerometer data (150 timesteps × 3 axes = 450 values).
    - Simulate small movements in X, Y, Z axes.
    """
    accel_data = []
    for _ in range(150):
        accel_data.extend([1.0 + 0.1 * random.uniform(-1, 1) for _ in range(3)])  # Simulate small movements
    return accel_data

# Preprocessing functions
def preprocess_ppg(ppg_data):
    """
    Preprocess PPG data.
    - Input: List of 50 PPG values.
    - Output: Reshaped and normalized PPG data with shape (1, 50, 1).
    """
    ppg_data = np.array(ppg_data, dtype=np.float32).reshape(1, 50, 1)  # Reshape to (1, 50, 1)
    ppg_data = (ppg_data - np.min(ppg_data)) / (np.max(ppg_data) - np.min(ppg_data))  # Normalize
    return ppg_data

def preprocess_gsr(gsr_data):
    """
    Preprocess GSR data.
    - Input: List of 50 GSR values.
    - Output: Reshaped and normalized GSR data with shape (1, 50, 1).
    """
    gsr_data = np.array(gsr_data, dtype=np.float32).reshape(1, 50, 1)  # Reshape to (1, 50, 1)
    gsr_data = (gsr_data - np.min(gsr_data)) / (np.max(gsr_data) - np.min(gsr_data))  # Normalize
    return gsr_data

def preprocess_accel(accel_data):
    """
    Preprocess accelerometer data.
    - Input: List of 450 values (150 timesteps × 3 axes).
    - Output: Reshaped accelerometer data with shape (1, 150, 3).
    """
    accel_data = np.array(accel_data, dtype=np.float32).reshape(1, 150, 3)  # Reshape to (1, 150, 3)
    return accel_data

# Prediction function with adjustable threshold
def predict_stress(accel_data, gsr_data, ppg_data, threshold=0.5):
    """
    Predict stress status using the TensorFlow Lite model.
    - Input: Preprocessed accelerometer, GSR, and PPG data.
    - Output: Stress status and probability.
    """
    # Set input tensors
    interpreter.set_tensor(input_details[0]['index'], accel_data)  # Accelerometer data
    interpreter.set_tensor(input_details[1]['index'], gsr_data)   # GSR data
    interpreter.set_tensor(input_details[2]['index'], ppg_data)   # PPG data

    # Run inference
    interpreter.invoke()
    output = interpreter.get_tensor(output_details[0]['index'])
    stress_prob = 1 / (1 + np.exp(-output[0][0]))  # Sigmoid function

    # Adjust threshold for "Fear" class
    stress_status = "Fear" if stress_prob > threshold else "No-Fear"
    return stress_status, stress_prob

# PyQt5 Main Window
class StressDetectionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real-Time Stress Detection")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #f0f8ff;")  # Light blue background

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Title
        title = QLabel("Real-Time Stress Detection System")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Sensor data labels
        self.ppg_label = QLabel("PPG Data: Generating...")
        self.gsr_label = QLabel("GSR Data: Generating...")
        self.accel_label = QLabel("Accelerometer Data: Generating...")
        self.result_label = QLabel("Result: Waiting for prediction...")

        # Set font and style for labels
        for label in [self.ppg_label, self.gsr_label, self.accel_label, self.result_label]:
            label.setFont(QFont("Arial", 14))
            label.setStyleSheet("color: #34495e; padding: 10px; border-radius: 5px; background-color: #ffffff;")
            layout.addWidget(label)

        # Threshold slider
        self.threshold_label = QLabel("Decision Threshold: 0.5")
        self.threshold_label.setFont(QFont("Arial", 14))
        self.threshold_label.setStyleSheet("color: #34495e; padding: 10px; border-radius: 5px; background-color: #ffffff;")
        layout.addWidget(self.threshold_label)

        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setMinimum(0)
        self.threshold_slider.setMaximum(100)
        self.threshold_slider.setValue(50)  # Default threshold = 0.5
        self.threshold_slider.valueChanged.connect(self.update_threshold)
        layout.addWidget(self.threshold_slider)

        # Start button
        self.start_button = QPushButton("Start Real-Time Prediction")
        self.start_button.setFont(QFont("Arial", 16))
        self.start_button.setStyleSheet(
            "background-color: #3498db; color: white; padding: 15px; border-radius: 10px;"
        )
        self.start_button.clicked.connect(self.start_real_time_prediction)
        layout.addWidget(self.start_button)

        # Stop button
        self.stop_button = QPushButton("Stop Real-Time Prediction")
        self.stop_button.setFont(QFont("Arial", 16))
        self.stop_button.setStyleSheet(
            "background-color: #e74c3c; color: white; padding: 15px; border-radius: 10px;"
        )
        self.stop_button.clicked.connect(self.stop_real_time_prediction)
        self.stop_button.setEnabled(False)  # Disable initially
        layout.addWidget(self.stop_button)

        # Timer for real-time updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_predictions)

        # Threshold value
        self.threshold = 0.5

    def update_threshold(self):
        """
        Update the decision threshold based on the slider value.
        """
        self.threshold = self.threshold_slider.value() / 100.0
        self.threshold_label.setText(f"Decision Threshold: {self.threshold:.2f}")

    def start_real_time_prediction(self):
        """
        Start real-time prediction updates every 5 seconds.
        """
        self.timer.start(5000)  # Update every 5 seconds
        self.start_button.setEnabled(False)  # Disable the start button
        self.stop_button.setEnabled(True)  # Enable the stop button
        self.start_button.setText("Real-Time Prediction Running...")

    def stop_real_time_prediction(self):
        """
        Stop real-time prediction updates.
        """
        self.timer.stop()
        self.start_button.setEnabled(True)  # Enable the start button
        self.stop_button.setEnabled(False)  # Disable the stop button
        self.start_button.setText("Start Real-Time Prediction")

    def update_predictions(self):
        """
        Generate synthetic data, preprocess it, and update the predictions.
        """
        try:
            # Generate synthetic data
            ppg_data = generate_ppg()
            gsr_data = generate_gsr()
            accel_data = generate_accel()

            # Update sensor data labels
            self.ppg_label.setText(f"PPG Data: {ppg_data[:5]}...")  # Show first 5 values
            self.gsr_label.setText(f"GSR Data: {gsr_data[:5]}...")  # Show first 5 values
            self.accel_label.setText(f"Accelerometer Data: {accel_data[:15]}...")  # Show first 15 values (5 timesteps × 3 axes)

            # Preprocess data
            ppg_data = preprocess_ppg(ppg_data)
            gsr_data = preprocess_gsr(gsr_data)
            accel_data = preprocess_accel(accel_data)

            # Predict stress with adjustable threshold
            stress_status, stress_prob = predict_stress(accel_data, gsr_data, ppg_data, self.threshold)
            self.result_label.setText(f"Result: {stress_status} (Probability: {stress_prob:.2f})")
        except Exception as e:
            self.result_label.setText(f"Error: {str(e)}")

# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StressDetectionApp()
    window.show()
    sys.exit(app.exec_())