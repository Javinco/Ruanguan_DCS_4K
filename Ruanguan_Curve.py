from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QPushButton
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.dates as mdates
from Data_Manager import DataManager
from PyQt5.QtCore import QTimer, Qt
import datetime


class RealTimeCurvePlotter(QWidget):
    def __init__(self, parent_widget, table_name, params_config, y_limits=(-1, 1)):
        # 调用父类QWidget的初始化方法
        super().__init__()
        # 存储父容器窗口引用（用于界面布局）
        self.parent_widget = parent_widget
        # 数据库表名称（用于数据查询）
        self.table_name = table_name
        # 参数配置字典（包含曲线和报警线的参数名称）
        self.params_config = params_config
        # Y轴显示范围（例如：-1到1）
        self.y_limits = y_limits
        # 创建数据管理器实例（用于数据库操作）
        self.data_manager = DataManager()

        # 创建Matplotlib图形对象（设置黑色背景）
        self.figure = Figure(facecolor='black')
        # 创建Qt画布组件，用于显示图形
        self.canvas = FigureCanvas(self.figure)
        # 在图形上添加子图（1行1列第1个图）
        self.axes = self.figure.add_subplot(111)

        # 初始化图形样式
        self._init_plot_style()
        # 设置界面布局
        self._setup_layout()
        # 初始化定时器（用于实时更新）
        self._init_timer()

    def _init_plot_style(self):
        # 设置子图背景为黑色
        self.axes.set_facecolor('black')
        # 设置坐标轴刻度的颜色为白色
        self.axes.tick_params(axis='both', colors='white', width=4)
        # 设置四个坐标轴边框颜色为白色
        self.axes.spines['bottom'].set_color('white')
        self.axes.spines['bottom'].set_linewidth(5.0)
        self.axes.spines['top'].set_color('white')
        self.axes.spines['top'].set_linewidth(1.0)
        self.axes.spines['left'].set_color('white')
        self.axes.spines['left'].set_linewidth(5.0)
        self.axes.spines['right'].set_color('white')
        self.axes.spines['right'].set_linewidth(1.0)

        # 设置Y轴显示范围
        self.axes.set_ylim(self.y_limits)
        # 设置X轴时间格式为 小时:分钟
        self.axes.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

        # 去除图形边距（让曲线充满整个区域）
        self.figure.subplots_adjust(left=0, right=1, top=1, bottom=0)
        # left = 0：左边距为
        # 0 %（坐标轴紧贴图形左边界）
        # right = 1：右边距为
        # 100 %（坐标轴紧贴图形右边界）
        # top = 1：上边距为
        # 100 %（坐标轴紧贴图形上边界）
        # bottom = 0：下边距为
        # 0 %（坐标轴紧贴图形下边界）

    def _setup_layout(self):
        # 创建垂直布局容器（用于在父容器中排列组件）
        layout = QVBoxLayout(self.parent_widget)
        # 设置布局边距为0（不留空白）
        layout.setContentsMargins(0, 0, 0, 0)
        # 将画布添加到布局中
        layout.addWidget(self.canvas)
        # 将布局设置到父容器
        self.parent_widget.setLayout(layout)

    def _init_timer(self):
        # 创建Qt定时器对象
        self.timer = QTimer(self)
        # 连接定时信号到更新曲线的槽函数
        self.timer.timeout.connect(self.update_plot)  # type: ignore[attr-defined]
        # 启动定时器（1000毫秒=1秒触发一次）
        self.timer.start(1000)

    def update_plot(self):
        # 获取当前系统时间
        now = datetime.datetime.now()
        # 计算X轴起始时间（当前时间向前10分钟）
        x_start = now - datetime.timedelta(minutes=10)
        # X轴结束时间为当前时间
        x_end = now

        # 从数据库获取实时数据（通过数据管理器）
        data = self.data_manager.get_realtime_data(self.table_name)
        # 如果没有数据则直接返回
        if not data:
            return

        # 清空当前子图内容（准备绘制新数据）
        self.axes.cla()

        # 绘制主曲线（青蓝色实线）
        self.axes.plot(
            [now],  # X轴数据（当前时间）
            [data.get(self.params_config['curve3'], 0)],  # Y轴数据（从数据中获取主参数值）
            color='#00FFFF',  # 青蓝色
            marker='o',  # 数据点标记为圆形
            linestyle='-'  # 实线样式
        )
        # # 绘制曲线4（绿色实线）
        # self.axes.plot(
        #     [now],  # X轴数据（当前时间）
        #     [data.get(self.params_config['curve4'], 0)],  # Y轴数据（从数据中获取主参数值）
        #     color='##00FF00',  # 绿色
        #     marker='o',  # 数据点标记为圆形
        #     linestyle='-'  # 实线样式
        # )

        # 绘制报警线（红色实线）
        self.axes.axhline(
            y=data.get(self.params_config['curve4'], 0),  # 报警上限值
            color='#00FF00',    # 绿色
            linestyle='-'  # 实线样式
        )

        # 绘制报警线（红色实线）
        self.axes.axhline(
            y=data.get(self.params_config['curve1'], 0),  # 报警上限值
            color='#FF0000',    # 红色
            linestyle='-'  # 实线样式
        )
        self.axes.axhline(
            y=data.get(self.params_config['curve6'], 0),   # 报警下限值
            color='#FF0000',    # 红色
            linestyle='-'   # 实线样式
        )
        self.axes.axhline(
            y=data.get(self.params_config['curve2'], 0),
            color='#FFFF00',    # 黄色
            linestyle='-'   # 实线样式
        )
        self.axes.axhline(
            y=data.get(self.params_config['curve5'], 0),
            color='#FFFF00',    # 红色
            linestyle='-'   # 实线样式
        )

        # 设置X轴时间范围（最近10分钟）
        self.axes.set_xlim([x_start, x_end])
        # print('起始时间：', x_start, '现在时间：', x_end)
        # 设置Y轴显示范围
        self.axes.set_ylim(self.y_limits)

        # 重绘画布以显示更新
        self.canvas.draw()
