import sys
import requests
import json
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFileDialog, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QMessageBox, QTabWidget)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

API_URL = "http://127.0.0.1:8000/api/analyze/"

class ChemicalApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chemical Equipment Analyzer (Desktop)")
        self.resize(1100, 700)
        
        # Main Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Header
        self.header = QLabel("Upload CSV to analyze chemical equipment parameters")
        self.header.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        self.layout.addWidget(self.header)

        # Upload Button
        self.btn_upload = QPushButton("Select CSV & Analyze")
        self.btn_upload.setStyleSheet("padding: 10px; font-size: 14px;")
        self.btn_upload.clicked.connect(self.upload_file)
        self.layout.addWidget(self.btn_upload)

        # Tabs for Visualization and Data
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # Tab 1: Dashboard (Stats + Chart)
        self.dashboard_tab = QWidget()
        self.dashboard_layout = QHBoxLayout(self.dashboard_tab)
        
        # Stats Panel
        self.stats_label = QLabel("No Data Loaded")
        self.stats_label.setStyleSheet("font-size: 14px; padding: 20px; border: 1px solid #ccc;")
        self.dashboard_layout.addWidget(self.stats_label, 1)

        # Chart Panel
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.dashboard_layout.addWidget(self.canvas, 2)
        
        self.tabs.addTab(self.dashboard_tab, "Dashboard")

        # Tab 2: Data Table
        self.table_tab = QWidget()
        self.table_layout = QVBoxLayout(self.table_tab)
        self.data_table = QTableWidget()
        self.table_layout.addWidget(self.data_table)
        self.tabs.addTab(self.table_tab, "Raw Data")

    def upload_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open CSV', '.', "CSV Files (*.csv)")
        if not fname:
            return

        self.header.setText(f"Processing: {fname}...")
        files = {'file': open(fname, 'rb')}
        
        try:
            # Call Django API
            response = requests.post(API_URL, files=files)
            
            if response.status_code == 200:
                data = response.json()
                self.update_ui(data)
                self.header.setText(f"Analysis Complete: {fname}")
            else:
                QMessageBox.critical(self, "Error", f"Server Error: {response.text}")

        except requests.exceptions.ConnectionError:
            QMessageBox.critical(self, "Error", "Could not connect to Django Backend.\nMake sure the server is running.")

    def update_ui(self, data):
        stats = data['stats']
        records = data['data']

        # 1. Update Stats Text
        txt = (f"Total Records: {stats['total_count']}\n\n"
               f"Avg Pressure: {stats['avg_pressure']} bar\n"
               f"Avg Temperature: {stats['avg_temp']} °C\n"
               f"Avg Flowrate: {stats['avg_flow']} m³/h")
        self.stats_label.setText(txt)

        # 2. Update Matplotlib Chart
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        types = list(stats['type_distribution'].keys())
        counts = list(stats['type_distribution'].values())
        
        ax.bar(types, counts, color='#4CAF50')
        ax.set_title("Equipment Type Distribution")
        ax.set_ylabel("Count")
        self.canvas.draw()

        # 3. Update Table
        self.data_table.setRowCount(len(records))
        self.data_table.setColumnCount(5)
        self.data_table.setHorizontalHeaderLabels(["Name", "Type", "Flow", "Pressure", "Temp"])
        
        for i, row in enumerate(records):
            self.data_table.setItem(i, 0, QTableWidgetItem(str(row['Equipment Name'])))
            self.data_table.setItem(i, 1, QTableWidgetItem(str(row['Type'])))
            self.data_table.setItem(i, 2, QTableWidgetItem(str(row['Flowrate'])))
            self.data_table.setItem(i, 3, QTableWidgetItem(str(row['Pressure'])))
            self.data_table.setItem(i, 4, QTableWidgetItem(str(row['Temperature'])))
        
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ChemicalApp()
    window.show()
    sys.exit(app.exec_())