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
#         self.dialog_original_pos = None  # 存储弹窗原始位置
#         self.drag_start_pos = None       # 记录鼠标拖动起始位置
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
#         # 绑定弹窗鼠标事件
#         self.pop_dialog.mousePressEvent = self.dialog_mouse_press  # 绑定鼠标按下事件
#         self.pop_dialog.mouseMoveEvent = self.dialog_mouse_move    # 绑定鼠标移动事件
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
#         if event.button() == Qt.LeftButton:    # 判断是否左键点击
#             self.drag_start_pos = event.globalPos()     # 获取全局鼠标位置
#             self.dialog_original_pos = self.pop_dialog.pos()    # 记录弹窗当前位置
#             event.accept()  # 接受事件防止传递
#
#     def dialog_mouse_move(self, event):
#         """处理窗口拖动"""
#         if event.buttons() & Qt.LeftButton and hasattr(self, 'drag_start_pos'):
#             delta = event.globalPos() - self.drag_start_pos     # 计算移动距离差
#             self.pop_dialog.move(self.dialog_original_pos + delta)  # 更新弹窗位置
#             event.accept()  # 接受事件防止卡顿
#
#
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     mainWindow = MainWindow()
#     mainWindow.show()  # 显示主窗口
#     sys.exit(app.exec_())  # 进入应用程序主循环
