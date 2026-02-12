import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import sys
import numpy as np
import tensorflow as tf
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, 
                             QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import QTimer, Qt, QDateTime
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis, QDateTimeAxis

# Load TFLite model
interpreter = tf.lite.Interpreter(model_path="model.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Normalize function (match training ranges: PPG -1643 to 1772, GSR 0.04 to 15.94, Accel -190 to 173)
def normalize(data, min_val, max_val):
    return (data - min_val) / (max_val - min_val + 1e-8)

# Generate realistic sensor data
def generate_sensor_data():
    mode = np.random.choice(["calm", "fear", "stressed", "random"], p=[0.3, 0.3, 0.3, 0.1])  # Balanced mix
    if mode == "calm":
        ppg = np.full((1, 50, 1), np.random.uniform(60, 80))  # BPM
        gsr = np.full((1, 50, 1), np.random.uniform(0.5, 1.5))  # µS
        accel = np.random.uniform(0.0, 0.5, (1, 150, 3))  # m/s²
    elif mode == "fear":
        ppg = np.linspace(100, 140, 50).reshape(1, 50, 1)
        gsr = np.linspace(5.0, 10.0, 50).reshape(1, 50, 1)
        accel = np.random.uniform(1.0, 2.0, (1, 150, 3))
    elif mode == "stressed":
        ppg = np.linspace(140, 180, 50).reshape(1, 50, 1)
        gsr = np.linspace(10.0, 15.0, 50).reshape(1, 50, 1)
        accel = np.random.uniform(2.0, 3.0, (1, 150, 3))
    else:  # random
        ppg = np.random.uniform(60, 180, (1, 50, 1))
        gsr = np.random.uniform(0.5, 15.0, (1, 50, 1))
        accel = np.random.uniform(0.0, 3.0, (1, 150, 3))
    
    # Normalize to training ranges
    ppg_norm = normalize(ppg, -1643, 1772).astype(np.float32)
    gsr_norm = normalize(gsr, 0.04, 15.94).astype(np.float32)
    accel_norm = normalize(accel, -190, 173).astype(np.float32)
    return ppg, gsr, accel, ppg_norm, gsr_norm, accel_norm, mode

# Predict with TFLite
def predict_fear(ppg, gsr, accel):
    input_map = {detail['name']: detail['index'] for detail in input_details}
    interpreter.set_tensor(input_map['serving_default_accel:0'], accel)
    interpreter.set_tensor(input_map['serving_default_gsr:0'], gsr)
    interpreter.set_tensor(input_map['serving_default_ppg:0'], ppg)
    interpreter.invoke()
    fear_score = 1 - interpreter.get_tensor(output_details[0]['index'])[0][0]  # Invert: 1 = fear
    return fear_score * 100

# Dashboard
class FearDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FearSense Live Dashboard")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("background-color: #F0F4F8;")  # Light, fresh blue-gray

        # Main widget and layout
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # Header
        header = QLabel("FearSense Live Dashboard", self)
        header.setFont(QFont("Arial", 28, QFont.Bold))
        header.setStyleSheet("color: #1E88E5; padding: 15px; background-color: #FFFFFF; border-radius: 10px;")
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)

        # Main content layout
        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)

        # Left panel (sensors + table)
        left_panel = QVBoxLayout()
        content_layout.addLayout(left_panel, stretch=1)

        # Sensor displays
        sensor_style = "color: #1565C0; background-color: #E3F2FD; padding: 15px; border-radius: 8px; font: 18pt Arial;"
        self.ppg_label = QLabel("PPG: -- bpm", self)
        self.ppg_label.setStyleSheet(sensor_style)
        left_panel.addWidget(self.ppg_label)

        self.gsr_label = QLabel("GSR: -- µS", self)
        self.gsr_label.setStyleSheet(sensor_style)
        left_panel.addWidget(self.gsr_label)

        self.accel_label = QLabel("Accel: -- m/s²", self)
        self.accel_label.setStyleSheet(sensor_style)
        left_panel.addWidget(self.accel_label)

        # Table for live data
        self.data_table = QTableWidget(self)
        self.data_table.setColumnCount(5)
        self.data_table.setHorizontalHeaderLabels(["Time", "PPG (bpm)", "GSR (µS)", "Accel (m/s²)", "Fear %"])
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.data_table.setStyleSheet("""
            QTableWidget { background-color: #FFFFFF; font: 14pt Arial; color: #1976D2; border: none; }
            QHeaderView::section { background-color: #BBDEFB; color: #0D47A1; padding: 5px; font: bold 14pt Arial; }
        """)
        left_panel.addWidget(self.data_table)

        # Right panel (chart + status)
        right_panel = QVBoxLayout()
        content_layout.addLayout(right_panel, stretch=1)

        # Live fear graph (Line chart for time series)
        self.fear_series = QLineSeries()
        self.fear_series.setPen(QColor("#42A5F5"))
        self.chart = QChart()
        self.chart.addSeries(self.fear_series)
        self.chart.setTitle("Fear Level Over Time")
        self.chart.setTitleFont(QFont("Arial", 18, QFont.Bold))
        self.chart.setBackgroundBrush(QColor("#E3F2FD"))

        self.time_axis = QDateTimeAxis()
        self.time_axis.setFormat("hh:mm:ss")
        self.time_axis.setTitleText("Time")
        self.chart.addAxis(self.time_axis, Qt.AlignBottom)
        self.fear_series.attachAxis(self.time_axis)

        self.fear_axis = QValueAxis()
        self.fear_axis.setRange(0, 100)
        self.fear_axis.setTitleText("Fear %")
        self.fear_axis.setLabelFormat("%.0f")
        self.chart.addAxis(self.fear_axis, Qt.AlignLeft)
        self.fear_series.attachAxis(self.fear_axis)

        self.chart_view = QChartView(self.chart)
        self.chart_view.setMinimumSize(500, 400)
        right_panel.addWidget(self.chart_view)

        # Status badge
        self.status_label = QLabel("Status: --", self)
        self.status_label.setFont(QFont("Arial", 20, QFont.Bold))
        self.status_label.setStyleSheet("color: #FFFFFF; background-color: #81C784; padding: 15px; border-radius: 10px;")
        self.status_label.setAlignment(Qt.AlignCenter)
        right_panel.addWidget(self.status_label)

        # Avg Fear
        self.avg_label = QLabel("Avg Fear: --%", self)
        self.avg_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.avg_label.setStyleSheet("color: #FFFFFF; background-color: #64B5F6; padding: 10px; border-radius: 8px;")
        self.avg_label.setAlignment(Qt.AlignCenter)
        right_panel.addWidget(self.avg_label)

        # Stretch
        main_layout.addStretch()

        # Timer for 5-second updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_dashboard)
        self.timer.start(5000)

        # Data storage
        self.fear_history = []
        self.time_history = []
        self.update_dashboard()

    def update_dashboard(self):
        ppg, gsr, accel, ppg_norm, gsr_norm, accel_norm, mode = generate_sensor_data()
        
        # Raw values for display
        ppg_val = np.mean(ppg[0, :, 0])
        gsr_val = np.mean(gsr[0, :, 0])
        accel_val = np.mean(np.linalg.norm(accel[0], axis=1))
        
        self.ppg_label.setText(f"PPG: {ppg_val:.1f} bpm")
        self.gsr_label.setText(f"GSR: {gsr_val:.2f} µS")
        self.accel_label.setText(f"Accel: {accel_val:.2f} m/s²")

        # Predict fear
        fear_percent = predict_fear(ppg_norm, gsr_norm, accel_norm)

        # Status logic
        if fear_percent > 70:
            status = "Stressed"
            self.status_label.setStyleSheet("color: #FFFFFF; background-color: #EF5350; padding: 15px; border-radius: 10px;")
        elif fear_percent > 30:
            status = "Fear"
            self.status_label.setStyleSheet("color: #FFFFFF; background-color: #FFB300; padding: 15px; border-radius: 10px;")
        else:
            status = "Calm"
            self.status_label.setStyleSheet("color: #FFFFFF; background-color: #81C784; padding: 15px; border-radius: 10px;")
        self.status_label.setText(f"Status: {status}")

        # Add to table
        current_time = QDateTime.currentDateTime().toString("hh:mm:ss")
        row = self.data_table.rowCount()
        self.data_table.insertRow(row)
        self.data_table.setItem(row, 0, QTableWidgetItem(current_time))
        self.data_table.setItem(row, 1, QTableWidgetItem(f"{ppg_val:.1f}"))
        self.data_table.setItem(row, 2, QTableWidgetItem(f"{gsr_val:.2f}"))
        self.data_table.setItem(row, 3, QTableWidgetItem(f"{accel_val:.2f}"))
        self.data_table.setItem(row, 4, QTableWidgetItem(f"{fear_percent:.1f}"))
        self.data_table.scrollToBottom()

        # Update chart
        current_ms = QDateTime.currentMSecsSinceEpoch()
        self.fear_series.append(current_ms, fear_percent)
        self.time_history.append(current_ms)
        self.fear_history.append(fear_percent)
        
        # Trim history to last 10 points for readability
        if len(self.fear_series) > 10:
            self.fear_series.remove(0)
            self.time_history.pop(0)
            self.fear_history.pop(0)
        
        self.time_axis.setRange(QDateTime.fromMSecsSinceEpoch(self.time_history[0]), 
                              QDateTime.fromMSecsSinceEpoch(self.time_history[-1]))

        # Update avg fear
        avg_fear = np.mean(self.fear_history) if self.fear_history else 0
        self.avg_label.setText(f"Avg Fear: {avg_fear:.1f}%")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FearDashboard()
    window.show()
    sys.exit(app.exec_())