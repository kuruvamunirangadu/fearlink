import sys
import numpy as np
from scipy.signal import resample
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import tensorflow as tf

# Load your trained TensorFlow Lite model
interpreter = tf.lite.Interpreter(model_path="model.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Preprocessing functions
def preprocess_ppg(ppg_data):
    """
    Preprocess PPG data.
    - Input: List of 50 PPG values.
    - Output: Reshaped and normalized PPG data.
    """
    ppg_data = np.array(ppg_data, dtype=np.float32).reshape(1, 50, 1)
    ppg_data = (ppg_data - np.min(ppg_data)) / (np.max(ppg_data) - np.min(ppg_data))  # Normalize
    return ppg_data

def preprocess_gsr(gsr_data):
    """
    Preprocess GSR data.
    - Input: List of 50 GSR values.
    - Output: Reshaped and normalized GSR data.
    """
    gsr_data = np.array(gsr_data, dtype=np.float32).reshape(1, 50, 1)
    gsr_data = (gsr_data - np.min(gsr_data)) / (np.max(gsr_data) - np.min(gsr_data))  # Normalize
    return gsr_data

def preprocess_accel(accel_data):
    """
    Preprocess accelerometer data.
    - Input: List of 150 accelerometer values (50 timesteps × 3 axes).
    - Output: Reshaped and upsampled accelerometer data.
    """
    accel_data = np.array(accel_data, dtype=np.float32).reshape(50, 3)
    upsampled_accel = []
    for axis in range(3):  # Upsample each axis separately
        upsampled_axis = resample(accel_data[:, axis], 150)  # Upsample to 150 timesteps
        upsampled_accel.append(upsampled_axis)
    upsampled_accel = np.array(upsampled_accel).T  # Transpose to get shape (150, 3)
    upsampled_accel = upsampled_accel.reshape(1, 150, 3)  # Reshape to (1, 150, 3)
    return upsampled_accel

# Prediction function
def predict_stress(ppg_data, gsr_data, accel_data):
    """
    Predict stress status using the TensorFlow Lite model.
    - Input: Preprocessed PPG, GSR, and accelerometer data.
    - Output: Stress status and probability.
    """
    # Set input tensors
    interpreter.set_tensor(input_details[0]['index'], ppg_data)
    interpreter.set_tensor(input_details[1]['index'], gsr_data)
    interpreter.set_tensor(input_details[2]['index'], accel_data)

    # Run inference
    interpreter.invoke()
    output = interpreter.get_tensor(output_details[0]['index'])
    stress_prob = output[0][0]  # Probability of stress
    stress_status = "Stressed" if stress_prob > 0.5 else "Not Stressed"
    return stress_status, stress_prob

# PyQt5 Main Window
class StressDetectionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real-Time Stress Detection")
        self.setGeometry(100, 100, 600, 400)
        self.setStyleSheet("background-color: #f0f8ff;")  # Light blue background

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Title
        title = QLabel("Stress Detection System")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Input fields
        self.ppg_input = self.create_input_field("Enter PPG Data (50 values, comma-separated):", layout)
        self.gsr_input = self.create_input_field("Enter GSR Data (50 values, comma-separated):", layout)
        self.accel_input = self.create_input_field("Enter Accelerometer Data (150 values, comma-separated):", layout)

        # Predict button
        predict_button = QPushButton("Predict Stress")
        predict_button.setFont(QFont("Arial", 14))
        predict_button.setStyleSheet(
            "background-color: #3498db; color: white; padding: 10px; border-radius: 5px;"
        )
        predict_button.clicked.connect(self.on_predict)
        layout.addWidget(predict_button)

        # Result display
        self.result_label = QLabel()
        self.result_label.setFont(QFont("Arial", 16))
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet("color: #2ecc71;")
        layout.addWidget(self.result_label)

    def create_input_field(self, placeholder, layout):
        label = QLabel(placeholder)
        label.setFont(QFont("Arial", 12))
        label.setStyleSheet("color: #34495e;")
        layout.addWidget(label)

        input_field = QLineEdit()
        input_field.setFont(QFont("Arial", 12))
        input_field.setStyleSheet("padding: 5px; border: 1px solid #bdc3c7; border-radius: 5px;")
        layout.addWidget(input_field)
        return input_field

    def on_predict(self):
        try:
            # Get input data
            ppg_data = self.ppg_input.text().strip()
            gsr_data = self.gsr_input.text().strip()
            accel_data = self.accel_input.text().strip()

            # Check if inputs are empty
            if not ppg_data or not gsr_data or not accel_data:
                raise ValueError("Please fill in all input fields.")

            # Convert inputs to lists of floats
            ppg_data = list(map(float, ppg_data.split(',')))
            gsr_data = list(map(float, gsr_data.split(',')))
            accel_data = list(map(float, accel_data.split(',')))

            # Validate input lengths
            if len(ppg_data) != 50:
                raise ValueError(f"PPG data must have exactly 50 values. You entered {len(ppg_data)} values.")
            if len(gsr_data) != 50:
                raise ValueError(f"GSR data must have exactly 50 values. You entered {len(gsr_data)} values.")
            if len(accel_data) != 150:
                raise ValueError(f"Accelerometer data must have exactly 150 values. You entered {len(accel_data)} values.")

            # Preprocess data
            ppg_data = preprocess_ppg(ppg_data)
            gsr_data = preprocess_gsr(gsr_data)
            accel_data = preprocess_accel(accel_data)

            # Predict stress
            stress_status, stress_prob = predict_stress(ppg_data, gsr_data, accel_data)
            self.result_label.setText(f"Result: {stress_status} (Probability: {stress_prob:.2f})")
        except ValueError as e:
            QMessageBox.critical(self, "Input Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {str(e)}")

# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StressDetectionApp()
    window.show()
    sys.exit(app.exec_())