# gui/user_window.py
import sqlite3
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout, QLineEdit, 
                             QHBoxLayout, QGroupBox, QDesktopWidget, QMessageBox, 
                             QTableWidget, QTableWidgetItem, QListWidget)
from PyQt5.QtCore import Qt

from core.parking_system import ParkingSystem
# from .login_window import LoginWindow # <--- 删除此处的导入

class UserWindow(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.parking = ParkingSystem()
        self.login_window_instance = None # 用于持有新登录窗口的引用
        self.init_ui()
        self.load_user_vehicles()
        
    def init_ui(self):
        self.setMinimumSize(800, 600)
        self.center()
        self.setWindowTitle(f'用户界面 - {self.username}')
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        title_label = QLabel(f'欢迎, {self.username}!')
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        vehicles_group = QGroupBox('我绑定的车辆 (点击车牌查询历史记录)')
        vehicles_layout = QVBoxLayout()
        self.vehicle_list = QListWidget()
        self.vehicle_list.itemClicked.connect(self.search_vehicle_history)
        vehicles_layout.addWidget(self.vehicle_list)
        vehicles_group.setLayout(vehicles_layout)
        main_layout.addWidget(vehicles_group)

        history_group = QGroupBox('停车历史记录')
        history_layout = QVBoxLayout()
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(['入场时间', '出场时间', '费用(元)', '车位号'])
        self.history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        history_layout.addWidget(self.history_table)
        history_group.setLayout(history_layout)
        main_layout.addWidget(history_group)

        logout_btn = QPushButton('登出')
        logout_btn.setFixedSize(120, 40)
        logout_btn.clicked.connect(self.logout)
        logout_btn.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold;")
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(logout_btn)
        main_layout.addLayout(btn_layout)
        
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def load_user_vehicles(self):
        self.vehicle_list.clear()
        conn = sqlite3.connect('parking.db')
        cursor = conn.cursor()
        cursor.execute("SELECT plate_number FROM user_vehicles WHERE username = ? ORDER BY plate_number", (self.username,))
        vehicles = cursor.fetchall()
        conn.close()
        
        if vehicles:
            for v in vehicles:
                self.vehicle_list.addItem(v[0])
        else:
            self.vehicle_list.addItem("您还没有绑定任何车辆")

    def search_vehicle_history(self, item):
        plate_number = item.text()
        if plate_number == "您还没有绑定任何车辆":
            self.history_table.setRowCount(0)
            return

        records = self.parking.get_vehicle_history(plate_number)
        
        self.history_table.setRowCount(len(records))
        if records:
            for i, record in enumerate(records):
                entry_time, exit_time, fee, spot = record
                self.history_table.setItem(i, 0, QTableWidgetItem(str(entry_time)))
                self.history_table.setItem(i, 1, QTableWidgetItem(str(exit_time) if exit_time else "在场"))
                self.history_table.setItem(i, 2, QTableWidgetItem(f"{fee:.2f}" if fee is not None else "-"))
                self.history_table.setItem(i, 3, QTableWidgetItem(str(spot)))
        else:
            self.history_table.setRowCount(0)

    def logout(self):
        # <--- 修改在这里
        # 在需要时才导入 LoginWindow，打破循环
        from .login_window import LoginWindow
        
        self.close()
        self.login_window_instance = LoginWindow()
        self.login_window_instance.show()