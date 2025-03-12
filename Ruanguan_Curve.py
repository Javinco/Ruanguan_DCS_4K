from PyQt5.QtWidgets import QWidget,QApplication, QVBoxLayout, QPushButton
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.dates as mdates
from Data_Manager import DataManager
from PyQt5.QtCore import QTimer, Qt
import datetime


class RealTimeCurvePlotter(QWidget):
    def __init__(self, parent_widget, table_name, params_config, y_limits=(-1, 1)):
        super().__init__()
        self.parent_widget = parent_widget
        self.table_name = table_name
        self.params_config = params_config  # 参数配置字典
        self.y_limits = y_limits
        self.data_manager = DataManager()

        # 初始化绘图组件
        self.figure = Figure(facecolor='black')
        self.canvas = FigureCanvas(self.figure)
        self.axes = self.figure.add_subplot(111)

        # 设置组件样式
        self._init_plot_style()
        self._setup_layout()
        self._init_timer()

    def _init_plot_style(self):
        # 坐标轴样式设置
        self.axes.set_facecolor('black')
        self.axes.tick_params(axis='both', colors='white')
        self.axes.spines['bottom'].set_color('white')
        self.axes.spines['top'].set_color('white')
        self.axes.spines['left'].set_color('white')
        self.axes.spines['right'].set_color('white')

        # 设置坐标范围
        self.axes.set_ylim(self.y_limits)
        self.axes.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

        # 去除边距
        self.figure.subplots_adjust(left=0, right=1, top=1, bottom=0)

    def _setup_layout(self):
        # 嵌入到父容器
        layout = QVBoxLayout(self.parent_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)
        self.parent_widget.setLayout(layout)

    def _init_timer(self):
        # 数据更新定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(1000)  # 1秒刷新

    def update_plot(self):
        # 获取当前时间范围
        now = datetime.datetime.now()
        x_start = now - datetime.timedelta(minutes=10)
        x_end = now

        # 获取数据库数据
        data = self.data_manager.get_realtime_data(self.table_name)
        if not data:
            return

        # 清空当前曲线
        self.axes.cla()

        # 绘制主曲线
        self.axes.plot(
            [now], [data.get(self.params_config['main_param'], 0)],
            color='#00FFFF', marker='o', linestyle='-'
        )

        # 绘制报警/预警线
        self.axes.axhline(
            y=data.get(self.params_config['alarm_upper'], 0),
            color='#FF0000', linestyle='--'
        )
        self.axes.axhline(
            y=data.get(self.params_config['alarm_lower'], 0),
            color='#FF0000', linestyle='--'
        )
        self.axes.axhline(
            y=data.get(self.params_config['warning_upper'], 0),
            color='#FFFF00', linestyle=':'
        )
        self.axes.axhline(
            y=data.get(self.params_config['warning_lower'], 0),
            color='#FFFF00', linestyle=':'
        )

        # 设置坐标轴范围
        self.axes.set_xlim([x_start, x_end])
        self.axes.set_ylim(self.y_limits)

        # 重绘画布
        self.canvas.draw()


# ... 原有代码保持不变 ...

# 添加以下测试类到文件底部
class CurveTestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("曲线测试窗口")
        self.resize(720, 280)  # 匹配实际容器尺寸

        # 创建测试用布局容器
        container = QWidget(self)
        container.setGeometry(0, 0, 720, 280)

        # 模拟参数配置
        params_config = {
            'main_param': 'parameter3',
            'alarm_upper': 'parameter1',
            'warning_upper': 'parameter2',
            'alarm_lower': 'parameter6',
            'warning_lower': 'parameter5'
        }

        # 初始化曲线组件（使用模拟数据）
        self.plotter = RealTimeCurvePlotter(
            parent_widget=container,
            table_name="test_data",
            params_config=params_config,
            y_limits=(-1, 1)
        )

        # 替换数据获取方法为本地模拟
        self.plotter.data_manager.get_realtime_data = self.mock_realtime_data

        # 添加关闭按钮
        self.btn_close = QPushButton("关闭测试", self)
        self.btn_close.clicked.connect(self.close)
        self.btn_close.move(620, 250)

    def mock_realtime_data(self, table_name):
        """模拟数据库数据生成"""
        from random import uniform
        return {
            'parameter1': uniform(0.8, 1.0),  # 报警上线
            'parameter2': uniform(0.6, 0.8),  # 预警上线
            'parameter3': uniform(-0.9, 0.9),  # 实时值
            'parameter5': uniform(-0.8, -0.6),  # 预警下线
            'parameter6': uniform(-1.0, -0.8)  # 报警下线
        }


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = CurveTestWindow()
    window.show()
    sys.exit(app.exec_())



# import sys
# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication
#
#
# class RuanguanCurve(QWidget):
#     def __init__(self):
#         super().__init__()
#
#         # 设置窗口大小
#         self.setFixedSize(365, 245)
#
#         # 初始化数据
#         self.time_data = np.linspace(0, 10, 100)  # 10分钟的时间数据
#         self.diameter_data = np.zeros(100)  # 管径差值初始化为0
#         self.index = 0  # 数据索引
#
#         # 创建图形和画布
#         self.figure, self.ax = plt.subplots()
#         self.canvas = FigureCanvas(self.figure)
#
#         # 设置坐标轴
#         self.ax.set_xlim(0, 10)  # X轴范围为0到10分钟
#         self.ax.set_ylim(-1, 1)  # Y轴范围为-1到1
#         self.ax.set_facecolor('black')  # 背景为黑色
#
#         # 绘制基准线和预警线、报警线（实线）
#         self.ax.axhline(0, color='white', linewidth=1)  # 基准线
#         self.ax.axhline(0.4, color='yellow', linewidth=1)  # 预警线
#         self.ax.axhline(-0.4, color='yellow', linewidth=1)  # 预警线
#         self.ax.axhline(0.7, color='red', linewidth=1)  # 报警线
#         self.ax.axhline(-0.7, color='red', linewidth=1)  # 报警线
#
#         # 设置Y轴刻度
#         self.ax.set_yticks([-1, 0, 1])
#         self.ax.yaxis.set_tick_params(color='white')  # Y轴刻度颜色为白色
#
#         # 设置X轴刻度
#         self.ax.xaxis.set_tick_params(color='white')  # X轴刻度颜色为白色
#         self.ax.set_xticks([0, 10])  # 只显示收尾的时间
#
#         # 创建布局
#         layout = QVBoxLayout()
#         layout.addWidget(self.canvas)
#
#         self.setLayout(layout)
#
#         # 启动定时器，每1000ms刷新一次
#         self.timer = self.startTimer(1000)
#
#     def timerEvent(self, event):
#         # 读取实时数据并更新曲线
#         self.update_data()
#         self.plot_curve()
#
#     def update_data(self):
#         # 模拟读取管径实时数据，这里用随机数代替
#         new_value = np.random.uniform(-1, 1)  # 随机生成管径差值
#         self.diameter_data[self.index] = new_value  # 更新数据
#         self.index = (self.index + 1) % 100  # 循环索引
#
#     def plot_curve(self):
#         # 清空当前图形
#         self.ax.clear()
#
#         # 重新绘制背景和线
#         self.ax.set_facecolor('black')
#         self.ax.set_xlim(0, 10)
#         self.ax.set_ylim(-1, 1)
#
#         # 绘制基准线和预警线、报警线（实线）
#         self.ax.axhline(0, color='white', linewidth=1)  # 基准线
#         self.ax.axhline(0.4, color='yellow', linewidth=1)  # 预警线
#         self.ax.axhline(-0.4, color='yellow', linewidth=1)  # 预警线
#         self.ax.axhline(0.7, color='red', linewidth=1)  # 报警线
#         self.ax.axhline(-0.7, color='red', linewidth=1)  # 报警线
#
#         # 设置Y轴刻度
#         self.ax.set_yticks([-1, 0, 1])
#         self.ax.yaxis.set_tick_params(color='white')  # Y轴刻度颜色为白色
#
#         # 设置X轴刻度
#         self.ax.xaxis.set_tick_params(color='white')  # X轴刻度颜色为白色
#         self.ax.set_xticks([0, 10])  # 只显示收尾的时间
#
#         # 绘制管径差值曲线
#         self.ax.plot(self.time_data, self.diameter_data, color='blue')
#
#         # 更新画布
#         self.canvas.draw()
#
#
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     window = RuanguanCurve()
#     window.show()
#     sys.exit(app.exec_())
