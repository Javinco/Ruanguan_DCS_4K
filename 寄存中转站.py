# import sys
# from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog
# from PyQt5.QtCore import *
# from Ui_MainWindow import Ui_MainWindow  # 确保导入 Ui_Unit_Window
# from Ui_pop_parameter import Ui_Dialog_Pop_Parameter  # 确保导入 Ui_Dialog
#
#
# class MainWindow(QMainWindow, Ui_MainWindow):
#     def __init__(self):
#         # 调用父类初始化方法
#         super(MainWindow, self).__init__()
#         # 初始化UI界面（来自Ui_MainWindow）
#         self.setupUi(self)
#         # 设置窗口全屏显示
#         self.setWindowState(Qt.WindowFullScreen)
#
#         # 新增弹窗实例初始化
#         self.pop_dialog = QDialog()  # 先创建对话框容器
#         self.pop_ui = Ui_Dialog_Pop_Parameter()  # 创建UI实例
#         self.pop_ui.setupUi(self.pop_dialog)  # 将UI挂载到对话框
#
#         # 连接信号（使用正确的事件绑定）
#         self.curve1.mousePressEvent = self.show_pop_parameter  # 使用鼠标事件
#
#         # ↓↓↓ 新增的时间功能代码 ↓↓↓
#         # 程序启动时立即更新一次时间显示
#         self.update_time()
#
#         # 创建定时器对象（parent设为当前窗口）
#         self.timer = QTimer(self)
#         # 连接定时器的timeout信号到更新时间方法（每秒触发一次）
#         self.timer.timeout.connect(self.update_time)
#         # 启动定时器，参数1000表示间隔1000毫秒（1秒）
#         self.timer.start(1000)
#         # ↑↑↑ 新增的时间功能代码 ↑↑↑
#
#     # 新增的时间获取方法 ↓↓↓
#
#     @staticmethod
#     def get_localtime():
#         # 从datetime模块导入datetime类
#         from datetime import datetime
#         # 获取当前日期时间对象
#         now = datetime.now()
#         # 返回格式化后的日期字符串和时间字符串
#         return now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")
#
#     # 新增的时间更新方法 ↓↓↓
#     def update_time(self):
#         # 调用获取时间方法，解包日期和时间
#         date_str, time_str = self.get_localtime()
#         # 直接设置日期标签的文本内容
#         self.title_DATA.setText(date_str)
#         # 直接设置时间标签的文本内容
#         self.title_time.setText(time_str)
#
#     # 新增的显示参数弹窗方法 ↓↓↓
#     def show_pop_parameter(self, event):
#         """显示参数弹窗"""
#         # 设置无边框 + 窗口置顶
#         self.pop_dialog.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
#         self.pop_dialog.show()
#
#
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     mainWindow = MainWindow()
#     mainWindow.show()  # 显示主窗口
#     sys.exit(app.exec_())  # 进入应用程序主循环

#       2025年2月25日13:24
# import sys
# from PyQt5 import QtCore  # 新增导入用于窗口属性设置
# from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog
# from PyQt5.QtCore import *
# from Ui_MainWindow import Ui_MainWindow  # 确保导入 Ui_Unit_Window
# from Ui_pop_parameter import Ui_Dialog_Pop_Parameter  # 确保导入 Ui_Dialog
#
#
# class MainWindow(QMainWindow, Ui_MainWindow):
#     def __init__(self):
#         # 调用父类初始化方法
#         super(MainWindow, self).__init__()
#         # 初始化UI界面（来自Ui_MainWindow）
#         self.dialog_original_pos = None  # 存储弹窗原始位置
#         self.drag_start_pos = None  # 记录鼠标拖动起始位置
#         self.setupUi(self)
#         # 设置窗口全屏显示
#         self.setWindowState(Qt.WindowFullScreen)
#
#         # 修改弹窗初始化方式 ▼▼▼
#         # 新增弹窗实例初始化
#         self.pop_dialog = CustomDialog()  # 使用自定义对话框替代普通QDialog
#         # 删除以下两行原始初始化代码：
#         # self.pop_ui = Ui_Dialog_Pop_Parameter()
#         # self.pop_ui.setupUi(self.pop_dialog)
#
#         # 连接信号（使用正确的事件绑定）
#         self.curve1.mousePressEvent = self.show_pop_parameter  # 使用鼠标事件
#
#         # ↓↓↓ 新增的时间功能代码 ↓↓↓
#         # 程序启动时立即更新一次时间显示
#         self.update_time()
#
#         # 创建定时器对象（parent设为当前窗口）
#         self.timer = QTimer(self)
#         # 连接定时器的timeout信号到更新时间方法（每秒触发一次）
#         self.timer.timeout.connect(self.update_time)
#         # 启动定时器，参数1000表示间隔1000毫秒（1秒）
#         self.timer.start(1000)
#         # ↑↑↑ 新增的时间功能代码 ↑↑↑
#         # 绑定弹窗鼠标事件
#         self.pop_dialog.mousePressEvent = self.dialog_mouse_press  # 绑定鼠标按下事件
#         self.pop_dialog.mouseMoveEvent = self.dialog_mouse_move  # 绑定鼠标移动事件
#
#     # 新增的时间获取方法 ↓↓↓
#
#     @staticmethod
#     def get_localtime():
#         # 从datetime模块导入datetime类
#         from datetime import datetime
#         # 获取当前日期时间对象
#         now = datetime.now()
#         # 返回格式化后的日期字符串和时间字符串
#         return now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")
#
#     # 新增的时间更新方法 ↓↓↓
#     def update_time(self):
#         # 调用获取时间方法，解包日期和时间
#         date_str, time_str = self.get_localtime()
#         # 直接设置日期标签的文本内容
#         self.title_DATA.setText(date_str)
#         # 直接设置时间标签的文本内容
#         self.title_time.setText(time_str)
#
#     # 新增的显示参数弹窗方法 ↓↓↓
#     def show_pop_parameter(self, event):
#         """显示参数弹窗"""
#         # 设置无边框 + 窗口置顶
#         self.pop_dialog.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, True)
#         self.center_dialog()
#         self.pop_dialog.show()
#
#     def center_dialog(self):
#         """居中显示弹窗"""
#         # 获取屏幕几何信息
#         screen = QApplication.primaryScreen().geometry()
#         # 计算居中坐标（基于弹窗和屏幕尺寸计算中心点）
#         x = (screen.width() - self.pop_dialog.width()) // 2
#         y = (screen.height() - self.pop_dialog.height()) // 2
#         self.pop_dialog.move(x, y)  # 移动弹窗到屏幕中心
#
#     def dialog_mouse_press(self, event):
#         """记录拖动起始位置"""
#         if event.button() == Qt.LeftButton:  # 判断是否左键点击
#             self.drag_start_pos = event.globalPos()  # 获取全局鼠标位置
#             self.dialog_original_pos = self.pop_dialog.pos()  # 记录弹窗当前位置
#             event.accept()  # 接受事件防止传递
#
#     def dialog_mouse_move(self, event):
#         """处理窗口拖动"""
#         if event.buttons() & Qt.LeftButton and hasattr(self, 'drag_start_pos'):
#             delta = event.globalPos() - self.drag_start_pos  # 计算移动距离差
#             self.pop_dialog.move(self.dialog_original_pos + delta)  # 更新弹窗位置
#             event.accept()  # 接受事件防止卡顿
#
#
# # 在MainWindow类定义前新增对话框子类
# class CustomDialog(QDialog):
#     def __init__(self):
#         super().__init__()  # 初始化弹窗属性
#         self.setAttribute(QtCore.Qt.WA_TranslucentBackground)  # 设置窗口透明背景（必须最先设置）
#         self.setWindowFlags(QtCore.Qt.FramelessWindowHint)  # 去除系统边框（同时禁用标题栏）
#         # 初始化UI组件（来自Qt Designer生成的Ui_pop_parameter.py文件）
#         self.ui = Ui_Dialog_Pop_Parameter()
#         self.ui.setupUi(self)
#
#
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     mainWindow = MainWindow()
#     mainWindow.show()  # 显示主窗口
#     sys.exit(app.exec_())  # 进入应用程序主循环





#2025年2月25日17:07 划分功能到各自的类中之前存档
# import sys
# from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog
# from PyQt5.QtCore import *
# from Ui_MainWindow import Ui_MainWindow  # 确保导入 Ui_Unit_Window
# from Ui_pop_parameter import Ui_Dialog_Pop_Parameter  # 确保导入 Ui_Dialog
#
#
# class MainWindow(QMainWindow, Ui_MainWindow):
#     def __init__(self):
#         # 调用父类初始化方法
#         super(MainWindow, self).__init__()
#         # 初始化UI界面（来自Ui_MainWindow）
#         self.setupUi(self)
#         # 设置窗口全屏显示
#         self.setWindowState(Qt.WindowFullScreen)
#         # 新增弹窗实例初始化
#         self.pop_dialog = QDialog()  # 先创建对话框容器
#         self.pop_ui = Ui_Dialog_Pop_Parameter()  # 创建UI实例
#         self.pop_ui.setupUi(self.pop_dialog)  # 将UI挂载到对话框
#         # 连接信号（使用正确的事件绑定）
#         self.curve1.mousePressEvent = self.show_pop_parameter  # 使用鼠标事件
#
#         # ↓↓↓ 新增的时间功能代码 ↓↓↓
#         # 程序启动时立即更新一次时间显示
#         self.update_time()
#         # 创建定时器对象（parent设为当前窗口）
#         self.timer = QTimer(self)
#         # 连接定时器的timeout信号到更新时间方法（每秒触发一次）
#         self.timer.timeout.connect(self.update_time)
#         # 启动定时器，参数1000表示间隔1000毫秒（1秒）
#         self.timer.start(1000)
#         # ↑↑↑ 新增的时间功能代码 ↑↑↑
#
#         self.dialog_original_pos = None  # 存储弹窗原始位置
#         self.drag_start_pos = None  # 记录鼠标拖动起始位置
#         # 绑定弹窗鼠标事件
#         self.pop_dialog.mousePressEvent = self.dialog_mouse_press  # 绑定鼠标按下事件
#         self.pop_dialog.mouseMoveEvent = self.dialog_mouse_move  # 绑定鼠标移动事件
#
#     # 新增的时间获取方法 ↓↓↓
#
#     @staticmethod
#     def get_localtime():
#         # 从datetime模块导入datetime类
#         from datetime import datetime
#         # 获取当前日期时间对象
#         now = datetime.now()
#         # 返回格式化后的日期字符串和时间字符串
#         return now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")
#
#     # 新增的时间更新方法 ↓↓↓
#     def update_time(self):
#         # 调用获取时间方法，解包日期和时间
#         date_str, time_str = self.get_localtime()
#         # 直接设置日期标签的文本内容
#         self.title_DATA.setText(date_str)
#         # 直接设置时间标签的文本内容
#         self.title_time.setText(time_str)
#
#     # 新增的显示参数弹窗方法 ↓↓↓
#     def show_pop_parameter(self, event):
#         """显示参数弹窗"""
#         # 设置无边框 + 窗口置顶
#         self.pop_dialog.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
#         self.center_dialog()
#         self.pop_dialog.show()
#
#     def center_dialog(self):
#         """居中显示弹窗"""
#         # 获取屏幕几何信息
#         screen = QApplication.primaryScreen().geometry()
#         # 计算居中坐标（基于弹窗和屏幕尺寸计算中心点）
#         x = (screen.width() - self.pop_dialog.width()) // 2
#         y = (screen.height() - self.pop_dialog.height()) // 2
#         self.pop_dialog.move(x, y)  # 移动弹窗到屏幕中心
#
#     def dialog_mouse_press(self, event):
#         """记录拖动起始位置"""
#         # 将点击位置转换为标题部件的坐标系
#         point_in_title = self.pop_ui.widget_title.rect().contains(event.pos())
#         # rect()获取标题部件的矩形区域，contains()判断点击坐标是否在区域内
#
#         if event.button() == Qt.LeftButton and point_in_title:
#             # 仅当左键点击且位置在标题栏时触发
#             self.drag_start_pos = event.globalPos()  # 记录点击时的全局坐标
#             self.dialog_original_pos = self.pop_dialog.pos()  # 存储弹窗初始位置
#             event.accept()  # 接受事件，阻止事件继续传播
#         else:
#             event.ignore()  # 忽略非标题区域事件，允许子部件接收事件
#
#     def dialog_mouse_move(self, event):
#         """处理窗口拖动"""
#         # 三重条件判断：
#         # 1. 左键保持按下状态(判断鼠标左键是否按下。)
#         # 2. 存在初始拖动位置记录(判断是否已经记录了拖动的起始位置（即是否已经执行过 dialog_mouse_press 方法）。)
#         # 3. 当前鼠标位置在标题区域内
#         if (event.buttons() & Qt.LeftButton and
#                 hasattr(self, 'drag_start_pos') and
#                 self.pop_ui.widget_title.rect().contains(event.pos())):
#
#             # 计算坐标偏移量（当前全局坐标 - 起始全局坐标）
#             delta = event.globalPos() - self.drag_start_pos
#             # 移动弹窗到新位置（初始位置 + 偏移量）
#             self.pop_dialog.move(self.dialog_original_pos + delta)
#             event.accept()  # 接受事件，确保操作流畅
#         else:
#             event.ignore()  # 忽略无效拖动，避免意外操作
#
#
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     mainWindow = MainWindow()
#     mainWindow.show()  # 显示主窗口
#     sys.exit(app.exec_())  # 进入应用程序主循环

# 2025/2/28 10:21
# 导入系统模块
# import sys
# # 从PyQt5导入需要的组件
# from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog, QLabel, QLineEdit
# from PyQt5.QtCore import Qt, QTimer
# # 导入自动生成的UI界面类
# from Ui_MainWindow import Ui_MainWindow
# from Ui_pop_parameter import Ui_Dialog_Pop_Parameter
# from Ui_pop_historical_parameter import Ui_Dialog_Pop_Historical_Parameter
# from Ui_pop_alarm import Ui_Dialog_alarm
# from Data_Manager import DataManager  # 添加导入
#
#
# # 参数弹窗类（继承QDialog和UI类）
# class ParameterDialog(QDialog, Ui_Dialog_Pop_Parameter):
#     def __init__(self):
#         # 调用父类构造方法
#         super().__init__()
#         # 初始化UI界面
#         self.setWindowFlags(Qt.FramelessWindowHint)  # 设置无边框窗口样式（隐藏标题栏和边框）
#         self.setAttribute(Qt.WA_TranslucentBackground)  # 启用透明背景属性（实现半透明/异形窗口效果）
#         self.setupUi(self)
#
#         self.dialog_historical = None  # 定义创建用于存储历史数据曲线弹窗的实例
#         self.pushButton_historical_curve.clicked.connect(self.show_dialog_pop_historical_parameter)  # 连接按钮点击信号
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
#     # 定义隐藏当前实时数据窗口，显示历史参数弹窗的方法
#     def show_dialog_pop_historical_parameter(self):
#         self.hide()  # 隐藏当前窗口
#         self.dialog_historical = HistoricalParameterDialog()  # 创建历史数据曲线对话框并传递父对象
#         self.dialog_historical.show()  # 显示弹窗
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
#         point_in_title = self.widget_title.rect().contains(event.pos())
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
#                 self.widget_title.rect().contains(event.pos())):
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
#     # 参数弹窗类新增关闭事件处理
#     # 重写窗口关闭事件处理方法（当窗口被关闭时自动触发）
#     def closeEvent(self, event):
#         """处理关闭事件：关闭关联的历史参数弹窗"""
#         # 检查是否存在历史参数弹窗实例
#         if self.dialog_historical:  # 判断dialog_historical是否已初始化
#             self.dialog_historical.close()  # 调用历史弹窗的关闭方法
#         super().closeEvent(event)  # 调用父类QDialog的关闭事件处理，确保正常关闭流程
#
#
# 历史参数弹窗类（继承QDialog和UI类）
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
# # 历史参数弹窗类（继承QDialog和UI类）
# class AlarmDialog(QDialog, Ui_Dialog_alarm):
#     def __init__(self):
#         # 调用父类构造方法
#         super().__init__()
#         # 初始化UI界面
#         self.setWindowFlags(Qt.FramelessWindowHint)  # 设置无边框窗口样式（隐藏标题栏和边框）
#         self.setAttribute(Qt.WA_TranslucentBackground)  # 启用透明背景属性（实现半透明/异形窗口效果）
#         self.setupUi(self)
#
#         # 设置窗口属性
#         self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)  # 置顶+无边框
#         self.right_down_dialog()  # 初始右下角显示
#
#     def right_down_dialog(self):
#         """将弹窗居中显示的方法"""
#         # 获取主屏幕尺寸
#         screen = QApplication.primaryScreen().geometry()
#         # 计算居中坐标（屏幕宽度-窗口宽度）/2
#         x = (screen.width() - self.width())
#         y = (screen.height() - self.height())
#         # 移动窗口到计算位置
#         self.move(x, y)
#
#
# # 主窗口类（继承QMainWindow和UI类）
# class MainWindow(QMainWindow, Ui_MainWindow):
#     def __init__(self):
#         # 调用父类构造方法
#         super().__init__()
#         # 初始化UI界面
#         self.setupUi(self)
#         # 设置窗口全屏显示
#         self.setWindowState(Qt.WindowFullScreen)
#
#         # 初始化参数弹窗（使用自定义弹窗类）
#         self.pop_dialog = ParameterDialog()
#         # 初始化报警弹窗（使用自定义弹窗类）
#         self.pop_alarm_dialog = AlarmDialog()
#
#         # 绑定曲线控件的鼠标点击事件
#         self.curve1.mousePressEvent = self.show_pop_parameter
#         # 绑定曲线控件的鼠标点击事件
#         self.pushButton_alarm.mousePressEvent = self.show_pop_alarm
#         # 绑定关闭按钮：点击时关闭所有窗口
#         self.Button_close.clicked.connect(self.close_all_windows)
#
#         # 初始化时间功能
#         self.timer = QTimer(self)  # 创建定时器对象
#         self.timer.timeout.connect(self.update_time)  # 连接定时信号
#         self.timer.start(1000)  # 启动定时器（1秒间隔）
#         self.update_time()  # 立即更新时间显示
#
#     def close_all_windows(self):
#         """关闭所有窗口的方法"""
#         self.pop_dialog.close()  # 关闭参数弹窗（会自动关闭其子弹窗）
#         self.pop_alarm_dialog.close()  # 关闭报警弹窗
#         self.close()  # 关闭主窗口
#
#     @staticmethod  # 静态方法，不依赖实例对象
#     def get_localtime():
#         """获取本地时间的静态方法"""
#         from datetime import datetime
#         now = datetime.now()  # 获取当前时间对象
#         # 返回格式化后的日期和时间字符串
#         return now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")
#
#     def update_time(self):
#         """更新时间显示的方法"""
#         date_str, time_str = self.get_localtime()  # 解包日期时间
#         self.title_DATA.setText(date_str)  # 更新日期标签
#         self.title_time.setText(time_str)  # 更新时间标签
#
#     def show_pop_parameter(self, event):
#         """显示参数弹窗的槽函数"""
#         self.pop_dialog.show()  # 显示弹窗
#         event.accept()  # 接受事件，阻止进一步传播
#
#     def show_pop_alarm(self, event):
#         """显示报警弹窗的槽函数"""
#         self.pop_alarm_dialog.show()  # 显示弹窗
#         event.accept()  # 接受事件，阻止进一步传播
#
#
# # 程序入口
# if __name__ == '__main__':
#     app = QApplication(sys.argv)  # 创建应用实例
#     mainWindow = MainWindow()  # 创建主窗口对象
#     mainWindow.show()  # 显示主窗口
#     sys.exit(app.exec_())  # 进入主事件循环


# 2025年3月4日 9:16 Data_Manager
# class DataManager:
#     # 初始化方法（构造器）
#     def __init__(self, host='localhost', user='root', password='admin', database='dcs_data'):
#         """数据库管理器
#         Args参数说明:
#             host: MySQL服务器地址（默认本地）
#             user: 数据库用户名（默认root）
#             password: 数据库密码（需根据实际修改）
#             database: 要连接的数据库名称（默认dcs_data）
#         """
#         # 创建配置字典存储连接参数
#         self.config = {
#             'host': host,  # 服务器地址
#             'user': user,  # 用户名
#             'password': password,  # 密码
#             'database': database,  # 数据库名
#             'raise_on_warnings': True  # 启用警告提示
#         }
#         # 初始化连接对象为None（空）
#         self.connection = None  # 数据库连接对象
#
#     def connect(self):
#         """建立数据库连接的方法"""
#         try:
#             # 使用mysql.connector建立连接
#             self.connection = mysql.connector.connect(**self.config)  # **解包字典参数
#             return True  # 返回连接成功状态
#         except Error as e:  # 捕获数据库错误
#             print(f"数据库连接失败: {e}")  # 打印错误信息
#             return False  # 返回连接失败状态
#
#     def get_realtime_data(self, id):
#         """获取设备实时数据的方法
#         Args参数:
#             id: 要查询的设备编号
#         Returns返回:
#             包含时间戳和数值的字典（查询失败返回None）
#         """
#         # 检查连接状态：如果未连接或连接中断则尝试重连
#         global cursor
#         if not self.connection or not self.connection.is_connected():
#             if not self.connect():  # 如果连接失败
#                 return None  # 返回空值
#
#         try:
#             # 创建字典格式游标（使查询结果以字典形式返回）
#             cursor = self.connection.cursor(dictionary=True)
#             # 定义SQL查询语句（使用三重引号多行字符串）
#             query = """
#                 SELECT
#                     timestamp,    -- 时间戳字段
#                     parameter1,       -- 数值字段1
#                     parameter2        -- 数值字段2
#                 FROM realtime_data          -- 从实时数据表查询
#                 WHERE id = %s        -- 根据设备ID过滤
#                 ORDER BY timestamp DESC    -- 按时间倒序排列
#                 LIMIT 1                    -- 仅获取最新一条记录
#             """
#             # 执行SQL查询（第二个参数是元组形式的查询参数）
#             cursor.execute(query, (id,))
#             # 获取单条查询结果
#             result = cursor.fetchone()
#
#             # 处理时间戳：将MySQL时间对象转为字符串
#             if result and 'timestamp' in result:  # 如果存在结果且包含时间戳
#                 # 使用strftime格式化时间（转成'年-月-日 时:分:秒'格式）
#                 result['timestamp'] = result['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
#
#             return result  # 返回处理后的结果
#         except Error as e:  # 捕获数据库操作错误
#             print(f"查询失败: {e}")  # 打印错误信息
#             return None  # 返回空值
#         finally:  # 最终执行块（无论是否异常都会执行）
#             if cursor:  # 如果游标对象存在
#                 cursor.close()  # 关闭游标释放资源

# 2025/3/4 17:10 get_realtime_data方法
# def get_realtime_data(self, id):
#     """获取实时数据（完全重构）
#     Args参数:
#         id: int类型，设备唯一标识符（当前版本暂未使用，保留参数位）
#     Returns返回:
#         dict: 包含最新实时数据的字典，键为字段名（timestamp/parameter1/parameter2）
#               None表示查询失败
#     """
#     try:
#         # 使用with语句自动管理连接生命周期（确保连接正确释放）
#         # self.connection_pool.get_connection()：从连接池获取数据库连接
#         with self.connection_pool.get_connection() as connection:  # connection是连接对象
#
#             # 使用with语句自动管理游标生命周期（确保游标正确关闭）
#             # dictionary=True：使查询结果以字典形式返回（键为字段名）
#             with connection.cursor(dictionary=True) as cursor:  # cursor是游标对象
#
#                 # 执行参数化SQL查询（使用三重引号定义多行字符串）
#                 # 查询逻辑说明：
#                 # 1. SELECT选择三个字段：timestamp时间戳、parameter1参数1、parameter2参数2
#                 # 2. FROM指定数据表（需与DataInserter插入的表名保持一致）
#                 # 3. WHERE筛选条件（当前使用id=%s但表结构无设备ID字段，需要修正）
#                 # 4. ORDER BY按时间戳降序排列（DESC表示从大到小）
#                 # 5. LIMIT 1限制返回1条记录
#                 cursor.execute("""
#                     SELECT
#                         timestamp,    -- 字段注释：数据记录的时间戳（DATETIME类型）
#                         parameter1,   -- 字段注释：设备参数1的测量值（DECIMAL类型）
#                         parameter2    -- 字段注释：设备参数2的测量值（DECIMAL类型）
#                     FROM factory1_1_realtime_data_jcj  -- 修正为DataInserter实际使用的表名（原表名有误）
#                     ORDER BY id DESC    -- 按自增主键降序排列（替代时间戳排序方案）
#                     LIMIT 1             -- 限制返回最新一条记录
#                 """)  # 移除了WHERE条件参数
#
#                 # 获取单行查询结果（fetchone()返回字典或None）
#                 result = cursor.fetchone()  # result示例：{'timestamp':, 'parameter1':, 'parameter2':}
#
#                 if result:
#                     # 时间戳格式转换：将datetime对象转为ISO8601标准格式字符串
#                     # isoformat()输出示例：'2023-08-08T12:34:56'
#                     result['timestamp'] = result['timestamp'].isoformat()  # 转换时间格式
#
#                 return result  # 返回结果字典（无数据时返回None）
#
#     # 异常处理部分（捕获数据库操作错误）
#     except Error as e:
#         # 格式化输出错误信息（e包含具体错误类型和代码）
#         print(f"数据库操作失败: {e}")  # 示例输出：数据库操作失败: 1146 (42S02): Table 'xxx' doesn't exist
#         return None  # 返回空值表示查询失败


# 曲线功能，坐标轴X轴有移动bug版本
# class RealTimeCurvePlotter(QWidget):
#     def __init__(self, parent_widget, table_name, params_config, y_limits=(-1, 1)):
#         super().__init__()
#         self.parent_widget = parent_widget
#         self.table_name = table_name
#         self.params_config = params_config
#         self.y_limits = y_limits
#         self.data_manager = DataManager()
#
#         self.setStyleSheet("background-color: rgb(192, 192, 192);")
#
#         self.figure = Figure(facecolor='black')
#         self.canvas = FigureCanvas(self.figure)
#         self.axes = self.figure.add_subplot(111)
#
#         # 预先计算刻度位置
#         now = datetime.datetime.now()
#         x_start = now - datetime.timedelta(minutes=10)
#         x_end = now
#         x_ticks = mdates.date2num([x_start + datetime.timedelta(minutes=i) for i in range(0, 11)])
#         self.fixed_x_ticks = x_ticks
#         self.fixed_x_ticklabels = [mdates.num2date(t).strftime('%H:%M') for t in x_ticks]
#
#         self._init_plot_style()
#         self._setup_layout()
#         self._init_timer()
#
#     def _setup_layout(self):
#         layout = QVBoxLayout(self.parent_widget)
#         layout.setContentsMargins(5, 5, 5, 5)  # 设置边距以显示坐标轴外区域
#         layout.addWidget(self.canvas)
#         self.parent_widget.setLayout(layout)
#
#     def _init_plot_style(self):
#         self.axes.set_facecolor('black')
#         self.axes.tick_params(axis='both', colors='white', width=4, labelsize=8)
#         self.axes.spines['bottom'].set_color('white')
#         self.axes.spines['bottom'].set_linewidth(2.0)
#         self.axes.spines['top'].set_color('white')
#         self.axes.spines['top'].set_linewidth(1.0)
#         self.axes.spines['left'].set_color('white')
#         self.axes.spines['left'].set_linewidth(2.0)
#         self.axes.spines['right'].set_color('white')
#         self.axes.spines['right'].set_linewidth(1.0)
#         self.axes.set_ylim(self.y_limits)
#         self.axes.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
#         self.figure.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
#
#     def _init_timer(self):
#         # 创建Qt定时器对象
#         self.timer = QTimer(self)
#         # 连接定时信号到更新曲线的槽函数
#         self.timer.timeout.connect(self.update_plot)  # type: ignore[attr-defined]
#         # 启动定时器（1000毫秒=1秒触发一次）
#         self.timer.start(1000)
#
#     def update_plot(self):
#         now = datetime.datetime.now()
#         x_start = now - datetime.timedelta(minutes=10)
#         x_end = now
#         data = self.data_manager.get_realtime_data(self.table_name)
#         if not data:
#             return
#
#         if not hasattr(self, 'time_data'):
#             self.time_data = []
#             self.curve3_data = []
#             self.curve4_data = []
#
#         self.time_data.append(now)
#         self.curve3_data.append(data.get(self.params_config['curve3'], 0))
#         self.curve4_data.append(data.get(self.params_config['curve4'], 0))
#
#         while self.time_data and (now - self.time_data[0]).seconds > 600:
#             self.time_data.pop(0)
#             self.curve3_data.pop(0)
#             self.curve4_data.pop(0)
#
#         self.axes.cla()
#
#         if len(self.time_data) > 1:
#             self.axes.plot(
#                 self.time_data,
#                 self.curve3_data,
#                 color='#00FFFF',
#                 linestyle='-',
#                 label='Curve3'
#             )
#             self.axes.plot(
#                 self.time_data,
#                 self.curve4_data,
#                 color='#00FF00',
#                 linestyle='-',
#                 label='Curve4'
#             )
#
#             # 使用固定的X轴刻度位置和标签
#             self.axes.set_xticks(self.fixed_x_ticks)
#             self.axes.set_xticklabels(self.fixed_x_ticklabels)
#
#         self.axes.axhline(y=data.get(self.params_config['curve1'], 0), color='#FF0000', linestyle='-')
#         self.axes.axhline(y=data.get(self.params_config['curve6'], 0), color='#FF0000', linestyle='-')
#         self.axes.axhline(y=data.get(self.params_config['curve2'], 0), color='#FFFF00', linestyle='-')
#         self.axes.axhline(y=data.get(self.params_config['curve5'], 0), color='#FFFF00', linestyle='-')
#         self.axes.axhline(y=0, color='#FFFFFF', linestyle='--')
#
#         self.axes.set_xlim([x_start, x_end])
#         self.axes.set_ylim(self.y_limits)
#
#         self.canvas.draw()
