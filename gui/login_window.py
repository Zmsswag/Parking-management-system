# gui/login_window.py
import sqlite3
import sys
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QVBoxLayout, QLineEdit, 
                             QHBoxLayout, QMessageBox, QApplication, QDesktopWidget)
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtCore import Qt

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.login_attempts = 0
        self.main_window = None
        self.init_ui()
        
    def init_ui(self):
        self.setFixedSize(800, 600)
        self.center()
        
        overlay = QWidget(self)
        overlay.setStyleSheet("background-color: rgba(0, 0, 0, 0.4); border-radius: 15px;")
        overlay.setGeometry(50, 50, 700, 500)

        main_layout = QVBoxLayout(overlay)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(50, 50, 50, 50)
        
        title_label = QLabel('停车场管理系统')
        title_label.setStyleSheet("""
            QLabel {
                font-size: 36px;
                font-weight: bold;
                color: #ffffff;
                background-color: transparent;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        
        title_layout = QHBoxLayout()
        title_layout.addStretch()
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        main_layout.addLayout(title_layout)
        main_layout.addStretch(1)

        username_layout = QHBoxLayout()
        username_layout.addStretch()
        username_label = QLabel('用户名:')
        self.username_input = QLineEdit()
        self.username_input.setFixedSize(250, 35)
        self.username_input.setPlaceholderText('请输入用户名')
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        username_layout.addStretch()
        main_layout.addLayout(username_layout)
        
        password_layout = QHBoxLayout()
        password_layout.addStretch()
        password_label = QLabel('密  码:')
        self.password_input = QLineEdit()
        self.password_input.setFixedSize(250, 35)
        self.password_input.setPlaceholderText('请输入密码')
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        password_layout.addStretch()
        main_layout.addLayout(password_layout)
        main_layout.addStretch(1)

        login_btn = QPushButton('登 录')
        login_btn.setFixedSize(150, 45)
        login_btn.clicked.connect(self.login)
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 8px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #2980b9; }
            QPushButton:pressed { background-color: #2475a8; }
        """)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(login_btn)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)
        main_layout.addStretch(2)
        
        self.setWindowTitle('停车场管理系统 - 登录')

        self.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                font-size: 16px;
                background-color: rgba(255, 255, 255, 0.9);
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
            }
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #ffffff;
                background-color: transparent;
            }
        """)

    def paintEvent(self, event):
        painter = QPainter(self)
        
        pixmap = QPixmap('assets\\beijing.jpg')
        
        if pixmap.isNull():
            print("警告: 背景图片 'beijing.jpg' 加载失败。请确保该文件与 main.py 在同一目录下。")
            painter.fillRect(self.rect(), Qt.gray)
        else:
            scaled_pixmap = pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            
            # 计算偏移量
            x = (scaled_pixmap.width() - self.width()) / -2
            y = (scaled_pixmap.height() - self.height()) / -2
            
            # --- 修正部分 ---
            # 将浮点数坐标转换为整数
            painter.drawPixmap(int(x), int(y), scaled_pixmap)
            # --- 修正结束 ---
            
        super().paintEvent(event)
        
    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
    def login(self):
        from .admin_window import AdminWindow
        from .user_window import UserWindow
        username = self.username_input.text()
        password = self.password_input.text()
        if not username or not password:
            QMessageBox.warning(self, '提示', '用户名和密码不能为空！')
            return
        conn = sqlite3.connect('parking.db')
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE username = ? AND password = ?", (username, password))
        result = cursor.fetchone()
        conn.close()
        if result:
            self.hide()
            role = result[0]
            if role == 'admin':
                self.main_window = AdminWindow(username)
            else:
                self.main_window = UserWindow(username)
            self.main_window.show()
        else:
            self.login_attempts += 1
            remaining_attempts = 3 - self.login_attempts
            if remaining_attempts > 0:
                QMessageBox.warning(self, '登录失败', f'用户名或密码错误！\n您还剩下 {remaining_attempts} 次尝试机会。')
                self.password_input.clear()
            else:
                QMessageBox.critical(self, '登录锁定', '登录失败次数过多，应用程序将退出！')
                QApplication.quit()