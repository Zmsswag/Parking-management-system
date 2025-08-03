# gui/dialogs.py
import sqlite3
import calendar
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, QComboBox, QPushButton, 
                             QMessageBox, QFormLayout, QDateEdit, QTableWidget, 
                             QTableWidgetItem, QListWidget, QListWidgetItem, QLabel, QDialogButtonBox)
from PyQt5.QtCore import QDate, Qt
import os

class AddUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('添加新用户')
        self.setFixedSize(300, 200)
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.role_combo = QComboBox()
        self.role_combo.addItems(['user', 'admin'])

        form_layout.addRow('用户名:', self.username_input)
        form_layout.addRow('密码:', self.password_input)
        form_layout.addRow('角色:', self.role_combo)
        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def accept(self):
        username = self.username_input.text()
        password = self.password_input.text()
        role = self.role_combo.currentText()
        
        if not username or not password:
            QMessageBox.warning(self, '错误', '请填写所有字段！')
            return

        conn = sqlite3.connect('parking.db')
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
            conn.commit()
            QMessageBox.information(self, '成功', f'用户 {username} 添加成功！')
            super().accept()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, '错误', '用户名已存在！')
        finally:
            conn.close()

class SearchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('查询与管理停车记录')
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(self)
        
        # 搜索区域
        form_layout = QFormLayout()
        self.plate_input = QLineEdit()
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        
        # --- 修正部分 ---
        # 允许一个特殊的“空”值，并设置其显示文本
        self.date_input.setSpecialValueText(" ") 
        # 将日期清空到这个特殊值状态
        self.date_input.clear()
        # --- 修正结束 ---

        form_layout.addRow('车牌号 (模糊搜索):', self.plate_input)
        form_layout.addRow('入场日期 (可选):', self.date_input)
        layout.addLayout(form_layout)
        
        search_btn = QPushButton('搜索')
        search_btn.clicked.connect(self.search)
        layout.addWidget(search_btn)
        
        # 结果显示
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(6)
        self.result_table.setHorizontalHeaderLabels(['ID', '车牌号', '入场时间', '出场时间', '费用', '车位号'])
        self.result_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.result_table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.result_table)
        
        delete_btn = QPushButton('删除选中记录')
        delete_btn.setStyleSheet("background-color: #e74c3c; color: white;")
        delete_btn.clicked.connect(self.delete_selected)
        layout.addWidget(delete_btn)

        self.search() # 初始加载所有记录
        
    def search(self):
        plate_number = self.plate_input.text()
        date_str = self.date_input.text().strip() # 获取文本并去除前后空格
        
        conn = sqlite3.connect('parking.db')
        cursor = conn.cursor()
        
        query = "SELECT id, plate_number, entry_time, exit_time, fee, spot_number FROM parking_records WHERE 1=1"
        params = []
        
        if plate_number:
            query += " AND plate_number LIKE ?"
            params.append(f"%{plate_number}%")
            
        # 只有当日期框不是空的特殊值时，才添加日期条件
        if date_str:
            query += " AND DATE(entry_time) = ?"
            params.append(self.date_input.date().toString("yyyy-MM-dd"))
        
        query += " ORDER BY entry_time DESC"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        self.result_table.setRowCount(len(results))
        for i, record in enumerate(results):
            for j, value in enumerate(record):
                display_value = str(value) if value is not None else ""
                self.result_table.setItem(i, j, QTableWidgetItem(display_value))

    def delete_selected(self):
        selected_items = self.result_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, '提示', '请先选择要删除的记录。')
            return
            
        selected_rows = sorted(list(set(item.row() for item in selected_items)))
        
        reply = QMessageBox.question(self, '确认删除', f'确定要删除选中的 {len(selected_rows)} 条记录吗？\n此操作不可撤销！',
                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                                   
        if reply == QMessageBox.Yes:
            record_ids_to_delete = []
            for row in selected_rows:
                record_id = self.result_table.item(row, 0).text()
                record_ids_to_delete.append((int(record_id),))

            conn = sqlite3.connect('parking.db')
            cursor = conn.cursor()
            cursor.executemany("DELETE FROM parking_records WHERE id = ?", record_ids_to_delete)
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, '成功', '选中的记录已删除。')
            self.search()

# ... BindVehicleDialog, DeleteUserDialog, MonthSelectionDialog 保持不变 ...
class BindVehicleDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('绑定用户车辆')
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        self.username_input = QLineEdit()
        self.plate_input = QLineEdit()
        
        form_layout.addRow('用户名:', self.username_input)
        form_layout.addRow('车牌号:', self.plate_input)
        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def accept(self):
        username = self.username_input.text()
        plate_number = self.plate_input.text().upper()
        
        if not username or not plate_number:
            QMessageBox.warning(self, '错误', '用户名和车牌号均不能为空！')
            return
            
        conn = sqlite3.connect('parking.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        if not cursor.fetchone():
            QMessageBox.warning(self, '错误', f'用户 "{username}" 不存在！')
            conn.close()
            return
            
        try:
            cursor.execute("INSERT INTO user_vehicles (username, plate_number) VALUES (?, ?)", (username, plate_number))
            conn.commit()
            QMessageBox.information(self, '成功', '车辆绑定成功！')
            super().accept()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, '错误', '该车辆已经绑定，请勿重复操作！')
        finally:
            conn.close()

class DeleteUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('删除用户')
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel('选择要删除的用户 (管理员账户无法删除):'))
        
        self.user_list = QListWidget()
        self.user_list.setSelectionMode(QListWidget.SingleSelection)
        layout.addWidget(self.user_list)
        
        delete_btn = QPushButton('删除选中用户')
        delete_btn.setStyleSheet("background-color: #e74c3c; color: white;")
        delete_btn.clicked.connect(self.delete_user)
        layout.addWidget(delete_btn)
        
        self.load_users()
        
    def load_users(self):
        self.user_list.clear()
        conn = sqlite3.connect('parking.db')
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE role != 'admin' ORDER BY username")
        users = cursor.fetchall()
        conn.close()
        
        for user in users:
            self.user_list.addItem(user[0])
            
    def delete_user(self):
        current_item = self.user_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, '提示', '请先选择一个用户！')
            return
            
        username = current_item.text()
        
        reply = QMessageBox.question(self, '确认删除',
            f'确定要删除用户 "{username}" 吗？\n该用户的所有车辆绑定关系也将被一并删除，此操作不可撤销！',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            conn = sqlite3.connect('parking.db')
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM user_vehicles WHERE username = ?", (username,))
                cursor.execute("DELETE FROM users WHERE username = ?", (username,))
                conn.commit()
                QMessageBox.information(self, '成功', f'用户 {username} 已被成功删除！')
                self.load_users()
            except sqlite3.Error as e:
                conn.rollback()
                QMessageBox.critical(self, '数据库错误', f'删除用户时发生错误：{e}')
            finally:
                conn.close()

class MonthSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('选择报表月份')
        layout = QVBoxLayout(self)
        
        self.date_edit = QDateEdit(self)
        self.date_edit.setDisplayFormat('yyyy-MM')
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        layout.addWidget(QLabel("请选择要生成报表的年份和月份:"))
        layout.addWidget(self.date_edit)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_selected_date(self):
        return self.date_edit.date()