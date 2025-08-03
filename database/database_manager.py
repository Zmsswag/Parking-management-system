# database/database_manager.py
import sqlite3

def setup_database():
    """初始化数据库并创建所需的表结构"""
    # 连接到SQLite数据库，如果文件不存在，则会自动创建
    conn = sqlite3.connect('parking.db')
    cursor = conn.cursor()

    # 创建用户表 (users)
    # username: 用户名，主键
    # password: 密码
    # role: 角色 ('admin' 或 'user')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('admin', 'user'))
    )
    ''')

    # 创建停车记录表 (parking_records)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS parking_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        plate_number TEXT NOT NULL,
        entry_time TIMESTAMP NOT NULL,
        exit_time TIMESTAMP,
        fee REAL,
        spot_number INTEGER NOT NULL
    )
    ''')

    # 创建用户与车辆的关联表 (user_vehicles)
    # 用于记录哪个用户绑定了哪个车牌
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_vehicles (
        username TEXT,
        plate_number TEXT,
        PRIMARY KEY (username, plate_number),
        FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
    )
    ''')

    # 添加一个默认的管理员账户，如果不存在的话
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       ('admin', 'admin123', 'admin'))
    except sqlite3.IntegrityError:
        # 如果用户名已存在，则会抛出此异常，我们直接忽略即可
        pass

    # 提交事务并关闭连接
    conn.commit()
    conn.close()
    print("数据库初始化完成。")