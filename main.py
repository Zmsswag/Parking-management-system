# main.py
import sys
from PyQt5.QtWidgets import QApplication
from database.database_manager import setup_database
from gui.login_window import LoginWindow

def main():
    """
    应用程序主函数。
    """
    # 1. 创建Qt应用程序实例
    app = QApplication(sys.argv)

    # 2. 初始化数据库和表结构
    # 这个函数只会在第一次运行时创建表，之后运行则无操作
    setup_database()

    # 3. 创建并显示登录窗口
    login_win = LoginWindow()
    login_win.show()

    # 4. 启动应用程序的事件循环，等待用户操作
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()