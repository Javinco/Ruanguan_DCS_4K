# # 导入系统模块
# import sys
# import random
# import time
# # 数据库相关模块
# import mysql.connector
# from threading import Thread
# from queue import Queue
# from datetime import datetime
#
# # PyQt5组件
# from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog, QMessageBox
# from PyQt5.QtCore import Qt, QTimer
# # 自动生成的UI界面类
# from Ui_MainWindow import Ui_MainWindow
# from Ui_pop_parameter import Ui_Dialog_Pop_Parameter
# from Ui_pop_historical_parameter import Ui_Dialog_Pop_Historical_Parameter
# from Ui_pop_alarm import Ui_Dialog_alarm
#
#
# # ==================== 数据库管理类 ====================
# class DatabaseManager:
#     """数据库统一管理类，封装所有数据库操作"""
#
#     def __init__(self, host='localhost', user='root', password='admin', db_name='dcs_data'):
#         """初始化数据库配置"""
#         self.config = {
#             'host': host,
#             'user': user,
#             'password': password,
#             'database': db_name,
#             'auth_plugin': 'mysql_native_password'
#         }
#         self.connection = None  # 数据库连接对象
#         self.connect()  # 建立连接
#         self.create_tables()  # 初始化数据表
#
#     def connect(self):
#         """建立数据库连接（含自动创建数据库）"""
#         try:
#             # 临时连接用于创建数据库
#             temp_conn = mysql.connector.connect(**{k: v for k, v in self.config.items() if k != 'database'})
#             temp_conn.cursor().execute(f"CREATE DATABASE IF NOT EXISTS {self.config['database']}")
#             temp_conn.close()
#
#             # 正式连接数据库
#             self.connection = mysql.connector.connect(**self.config)
#             print("数据库连接成功")
#         except Exception as e:
#             raise RuntimeError(f"数据库连接失败: {str(e)}")
#
#     def create_tables(self):
#         """创建系统所需数据表"""
#         tables = {
#             'realtime_data': """
#                 CREATE TABLE IF NOT EXISTS realtime_data (
#                     id INT AUTO_INCREMENT PRIMARY KEY,
#                     timestamp DATETIME,
#                     parameter1 FLOAT,
#                     parameter2 FLOAT
#                 ) ENGINE=InnoDB
#             """,
#             'history_data': """
#                 CREATE TABLE IF NOT EXISTS history_data (
#                     id INT AUTO_INCREMENT PRIMARY KEY,
#                     start_time DATETIME,
#                     end_time DATETIME,
#                     avg_value FLOAT
#                 ) ENGINE=InnoDB
#             """
#         }
#         try:
#             cursor = self.connection.cursor()
#             for table_name, ddl in tables.items():
#                 cursor.execute(ddl)
#             self.connection.commit()
#         except Exception as e:
#             raise RuntimeError(f"创建表失败: {str(e)}")
#
#     def insert_realtime_data(self, data):
#         """插入实时数据到数据库"""
#         query = """
#             INSERT INTO realtime_data
#             (timestamp, parameter1, parameter2)
#             VALUES (%s, %s, %s)
#         """
#         try:
#             cursor = self.connection.cursor()
#             cursor.execute(query, (
#                 data['timestamp'],
#                 data['param1'],
#                 data['param2']
#             ))
#             self.connection.commit()
#         except Exception as e:
#             print(f"数据插入失败: {str(e)}")
#
#     def __del__(self):
#         """析构时自动关闭数据库连接"""
#         if self.connection and self.connection.is_connected():
#             self.connection.close()
#             print("数据库连接已关闭")
#
#
# # ==================== 参数弹窗类 ====================
# class ParameterDialog(QDialog, Ui_Dialog_Pop_Parameter):
#     """实时参数显示弹窗"""
#
#     def __init__(self):
#         super().__init__()
#         # 窗口初始化设置
#         self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)  # 无边框+置顶
#         self.setAttribute(Qt.WA_TranslucentBackground)  # 透明背景
#         self.setupUi(self)
#
#         # 弹窗交互设置
#         self.dialog_historical = None  # 子弹窗实例引用
#         self.pushButton_historical_curve.clicked.connect(self.show_dialog_pop_historical_parameter)  # 历史曲线按钮绑定
#
#         # 窗口拖动相关变量
#         self.dialog_original_pos = None  # 窗口原始位置
#         self.drag_start_pos = None  # 拖动起始位置
#         self.mousePressEvent = self.dialog_mouse_press  # 鼠标按下事件绑定
#         self.mouseMoveEvent = self.dialog_mouse_move  # 鼠标移动事件绑定
#
#         self.center_dialog()  # 初始居中显示
#
#     # ---------- 弹窗交互方法 ----------
#     def show_dialog_pop_historical_parameter(self):
#         """显示历史参数弹窗"""
#         self.hide()  # 隐藏当前窗口
#         self.dialog_historical = HistoricalParameterDialog()  # 创建历史参数弹窗
#         self.dialog_historical.show()  # 显示弹窗
#
#     def center_dialog(self):
#         """弹窗居中显示"""
#         screen = QApplication.primaryScreen().geometry()
#         x = (screen.width() - self.width()) // 2
#         y = (screen.height() - self.height()) // 2
#         self.move(x, y)
#
#     # ---------- 窗口拖动方法 ----------
#     def dialog_mouse_press(self, event):
#         """处理鼠标按下事件"""
#         if event.button() == Qt.LeftButton and self.widget_title.rect().contains(event.pos()):
#             self.drag_start_pos = event.globalPos()
#             self.dialog_original_pos = self.pos()
#             event.accept()
#         else:
#             event.ignore()
#
#     def dialog_mouse_move(self, event):
#         """处理鼠标拖动事件"""
#         if (event.buttons() & Qt.LeftButton and
#                 hasattr(self, 'drag_start_pos') and
#                 self.widget_title.rect().contains(event.pos())):
#             delta = event.globalPos() - self.drag_start_pos
#             self.move(self.dialog_original_pos + delta)
#             event.accept()
#         else:
#             event.ignore()
#
#     def closeEvent(self, event):
#         """关闭事件处理"""
#         if self.dialog_historical:
#             self.dialog_historical.close()
#         super().closeEvent(event)
#
#
# # ==================== 历史参数弹窗类 ====================
# # 历史参数弹窗类（继承QDialog和UI类）
# class HistoricalParameterDialog(QDialog, Ui_Dialog_Pop_Historical_Parameter):
#     def __init__(self):
#         # 调用父类构造方法
#         super().__init__()
#         # 初始化UI界面
#         self.setWindowFlags(Qt.FramelessWindowHint)  # 设置无边框窗口样式（隐藏标题栏和边框）
#         self.setAttribute(Qt.WA_TranslucentBackground)  # 启用透明背景属性（实现半透明/异形窗口效果）
#         self.setupUi(self)
#
#         self.dialog_realtime = None  # 定义创建用于存储历史数据曲线弹窗的实例
#         self.pushButton_realtime.clicked.connect(self.show_dialog_pop_parameter)  # 连接按钮点击信号
#
#         # 初始化位置记录变量
#         self.dialog_original_pos = None  # 窗口原始位置
#         self.drag_start_pos = None  # 鼠标拖动起始位置
#         # 绑定鼠标事件到自身方法
#         self.mousePressEvent = self.dialog_mouse_press  # 按下事件处理
#         self.mouseMoveEvent = self.dialog_mouse_move  # 移动事件处理
#         # 设置窗口属性
#         self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)  # 置顶+无边框
#         self.center_dialog()  # 初始居中显示
#
#     # 定义隐藏当前历史数据窗口，显示实时参数弹窗的方法
#     def show_dialog_pop_parameter(self):
#         self.hide()  # 隐藏当前窗口
#         self.dialog_realtime = ParameterDialog()  # 创建实时数据曲线对话框并传递父对象
#         self.dialog_realtime.show()  # 显示弹窗
#
#     def center_dialog(self):
#         """将弹窗居中显示的方法"""
#         # 获取主屏幕尺寸
#         screen = QApplication.primaryScreen().geometry()
#         # 计算居中坐标（屏幕宽度-窗口宽度）/2
#         x = (screen.width() - self.width()) // 2
#         y = (screen.height() - self.height()) // 2
#         # 移动窗口到计算位置
#         self.move(x, y)
#
#     def dialog_mouse_press(self, event):
#         """处理鼠标按下事件（用于窗口拖动）"""
#         # 判断点击位置是否在标题栏区域内
#         point_in_title = self.widget_historical_title.rect().contains(event.pos())
#         # 当左键点击且位置在标题栏时
#         if event.button() == Qt.LeftButton and point_in_title:
#             # 记录全局鼠标位置（屏幕坐标系）
#             self.drag_start_pos = event.globalPos()
#             # 保存窗口当前位置
#             self.dialog_original_pos = self.pos()
#             # 接受事件，阻止事件传递
#             event.accept()
#         else:
#             # 忽略非标题栏区域的点击
#             event.ignore()
#
#     def dialog_mouse_move(self, event):
#         """处理鼠标移动事件（实现窗口拖动）"""
#         # 当满足三个条件时处理拖动：
#         # 1. 左键保持按下状态
#         # 2. 存在初始拖动位置记录
#         # 3. 鼠标在标题栏区域
#         if (event.buttons() & Qt.LeftButton and
#                 hasattr(self, 'drag_start_pos') and
#                 self.widget_historical_title.rect().contains(event.pos())):
#
#             # 计算位置偏移量（当前鼠标位置 - 起始位置）
#             delta = event.globalPos() - self.drag_start_pos
#             # 移动窗口到新位置（原始位置 + 偏移量）
#             self.move(self.dialog_original_pos + delta)
#             # 接受事件，确保操作流畅
#             event.accept()
#         else:
#             # 忽略无效拖动操作
#             event.ignore()
#
#     # 历史参数弹窗类新增关闭事件处理
#     # 重写窗口关闭事件处理方法（当窗口被关闭时自动触发）
#     def closeEvent(self, event):
#         """处理关闭事件：关闭关联的实时参数弹窗"""
#         # 检查是否存在实时参数弹窗实例
#         if self.dialog_realtime:  # 判断dialog_realtime是否已初始化
#             self.dialog_realtime.close()  # 调用实时弹窗的关闭方法
#         super().closeEvent(event)  # 调用父类QDialog的关闭事件处理，确保正常关闭流程
#
#
# # ==================== 报警弹窗类 ====================
# class AlarmDialog(QDialog, Ui_Dialog_alarm):
#     """报警信息弹窗"""
#
#     def __init__(self):
#         super().__init__()
#         self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
#         self.setAttribute(Qt.WA_TranslucentBackground)
#         self.setupUi(self)
#         self.right_down_dialog()  # 初始位置在右下角
#
#     def right_down_dialog(self):
#         """弹窗定位到右下角"""
#         screen = QApplication.primaryScreen().geometry()
#         x = screen.width() - self.width()
#         y = screen.height() - self.height()
#         self.move(x, y)
#
#
# # ==================== 主窗口类 ====================
# class MainWindow(QMainWindow, Ui_MainWindow):
#     """DCS系统主窗口"""
#
#     def __init__(self):
#         super().__init__()
#         # 初始化UI界面
#         self.setupUi(self)
#         self.setWindowState(Qt.WindowFullScreen)  # 全屏显示
#
#         # 数据库初始化
#         try:
#             self.db_manager = DatabaseManager()  # 创建数据库管理器
#         except RuntimeError as e:
#             QMessageBox.critical(self, "错误", str(e))
#             sys.exit(1)
#
#         # 弹窗初始化
#         self.pop_dialog = ParameterDialog()  # 参数弹窗
#         self.pop_alarm_dialog = AlarmDialog()  # 报警弹窗
#
#         # 事件绑定
#         self.curve1.mousePressEvent = self.show_pop_parameter  # 曲线点击事件
#         self.pushButton_alarm.mousePressEvent = self.show_pop_alarm  # 报警按钮事件
#         self.Button_close.clicked.connect(self.close_all_windows)  # 关闭按钮事件
#
#         # 数据采集初始化
#         self.data_queue = Queue()  # 数据队列
#         self.data_thread_running = True  # 线程运行标志
#         self.data_thread = Thread(target=self.data_acquisition, daemon=True)
#         self.data_thread.start()  # 启动数据采集线程
#
#         # 定时器初始化
#         self.timer = QTimer(self)
#         self.timer.timeout.connect(self.update_time)
#         self.timer.start(1000)  # 1秒更新一次时间
#         self.update_time()  # 立即更新
#
#     # ---------- 数据采集相关方法 ----------
#     def data_acquisition(self):
#         """模拟数据采集线程"""
#         while self.data_thread_running:
#             # 生成模拟数据
#             new_data = {
#                 'param1': random.uniform(0, 50),
#                 'param2': random.uniform(0, 100),
#                 'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             }
#             # 数据入库
#             self.db_manager.insert_realtime_data(new_data)
#             # 数据入队
#             self.data_queue.put(new_data)
#             time.sleep(0.2)  # 采集间隔
#
#     # ---------- 界面更新方法 ----------
#     @staticmethod
#     def get_localtime():
#         """获取当前时间"""
#         now = datetime.now()
#         return now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")
#
#     def update_time(self):
#         """更新时间显示"""
#         date_str, time_str = self.get_localtime()
#         self.title_DATA.setText(date_str)
#         self.title_time.setText(time_str)
#
#     # ---------- 弹窗控制方法 ----------
#     def show_pop_parameter(self, event):
#         """显示参数弹窗"""
#         self.pop_dialog.show()
#         event.accept()
#
#     def show_pop_alarm(self, event):
#         """显示报警弹窗"""
#         self.pop_alarm_dialog.show()
#         event.accept()
#
#     def close_all_windows(self):
#         """关闭所有窗口"""
#         self.pop_dialog.close()
#         self.pop_alarm_dialog.close()
#         self.close()
#
#     def closeEvent(self, event):
#         """关闭事件处理"""
#         self.data_thread_running = False  # 停止数据线程
#         if self.data_thread.is_alive():
#             self.data_thread.join()  # 等待线程结束
#         super().closeEvent(event)
#
#
# # ==================== 程序入口 ====================
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     mainWindow = MainWindow()
#     mainWindow.show()
#     sys.exit(app.exec_())
