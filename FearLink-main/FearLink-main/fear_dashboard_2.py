import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import sys
import numpy as np
import tensorflow as tf
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, 
                             QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import QTimer, Qt, QDateTime, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QColor, QPen, QPainter, QBrush, QLinearGradient, QRadialGradient
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis, QDateTimeAxis

# Load TFLite model
interpreter = tf.lite.Interpreter(model_path="model.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Normalize function
def normalize(data, min_val, max_val):
    return (data - min_val) / (max_val - min_val + 1e-8)

# Generate sensor data with vital thresholds
def generate_sensor_data():
    mode = np.random.choice(["calm", "fear", "stressed", "random"], p=[0.4, 0.3, 0.2, 0.1])
    if mode == "calm":
        ppg = np.full((1, 50, 1), np.random.uniform(60, 90))  # Adjusted to 90
        gsr = np.full((1, 50, 1), np.random.uniform(0.5, 3.0))  # Adjusted to 3.0
        accel = np.random.uniform(0.0, 0.8, (1, 150, 3))  # Adjusted to 0.8
    elif mode == "fear":
        ppg = np.linspace(100, 130, 50).reshape(1, 50, 1)
        gsr = np.linspace(3.0, 7.0, 50).reshape(1, 50, 1)
        accel = np.random.uniform(1.0, 1.8, (1, 150, 3))
    elif mode == "stressed":
        ppg = np.linspace(140, 180, 50).reshape(1, 50, 1)
        gsr = np.linspace(10.0, 15.0, 50).reshape(1, 50, 1)
        accel = np.random.uniform(2.0, 3.0, (1, 150, 3))
    else:
        ppg = np.random.uniform(60, 180, (1, 50, 1))
        gsr = np.random.uniform(0.5, 15.0, (1, 50, 1))
        accel = np.random.uniform(0.0, 3.0, (1, 150, 3))
    
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
    fear_score = 1 - interpreter.get_tensor(output_details[0]['index'])[0][0]
    return fear_score * 100

# Custom glass widget
class GlassWidget(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(255, 255, 255, 30))
        gradient.setColorAt(1, QColor(0, 100, 200, 80))
        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect().adjusted(5, 5, -5, -5), 20, 20)
        painter.setPen(QColor(0, 150, 255, 100))
        painter.drawRoundedRect(self.rect().adjusted(5, 5, -5, -5), 20, 20)

# Dashboard
class FearDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FearSense: Neural Nexus")
        self.setGeometry(100, 100, 1400, 900)
        self.setStyleSheet("background-color: #0A1B2A;")

        main_widget = GlassWidget(self)
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # Header
        header = QLabel("FearSense: Neural Nexus", self)
        header.setFont(QFont("Orbitron", 36, QFont.Bold))
        header.setStyleSheet("color: #00E5FF; padding: 20px; background: none; text-transform: uppercase;")
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)

        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)

        # Left panel (Vitals)
        left_panel = QVBoxLayout()
        content_layout.addLayout(left_panel, stretch=1)

        # Vitals with thresholds
        self.vitals = {}
        vital_style = """
            color: #E0F7FA; 
            background: rgba(0, 50, 100, 100); 
            padding: 25px; 
            border-radius: 15px; 
            font: 22pt 'Orbitron'; 
            border: 2px solid rgba(0, 200, 255, 150);
            margin: 10px 0;
        """
        self.vitals['ppg'] = QLabel("PPG: -- bpm", self)
        self.vitals['ppg'].setStyleSheet(vital_style)
        left_panel.addWidget(self.vitals['ppg'])

        self.vitals['gsr'] = QLabel("GSR: -- µS", self)
        self.vitals['gsr'].setStyleSheet(vital_style)
        left_panel.addWidget(self.vitals['gsr'])

        self.vitals['accel'] = QLabel("Accel: -- m/s²", self)
        self.vitals['accel'].setStyleSheet(vital_style)
        left_panel.addWidget(self.vitals['accel'])

        # Data table
        self.data_table = QTableWidget(self)
        self.data_table.setColumnCount(5)
        self.data_table.setHorizontalHeaderLabels(["Time", "PPG (bpm)", "GSR (µS)", "Accel (m/s²)", "Fear %"])
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.data_table.setStyleSheet("""
            QTableWidget { 
                background: rgba(20, 50, 100, 120); 
                font: 16pt 'Orbitron'; 
                color: #B2EBF2; 
                border: none; 
                border-radius: 15px;
            }
            QHeaderView::section { 
                background: rgba(0, 150, 255, 150); 
                color: #E0F7FA; 
                padding: 10px; 
                font: bold 16pt 'Orbitron'; 
                border: none;
            }
        """)
        left_panel.addWidget(self.data_table)

        # Right panel (Chart and Status)
        right_panel = QVBoxLayout()
        content_layout.addLayout(right_panel, stretch=2)

        # Fear chart
        self.fear_series = QLineSeries()
        pen = QPen(QColor("#00E5FF"))
        pen.setWidth(4)
        pen.setStyle(Qt.DashDotLine)  # Enhanced cyberpunk line
        self.fear_series.setPen(pen)
        self.chart = QChart()
        self.chart.addSeries(self.fear_series)
        self.chart.setTitle("Neural Fear Pulse")
        self.chart.setTitleFont(QFont("Orbitron", 24, QFont.Bold))
        self.chart.setTitleBrush(QColor("#40C4FF"))
        self.chart.setBackgroundBrush(QBrush(QColor(20, 40, 80, 100)))

        self.time_axis = QDateTimeAxis()
        self.time_axis.setFormat("hh:mm:ss")
        self.time_axis.setTitleText("Temporal Stream")
        self.time_axis.setLabelsColor(QColor(178, 235, 242))
        self.time_axis.setTitleBrush(QColor("#40C4FF"))
        self.chart.addAxis(self.time_axis, Qt.AlignBottom)
        self.fear_series.attachAxis(self.time_axis)

        self.fear_axis = QValueAxis()
        self.fear_axis.setRange(0, 100)
        self.fear_axis.setTitleText("Fear Intensity (%)")
        self.fear_axis.setLabelFormat("%.0f")
        self.fear_axis.setLabelsColor(QColor(178, 235, 242))
        self.fear_axis.setTitleBrush(QColor("#40C4FF"))
        self.chart.addAxis(self.fear_axis, Qt.AlignLeft)
        self.fear_series.attachAxis(self.fear_axis)

        self.chart_view = QChartView(self.chart)
        self.chart_view.setMinimumSize(700, 500)
        self.chart_view.setStyleSheet("background: rgba(10, 30, 60, 150); border-radius: 20px;")
        right_panel.addWidget(self.chart_view)

        # Status orb
        self.status_label = QLabel("Status: --", self)
        self.status_label.setFont(QFont("Orbitron", 28, QFont.Bold))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            color: #E0F7FA; 
            background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, 
                stop:0 rgba(50, 200, 100, 150), stop:1 rgba(0, 150, 255, 50)); 
            padding: 25px; 
            border-radius: 50px; 
            border: 3px solid #00E5FF;
            min-width: 200px; min-height: 200px;
        """)
        right_panel.addWidget(self.status_label, alignment=Qt.AlignHCenter)

        # Avg Fear
        self.avg_label = QLabel("Avg Fear: --%", self)
        self.avg_label.setFont(QFont("Orbitron", 20, QFont.Bold))
        self.avg_label.setStyleSheet("""
            color: #E0F7FA; 
            background: rgba(100, 150, 255, 120); 
            padding: 20px; 
            border-radius: 15px; 
            border: 2px solid #40C4FF;
        """)
        self.avg_label.setAlignment(Qt.AlignCenter)
        right_panel.addWidget(self.avg_label)

        main_layout.addStretch()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_dashboard)
        self.timer.start(5000)

        self.fear_history = []
        self.time_history = []
        self.update_dashboard()

    def update_dashboard(self):
        ppg, gsr, accel, ppg_norm, gsr_norm, accel_norm, mode = generate_sensor_data()
        
        ppg_val = np.mean(ppg[0, :, 0])
        gsr_val = np.mean(gsr[0, :, 0])
        accel_val = np.mean(np.linalg.norm(accel[0], axis=1))
        
        # Vitals check
        ppg_color = "#81C784" if ppg_val < 100 else "#FFCA28" if ppg_val < 150 else "#EF5350"
        gsr_color = "#81C784" if gsr_val < 5 else "#FFCA28" if gsr_val < 10 else "#EF5350"
        accel_color = "#81C784" if accel_val < 1 else "#FFCA28" if accel_val < 2 else "#EF5350"
        
        self.vitals['ppg'].setText(f"PPG: {ppg_val:.1f} bpm")
        self.vitals['ppg'].setStyleSheet(f"""
            color: {ppg_color}; 
            background: rgba(0, 50, 100, 100); 
            padding: 25px; 
            border-radius: 15px; 
            font: 22pt 'Orbitron'; 
            border: 2px solid rgba(0, 200, 255, 150);
            margin: 10px 0;
        """)
        self.vitals['gsr'].setText(f"GSR: {gsr_val:.2f} µS")
        self.vitals['gsr'].setStyleSheet(f"""
            color: {gsr_color}; 
            background: rgba(0, 50, 100, 100); 
            padding: 25px; 
            border-radius: 15px; 
            font: 22pt 'Orbitron'; 
            border: 2px solid rgba(0, 200, 255, 150);
            margin: 10px 0;
        """)
        self.vitals['accel'].setText(f"Accel: {accel_val:.2f} m/s²")
        self.vitals['accel'].setStyleSheet(f"""
            color: {accel_color}; 
            background: rgba(0, 50, 100, 100); 
            padding: 25px; 
            border-radius: 15px; 
            font: 22pt 'Orbitron'; 
            border: 2px solid rgba(0, 200, 255, 150);
            margin: 10px 0;
        """)

        fear_percent = predict_fear(ppg_norm, gsr_norm, accel_norm)

        # Status with animated orb
        if fear_percent > 70:
            status = "Stressed"
            orb_color = "#EF5350"
        elif fear_percent > 30:
            status = "Fear"
            orb_color = "#FFCA28"
        else:
            status = "Calm"
            orb_color = "#81C784"
        
        self.status_label.setText(f"Status: {status}")
        anim = QPropertyAnimation(self.status_label, b"styleSheet")
        anim.setDuration(700)
        anim.setStartValue(f"""
            color: #E0F7FA; 
            background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, 
                stop:0 rgba(50, 200, 100, 50), stop:1 rgba(0, 150, 255, 20)); 
            padding: 25px; 
            border-radius: 50px; 
            border: 3px solid {orb_color};
            min-width: 200px; min-height: 200px;
        """)
        anim.setEndValue(f"""
            color: #E0F7FA; 
            background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, 
                stop:0 rgba(50, 200, 100, 150), stop:1 rgba(0, 150, 255, 50)); 
            padding: 25px; 
            border-radius: 50px; 
            border: 3px solid {orb_color};
            min-width: 200px; min-height: 200px;
        """)
        anim.setEasingCurve(QEasingCurve.InOutQuad)
        anim.start()

        # Table
        current_time = QDateTime.currentDateTime().toString("hh:mm:ss")
        row = self.data_table.rowCount()
        self.data_table.insertRow(row)
        self.data_table.setItem(row, 0, QTableWidgetItem(current_time))
        self.data_table.setItem(row, 1, QTableWidgetItem(f"{ppg_val:.1f}"))
        self.data_table.setItem(row, 2, QTableWidgetItem(f"{gsr_val:.2f}"))
        self.data_table.setItem(row, 3, QTableWidgetItem(f"{accel_val:.2f}"))
        self.data_table.setItem(row, 4, QTableWidgetItem(f"{fear_percent:.1f}"))
        self.data_table.scrollToBottom()

        # Chart
        current_ms = QDateTime.currentMSecsSinceEpoch()
        self.fear_series.append(current_ms, fear_percent)
        self.time_history.append(current_ms)
        self.fear_history.append(fear_percent)
        
        if len(self.fear_series) > 10:
            self.fear_series.remove(0)
            self.time_history.pop(0)
            self.fear_history.pop(0)
        
        self.time_axis.setRange(QDateTime.fromMSecsSinceEpoch(self.time_history[0]), 
                              QDateTime.fromMSecsSinceEpoch(self.time_history[-1]))

        avg_fear = np.mean(self.fear_history) if self.fear_history else 0
        self.avg_label.setText(f"Avg Fear: {avg_fear:.1f}%")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = FearDashboard()
    window.show()
    sys.exit(app.exec_())