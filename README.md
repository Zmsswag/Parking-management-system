# 停车场智能管理系统

一个使用 Python、PyQt5、EasyOCR 和 SQLite 构建的桌面版停车场管理应用。

## 功能特性

- **用户认证**: 支持管理员和普通用户两种角色登录。
- **车牌识别**: 使用摄像头进行实时车牌识别。
- **自动化管理**: 自动记录车辆入场和出场信息。
- **计费系统**: 根据停车时长自动计算费用，并模拟支付流程。
- **管理后台**: 管理员拥有用户管理、车辆查询、数据统计等高级权限。
- **报表生成**: 可生成Excel格式的月度财务报表。
- **用户查询**: 普通用户可以查询自己名下绑定车辆的停车历史。

## 项目结构

停车场管理系统/
├── assets/ # 图片等静态资源
├── core/ # 核心后端逻辑
├── database/ # 数据库初始化与管理
├── gui/ # 所有PyQt5界面窗口和对话框
├── utils/ # 工具类脚本
├── main.py # 程序主入口
├── README.md # 本说明文件
└── requirements.txt # Python依赖库列表

## 安装与设置

1.  **克隆仓库:**
    ```bash
    git clone <你的仓库地址>
    cd 停车场管理系统
    ```

2.  **创建并激活虚拟环境 (推荐):**
    ```bash
    # Windows
    python -m venv venv
    venv\\Scripts\\activate

    # macOS / Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **安装依赖:**
    ```bash
    pip install -r requirements.txt
    ```
    *注意：EasyOCR 在首次运行时会自动下载所需的语言模型文件。*

## 如何运行

1.  确保你位于项目的根目录，并且虚拟环境已经激活。

2.  运行主程序:
    ```bash
    python main.py
    ```

3.  程序将显示登录窗口。你可以使用默认的管理员账户登录：
    - **用户名:** `admin`
    - **密码:** `admin123`