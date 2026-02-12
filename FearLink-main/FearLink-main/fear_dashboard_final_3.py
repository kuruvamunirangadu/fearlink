import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import sys
import numpy as np
import tensorflow as tf
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, QHBoxLayout, QWidget, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QPushButton)
from PyQt5.QtCore import QTimer, Qt, QDateTime, QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup
from PyQt5.QtGui import QFont, QColor, QPen, QPainter, QBrush, QLinearGradient, QRadialGradient
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis, QDateTimeAxis
import math
import logging

# Setup logging
logging.basicConfig(filename='sos_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

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
        ppg = np.full((1, 50, 1), np.random.uniform(60, 90))
        gsr = np.full((1, 50, 1), np.random.uniform(0.5, 3.0))
        accel = np.random.uniform(0.0, 0.8, (1, 150, 3))
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
    logging.debug(f"Generated mode: {mode}, ppg: {np.mean(ppg):.1f}, gsr: {np.mean(gsr):.2f}, accel: {np.mean(np.linalg.norm(accel)):.2f}")
    return ppg, gsr, accel, ppg_norm, gsr_norm, accel_norm, mode

# Predict with TFLite
def predict_fear(ppg, gsr, accel):
    input_map = {detail['name']: detail['index'] for detail in input_details}
    interpreter.set_tensor(input_map['serving_default_accel:0'], accel)
    interpreter.set_tensor(input_map['serving_default_gsr:0'], gsr)
    interpreter.set_tensor(input_map['serving_default_ppg:0'], ppg)
    interpreter.invoke()
    fear_score = 1 - interpreter.get_tensor(output_details[0]['index'])[0][0]
    fear_percent = fear_score * 100
    logging.debug(f"Predicted fear: {fear_percent:.1f}%")
    return fear_percent

# Confirmation Popup
class ConfirmationPopup(QDialog):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SOS Confirmation")
        self.setGeometry(500, 300, 300, 100)
        self.setStyleSheet("""
            background-color: #1A2B3C; 
            border: 2px solid #81C784; 
            border-radius: 15px;
        """)

        layout = QVBoxLayout()
        label = QLabel(message, self)
        label.setFont(QFont("Orbitron", 12, QFont.Bold))
        label.setStyleSheet("color: #E0F7FA; padding: 10px;")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        self.setLayout(layout)

        QTimer.singleShot(3000, self.close)  # Auto-close after 3 seconds

# SOS Popup Dialog
class SOSPopup(QDialog):
    def __init__(self, ppg, gsr, accel, fear_percent, timestamp, guardians, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SOS Alert")
        self.setGeometry(500, 300, 400, 200)
        self.setStyleSheet("""
            background-color: #1A2B3C; 
            border: 2px solid #EF5350; 
            border-radius: 15px;
        """)
        self.parent = parent
        self.guardians = guardians

        layout = QVBoxLayout()
        
        # Alert Message
        alert_label = QLabel("Distress Detected! Alerting Guardians & Authorities", self)
        alert_label.setFont(QFont("Orbitron", 14, QFont.Bold))
        alert_label.setStyleSheet("color: #EF5350; padding: 10px;")
        alert_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(alert_label)

        # Info Shared
        info_label = QLabel(
            f"Time: {timestamp}\n"
            f"PPG: {ppg:.1f} bpm | GSR: {gsr:.2f} µS | Accel: {accel:.2f} m/s²\n"
            f"Fear: {fear_percent:.1f}%\n"
            f"Location: [Demo] 28.7041° N, 77.1025° E\n"
            f"Contacting Authorities...\n"
            f"Notifying Guardians: [{', '.join(self.guardians)}]",
            self
        )
        info_label.setFont(QFont("Orbitron", 12))
        info_label.setStyleSheet("color: #E0F7FA; padding: 10px;")
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)

        # Cancel Button
        cancel_button = QPushButton("Cancel SOS", self)
        cancel_button.setFont(QFont("Orbitron", 12))
        cancel_button.setStyleSheet("""
            background-color: #EF5350; 
            color: #E0F7FA; 
            padding: 10px; 
            border-radius: 10px;
        """)
        cancel_button.clicked.connect(self.cancel_sos)
        layout.addWidget(cancel_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

        # Auto-close after 5 seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.close_and_confirm)
        self.timer.start(5000)

    def cancel_sos(self):
        logging.info("SOS Cancelled by User")
        self.close()
        confirmation = ConfirmationPopup("SOS Cancelled", self.parent)
        confirmation.exec_()

    def close_and_confirm(self):
        self.close()
        confirmation = ConfirmationPopup("SOS Sent Successfully", self.parent)
        confirmation.exec_()

# Custom glass widget with water effect
class GlassWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sos_active = False
        # Ensure continuous repaint for pulsing effect
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(100)  # Update every 100ms for smooth pulsing

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        try:
            time = QDateTime.currentMSecsSinceEpoch() / 1000.0
            gradient = QLinearGradient(0, 0, 0, self.height())
            wave_offset = 30 * math.sin(2 * time)
            alpha = int(30 + 20 * math.sin(time)) % 256
            gradient.setColorAt(0, QColor(0, 100, 200, alpha))
            gradient.setColorAt(0.5 + wave_offset / self.height(), QColor(255, 255, 255, 50))
            gradient.setColorAt(1, QColor(0, 150, 255, 80))
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(self.rect().adjusted(5, 5, -5, -5), 20, 20)
            
            # Pulsing red border if SOS is active
            if self.sos_active:
                border_color = QColor(239, 83, 80, int(150 + 100 * math.sin(4 * time)))
                painter.setPen(QPen(border_color, 4))
            else:
                painter.setPen(QColor(0, 200, 255, 200))
            painter.drawRoundedRect(self.rect().adjusted(5, 5, -5, -5), 20, 20)
        finally:
            painter.end()

# Dashboard
class FearDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FearLink: The AI Smartwatch")
        self.setGeometry(100, 100, 1400, 900)
        self.setStyleSheet("background-color: #0A1B2A;")

        # Custom guardian list (can be set via app settings in real implementation)
        self.guardians = ["Mom", "Dad", "Friend"]  # Placeholder for user-defined guardians

        main_widget = GlassWidget(self)
        self.main_widget = main_widget
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)

        # Header
        header = QLabel("FearLink: The AI Smartwatch", self)
        header.setFont(QFont("Orbitron", 36, QFont.Bold))
        header.setStyleSheet("color: #00E5FF; padding: 20px; background: none; text-transform: uppercase;")
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)

        subtitle = QLabel("Predicts, Prevents, Protects. Powered by SelfMate – The Future of AI Companionship", self)
        subtitle.setFont(QFont("Orbitron", 18))
        subtitle.setStyleSheet("color: #40C4FF; padding: 10px; background: none;")
        subtitle.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(subtitle)

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
            border: 3px solid #00E5FF;
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
        pen.setStyle(Qt.DashDotLine)
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
        self.chart_view.setStyleSheet("background: rgba(10, 30, 60, 150); border-radius: 20px; border: 2px solid #00E5FF;")
        right_panel.addWidget(self.chart_view)

        # Status orb with water effect
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
        self.stressed_count = 0
        self.last_popup_time = QDateTime.currentMSecsSinceEpoch()
        self.update_dashboard()

    def update_dashboard(self):
        ppg, gsr, accel, ppg_norm, gsr_norm, accel_norm, mode = generate_sensor_data()
        
        ppg_val = np.mean(ppg[0, :, 0])
        gsr_val = np.mean(gsr[0, :, 0])
        accel_val = np.mean(np.linalg.norm(accel[0], axis=1))
        
        # Vitals check with water-like color pulse
        ppg_color = "#81C784" if ppg_val < 100 else "#FFCA28" if ppg_val < 150 else "#EF5350"
        gsr_color = "#81C784" if gsr_val < 5 else "#FFCA28" if gsr_val < 10 else "#EF5350"
        accel_color = "#81C784" if accel_val < 1 else "#FFCA28" if accel_val < 2 else "#EF5350"
        
        self.vitals['ppg'].setText(f"PPG: {ppg_val:.1f} bpm")
        self.vitals['ppg'].setStyleSheet(f"""
            color: {ppg_color}; 
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(0, 50, 100, 100), 
                stop:1 rgba({int(ppg_color[1:3], 16)}, {int(ppg_color[3:5], 16)}, {int(ppg_color[5:7], 16)}, 150)); 
            padding: 25px; 
            border-radius: 15px; 
            font: 22pt 'Orbitron'; 
            border: 3px solid #00E5FF;
            margin: 10px 0;
        """)
        self.vitals['gsr'].setText(f"GSR: {gsr_val:.2f} µS")
        self.vitals['gsr'].setStyleSheet(f"""
            color: {gsr_color}; 
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(0, 50, 100, 100), 
                stop:1 rgba({int(gsr_color[1:3], 16)}, {int(gsr_color[3:5], 16)}, {int(gsr_color[5:7], 16)}, 150)); 
            padding: 25px; 
            border-radius: 15px; 
            font: 22pt 'Orbitron'; 
            border: 3px solid #00E5FF;
            margin: 10px 0;
        """)
        self.vitals['accel'].setText(f"Accel: {accel_val:.2f} m/s²")
        self.vitals['accel'].setStyleSheet(f"""
            color: {accel_color}; 
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(0, 50, 100, 100), 
                stop:1 rgba({int(accel_color[1:3], 16)}, {int(accel_color[3:5], 16)}, {int(accel_color[5:7], 16)}, 150)); 
            padding: 25px; 
            border-radius: 15px; 
            font: 22pt 'Orbitron'; 
            border: 3px solid #00E5FF;
            margin: 10px 0;
        """)

        fear_percent = predict_fear(ppg_norm, gsr_norm, accel_norm)

        # Status with water-like animation
        if fear_percent > 70:
            status = "Stressed"
            orb_color = "#EF5350"
            self.stressed_count += 1
        elif fear_percent > 30:
            status = "Fear"
            orb_color = "#FFCA28"
            self.stressed_count = 0
        else:
            status = "Calm"
            orb_color = "#81C784"
            self.stressed_count = 0
        
        self.status_label.setText(f"Status: {status}")
        anim_group = QSequentialAnimationGroup(self)
        anim1 = QPropertyAnimation(self.status_label, b"styleSheet")
        anim1.setDuration(350)
        anim1.setStartValue(f"""
            color: #E0F7FA; 
            background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, 
                stop:0 rgba(50, 200, 100, 50), stop:1 rgba(0, 150, 255, 20)); 
            padding: 25px; 
            border-radius: 50px; 
            border: 3px solid {orb_color};
            min-width: 200px; min-height: 200px;
        """)
        anim1.setEndValue(f"""
            color: #E0F7FA; 
            background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, 
                stop:0 rgba(50, 200, 100, 150), stop:1 rgba(0, 150, 255, 50)); 
            padding: 25px; 
            border-radius: 50px; 
            border: 3px solid {orb_color};
            min-width: 200px; min-height: 200px;
        """)
        anim1.setEasingCurve(QEasingCurve.OutQuad)

        anim2 = QPropertyAnimation(self.status_label, b"styleSheet")
        anim2.setDuration(350)
        anim2.setStartValue(anim1.endValue())
        anim2.setEndValue(f"""
            color: #E0F7FA; 
            background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, 
                stop:0 rgba(50, 200, 100, 100), stop:1 rgba(0, 150, 255, 30)); 
            padding: 25px; 
            border-radius: 50px; 
            border: 3px solid {orb_color};
            min-width: 200px; min-height: 200px;
        """)
        anim2.setEasingCurve(QEasingCurve.InQuad)

        anim_group.addAnimation(anim1)
        anim_group.addAnimation(anim2)
        anim_group.start()

        # SOS System: Trigger on sustained stress
        current_time_ms = QDateTime.currentMSecsSinceEpoch()
        if self.stressed_count >= 2:
            if (current_time_ms - self.last_popup_time) >= 5000:
                timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
                logging.info(
                    f"SOS Triggered - Time: {timestamp}, PPG: {ppg_val:.1f} bpm, "
                    f"GSR: {gsr_val:.2f} µS, Accel: {accel_val:.2f} m/s², Fear: {fear_percent:.1f}%"
                )
                self.main_widget.sos_active = True
                sos_popup = SOSPopup(ppg_val, gsr_val, accel_val, fear_percent, timestamp, self.guardians, self)
                sos_popup.exec_()
                self.last_popup_time = current_time_ms
                self.stressed_count = 0
                self.main_widget.sos_active = False
        else:
            self.main_widget.sos_active = False

        # Table with corrected time
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