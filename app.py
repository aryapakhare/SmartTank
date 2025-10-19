import sys, random, datetime, csv
from math import pi
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QSpinBox, QDoubleSpinBox,
    QComboBox, QAbstractItemView, QDialog, QDialogButtonBox,
    QFileDialog
)
from PySide6.QtCore import Qt, QTimer, QDateTime
from PySide6.QtGui import QColor


def apply_theme(app):
    try:
        with open("dracula.qss", "r") as file:
            app.setStyleSheet(file.read())
    except Exception:
        pass


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login - Smart Tank Monitor")
        self.setModal(True)
        self.username = None
        
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("<b>Enter your username to continue:</b>"))
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.returnPressed.connect(self.accept)
        layout.addWidget(self.username_input)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        self.setMinimumWidth(300)
    
    def accept(self):
        username = self.username_input.text().strip()
        if not username:
            QMessageBox.warning(self, "Error", "Username cannot be empty!")
            return
        self.username = username
        super().accept()


class TankApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart Tank Monitor v2")
        self.setMinimumSize(1200, 550)

        self._selected_tank_id = None
        self.data = []
        self.simulating = False
        self.alarmed_tanks = set()
        self.current_user = None

        self.show_login()
        
        if self.current_user:
            self.init_ui()
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_levels)
        else:
            sys.exit()

    def show_login(self):
        dialog = LoginDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.current_user = dialog.username
            self.setWindowTitle(f"Smart Tank Monitor v2 - User: {self.current_user}")
        else:
            self.current_user = None

    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # User info bar
        user_bar = QHBoxLayout()
        user_label = QLabel(f"<b>Logged in as:</b> {self.current_user}")
        logout_btn = QPushButton("Logout")
        logout_btn.clicked.connect(self.logout)
        logout_btn.setMaximumWidth(100)
        user_bar.addWidget(user_label)
        user_bar.addStretch()
        user_bar.addWidget(logout_btn)
        main_layout.addLayout(user_bar)
        
        form_layout = QHBoxLayout()

        # Left panel - form
        left = QVBoxLayout()
        left.addWidget(QLabel("<b>Tank Parameters</b>"))

        self.tank_input = QLineEdit()

        self.fluid_input = QComboBox()
        self.fluid_input.addItems(["Water", "Oil", "Diesel"])

        self.radius_input = QDoubleSpinBox()
        self.radius_input.setRange(1.0, 1000.0)
        self.radius_input.setSuffix(" cm")
        self.radius_input.setValue(50.0)
        self.radius_input.setDecimals(1)

        self.target_input = QSpinBox()
        self.target_input.setRange(0, 200)
        self.flow_input = QSpinBox()
        self.flow_input.setRange(0, 50)
        self.flow_input.setValue(10)

        left.addWidget(QLabel("Tank ID"))
        left.addWidget(self.tank_input)

        left.addWidget(QLabel("Fluid Type"))
        left.addWidget(self.fluid_input)

        left.addWidget(QLabel("Tank Radius (cm)"))
        left.addWidget(self.radius_input)

        left.addWidget(QLabel("Target Level (cm)"))
        left.addWidget(self.target_input)

        left.addWidget(QLabel("Flow Rate (L/min)"))
        left.addWidget(self.flow_input)

        # Buttons
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add Tank")
        self.update_btn = QPushButton("Update Tank")
        self.delete_btn = QPushButton("Delete Tank")
        self.clear_btn = QPushButton("Clear Fields")
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.update_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.clear_btn)
        left.addLayout(btn_layout)

        # Simulation buttons
        sim_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start Simulation")
        self.stop_btn = QPushButton("Stop Simulation")
        sim_layout.addWidget(self.start_btn)
        sim_layout.addWidget(self.stop_btn)
        left.addLayout(sim_layout)
        
        # Export button
        export_layout = QHBoxLayout()
        self.export_btn = QPushButton("📥 Download CSV Logs")
        self.export_btn.clicked.connect(self.download_csv)
        export_layout.addWidget(self.export_btn)
        left.addLayout(export_layout)

        # Right panel - table
        right = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Tank ID", "Fluid", "Radius (cm)", "Level (cm)", "Volume (L)", 
             "Valve", "Target (cm)", "Flow (L/min)", "Last Modified By"]
        )
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        right.addWidget(self.table)

        form_layout.addLayout(left, 2)
        form_layout.addLayout(right, 7)
        main_layout.addLayout(form_layout)
        self.setLayout(main_layout)

        # Connect buttons
        self.add_btn.clicked.connect(self.add_tank)
        self.update_btn.clicked.connect(self.update_tank)
        self.delete_btn.clicked.connect(self.delete_tank)
        self.clear_btn.clicked.connect(self.clear_fields)
        self.start_btn.clicked.connect(self.start_simulation)
        self.stop_btn.clicked.connect(self.stop_simulation)
        self.table.cellClicked.connect(self.on_row_selected)

    def logout(self):
        reply = QMessageBox.question(
            self, "Logout", 
            "Are you sure you want to logout?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.stop_simulation()
            self.close()

    # ---------- Tank Data Operations ----------
    def add_tank(self):
        tank_id = self.tank_input.text().strip()
        fluid = self.fluid_input.currentText()
        radius = self.radius_input.value()
        target = self.target_input.value()
        flow = self.flow_input.value()

        if not tank_id:
            self.show_error("Tank ID is required.")
            return
        if radius <= 0:
            self.show_error("Tank radius must be greater than zero.")
            return

        level = 0.00
        valve = "OPEN" if level < target else "CLOSED"
        volume = self.calculate_volume(radius, level)

        record = [len(self.data) + 1, tank_id, fluid, radius, level, volume, valve, target, flow, self.current_user]
        self.data.append(record)
        self.refresh_table()
        self.clear_fields()
        self.show_message("Tank added successfully.")

    def update_tank(self):
        if self._selected_tank_id is None:
            self.show_error("Select a tank to update.")
            return

        tank_id = self.tank_input.text().strip()
        fluid = self.fluid_input.currentText()
        radius = self.radius_input.value()
        target = self.target_input.value()
        flow = self.flow_input.value()

        if not tank_id:
            self.show_error("Tank ID is required.")
            return
        if radius <= 0:
            self.show_error("Tank radius must be greater than zero.")
            return

        for row in self.data:
            if row[0] == self._selected_tank_id:
                row[1] = tank_id
                row[2] = fluid
                row[3] = radius
                row[7] = target
                row[8] = flow
                row[9] = self.current_user  # Update user
                # Recalculate volume with current level
                row[5] = self.calculate_volume(radius, row[4])
                self.refresh_table()
                self.show_message("Tank updated.")
                return

    def delete_tank(self):
        if self._selected_tank_id is None:
            self.show_error("Select a tank to delete.")
            return
        self.data = [r for r in self.data if r[0] != self._selected_tank_id]
        self.refresh_table()
        self.show_message("Tank deleted.")
        self.clear_fields()

    def clear_fields(self):
        self.tank_input.clear()
        self.fluid_input.setCurrentIndex(0)
        self.radius_input.setValue(50.0)
        self.target_input.setValue(0)
        self.flow_input.setValue(10)
        self.table.clearSelection()
        self._selected_tank_id = None

    # ---------- Simulation Logic ----------
    def start_simulation(self):
        if not self.data:
            self.show_error("Add at least one tank to start simulation.")
            return
        self.simulating = True
        self.timer.start(1500)
        self.show_message("Simulation started.")

    def stop_simulation(self):
        self.simulating = False
        self.timer.stop()
        self.show_message("Simulation stopped.")

    def update_levels(self):
        now = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        time_interval = 1.5  # seconds (timer interval)

        for row in self.data:
            level = float(row[4])
            radius = float(row[3])
            target = float(row[7])
            flow = float(row[8])

            # Valve logic
            if level < target:
                # Calculate volume added in this time interval
                volume_added = (flow / 60) * time_interval  # liters
                
                # Convert volume to height increase
                # Volume = π * r² * h, so h = Volume / (π * r²)
                radius_m = radius / 100  # convert cm to m
                height_increase_m = volume_added / (1000 * pi * radius_m ** 2)  # m
                height_increase_cm = height_increase_m * 100  # convert to cm
                
                level += height_increase_cm
                valve = "OPEN"
            else:
                level -= random.uniform(0.1, 0.5)
                valve = "CLOSED"

            # Clamp level between 0 and 200 (assuming max tank height)
            level = max(0, min(200, level))
            row[4] = level
            row[6] = valve

            # Recalculate volume
            row[5] = self.calculate_volume(radius, level)

            # Alarm conditions
            if (level < 10 or level > 190) and row[0] not in self.alarmed_tanks:
                self.alarmed_tanks.add(row[0])
                self.show_message(f"⚠️ Alarm: Tank {row[1]} level is {'too low' if level < 10 else 'too high'} ({level:.1f} cm)")

            # CSV Logging
            self.log_to_csv([now, row[1], row[2], f"{radius:.1f}", f"{level:.2f}", f"{row[5]:.2f}", valve, target, flow, row[9]])

        self.refresh_table()

    def calculate_volume(self, radius_cm, level_cm):
        # Convert cm to meters for volume calculation in cubic meters
        r = radius_cm / 100
        h = level_cm / 100
        volume_m3 = pi * r ** 2 * h  # volume in cubic meters
        volume_liters = volume_m3 * 1000  # convert to liters
        return volume_liters

    def refresh_table(self):
        self.table.setRowCount(len(self.data))
        for r, row in enumerate(self.data):
            for c, value in enumerate(row):
                # Format floats nicely
                if isinstance(value, float):
                    if c == 5:  # Volume column
                        item = QTableWidgetItem(f"{value:.1f}")
                    else:
                        item = QTableWidgetItem(f"{value:.2f}")
                else:
                    item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)

                # Color valve column
                if c == 6:  # Valve
                    if value == "OPEN":
                        item.setForeground(QColor("green"))
                    else:
                        item.setForeground(QColor("red"))

                # Highlight alarmed rows
                if row[0] in self.alarmed_tanks:
                    item.setBackground(QColor("#8A5628"))  # light red

                self.table.setItem(r, c, item)

    def on_row_selected(self, row, _col):
        tank_id_item = self.table.item(row, 0)
        if not tank_id_item:
            return
        tank_id = int(tank_id_item.text())
        self._selected_tank_id = tank_id
        self.tank_input.setText(self.table.item(row, 1).text())
        fluid = self.table.item(row, 2).text()
        radius = float(self.table.item(row, 3).text())
        target = int(float(self.table.item(row, 7).text()))
        flow = int(float(self.table.item(row, 8).text()))

        self.fluid_input.setCurrentText(fluid)
        self.radius_input.setValue(radius)
        self.target_input.setValue(target)
        self.flow_input.setValue(flow)

    def log_to_csv(self, row_data):
        try:
            with open("tank_logs.csv", "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(row_data)
        except Exception as e:
            print("Logging failed:", e)

    def download_csv(self):
        import os
        import shutil
        
        # Check if log file exists
        if not os.path.exists("tank_logs.csv"):
            self.show_error("No logs found! Start simulation to generate logs.")
            return
        
        # Check if file is empty
        if os.path.getsize("tank_logs.csv") == 0:
            self.show_error("Log file is empty! Run simulation first.")
            return
        
        # Open file dialog to choose save location
        timestamp = QDateTime.currentDateTime().toString("yyyyMMdd_HHmmss")
        default_filename = f"tank_logs_{timestamp}.csv"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save CSV Logs",
            default_filename,
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            try:
                # Copy the log file to chosen location
                shutil.copy2("tank_logs.csv", file_path)
                self.show_message(f"CSV logs successfully downloaded to:\n{file_path}")
            except Exception as e:
                self.show_error(f"Failed to download CSV: {str(e)}")

    # ---------- Helpers ----------
    def show_message(self, text):
        QMessageBox.information(self, "Info", text)

    def show_error(self, text):
        QMessageBox.critical(self, "Error", text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_theme(app)  # Optional if you want to apply a theme
    window = TankApp()
    window.show()

    sys.exit(app.exec())
