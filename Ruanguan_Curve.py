from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.dates as mdates
from Data_Manager import data_manager
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
        self.data_manager = data_manager
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

    def _init_plot_style(self):
        # 设置子图背景为黑色
        self.axes.set_facecolor('black')
        # 设置坐标轴刻度的颜色为白色
        self.axes.tick_params(axis='both', colors='white', width=4)
        # 设置四个坐标轴边框颜色为白色
        self.axes.spines['bottom'].set_color('white')
        self.axes.spines['bottom'].set_linewidth(1.0)
        self.axes.spines['left'].set_color('white')
        self.axes.spines['left'].set_linewidth(1.0)
        # 隐藏顶部和右侧边框
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)

        # 设置Y轴显示范围
        self.axes.set_ylim(self.y_limits)
        # 设置X轴时间格式为 小时:分钟:秒
        self.axes.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
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
    def update_plot(self,data):
        # 获取当前系统时间（精确到毫秒）
        now = datetime.datetime.now()
        # 计算X轴起始时间：当前时间往前推10分钟（用于显示时间窗口）
        x_start = now - datetime.timedelta(minutes=10)
        # X轴结束时间设置为当前时间（形成右边界）
        x_end = now
        # 通过数据管理器获取实时数据（self.table_name指定数据表）
        data = data
        # 数据有效性检查：如果没有获取到数据则退出本次更新
        if not data:
            return
        # 初始化历史数据存储结构（仅在首次运行时创建）
        if not hasattr(self, 'time_data'):
            self.time_data = []  # 存储时间戳的队列
            self.curve1_data = []  # 存储curve1数值的队列
            self.curve2_data = []  # 存储curve2数值的队列
            self.curve3_data = []  # 存储curve3数值的队列
            self.curve4_data = []  # 存储curve4数值的队列
            self.curve5_data = []  # 存储curve5数值的队列
            self.curve6_data = []  # 存储curve6数值的队列

        # 追加最新数据到队列末尾
        self.time_data.append(now)  # 当前时间戳入队
        # 从数据字典获取curve1参数值，若不存在则默认为0
        self.curve1_data.append(data.get(self.params_config['curve1'], 0))
        # 从数据字典获取curve2参数值，若不存在则默认为0
        self.curve2_data.append(data.get(self.params_config['curve2'], 0))
        # 从数据字典获取curve3参数值，若不存在则默认为0
        self.curve3_data.append(data.get(self.params_config['curve3'], 0))
        # 从数据字典获取curve4参数值，若不存在则默认为0
        self.curve4_data.append(data.get(self.params_config['curve4'], 0))
        # 从数据字典获取curve5参数值，若不存在则默认为0
        self.curve5_data.append(data.get(self.params_config['curve5'], 0))
        # 从数据字典获取curve6参数值，若不存在则默认为0
        self.curve6_data.append(data.get(self.params_config['curve6'], 0))
        # 维护数据队列长度（保持10分钟窗口）
        # while循环会删除超过10分钟（600秒）的旧数据
        while self.time_data and (now - self.time_data[0]).seconds > 600:
            self.time_data.pop(0)  # 移除最旧的时间戳
            self.curve1_data.pop(0)  # 移除对应的curve1数据
            self.curve2_data.pop(0)  # 移除对应的curve2数据
            self.curve3_data.pop(0)  # 移除对应的curve3数据
            self.curve4_data.pop(0)  # 移除对应的curve4数据
            self.curve5_data.pop(0)  # 移除对应的curve5数据
            self.curve6_data.pop(0)  # 移除对应的curve6数据
        # 清空当前坐标系（准备绘制新帧）
        self.axes.cla()

        # 绘制时序曲线（需至少2个数据点才能形成线段）
        if len(self.time_data) > 1:
            self.axes.plot(
                self.time_data,  # X轴数据序列（时间戳列表）
                self.curve1_data,  # Y轴数据序列（curve1数值列表）
                color='#FF0000',  # 十六进制颜色码（红色）
                linestyle='-',  # 线型：实线
                label='Curve1'  # 图例标签文本
            )
            # 绘制curve2曲线（黄色实线）
            self.axes.plot(
                self.time_data,  # X轴数据序列（时间戳列表）
                self.curve2_data,  # Y轴数据序列（curve2数值列表）
                color='#FFFF00',  # 十六进制颜色码（黄色）
                linestyle='-',  # 线型：实线
                label='Curve2'  # 图例标签文本
            )
            # 绘制curve3曲线（青蓝色实线）
            self.axes.plot(
                self.time_data,  # X轴数据序列（时间戳列表）
                self.curve3_data,  # Y轴数据序列（curve3数值列表）
                color='#00FFFF',  # 十六进制颜色码（青蓝色）
                linestyle='-',  # 线型：实线
                label='Curve3'  # 图例标签文本
            )
            # 绘制curve4曲线（绿色实线）
            self.axes.plot(
                self.time_data, # X轴数据序列（时间戳列表）
                self.curve4_data,   # Y轴数据序列（curve3数值列表）
                color='#00FF00',  # 十六进制颜色码（绿色）
                linestyle='-',  # 线型：实线
                label='Curve4'  # 图例标签文本
            )
            # 绘制curve5曲线（黄色实线）
            self.axes.plot(
                self.time_data,  # X轴数据序列（时间戳列表）
                self.curve5_data,  # Y轴数据序列（curve5数值列表）
                color='#FFFF00',  # 十六进制颜色码（黄色）
                linestyle='-',  # 线型：实线
                label='Curve6'  # 图例标签文本
            )
            # 绘制curve6曲线（红色色实线）
            self.axes.plot(
                self.time_data,  # X轴数据序列（时间戳列表）
                self.curve6_data,  # Y轴数据序列（curve6数值列表）
                color='#FF0000',  # 十六进制颜色码（红色）
                linestyle='-',  # 线型：实线
                label='Curve6'  # 图例标签文本
            )
            # # 添加图例（显示曲线标签），将图例添加到条件判断内（只有存在曲线时才会创建图例）
            # self.axes.legend(
            #     loc='upper right',  # 图例位置：右上角
            #     facecolor='black',  # 背景色：黑色
            #     labelcolor='white'  # 文字颜色：白色
            # )

        # 设置X轴显示范围（固定10分钟窗口）
        self.axes.set_xlim([x_start, x_end])
        # 设置Y轴显示范围（根据初始化时设置的y_limits）
        self.axes.set_ylim(self.y_limits)

        # 强制刷新画布（更新图形界面显示）
        self.canvas.draw()

class RealTimeJcjCurvePlotter(QWidget):
    def __init__(self, parent_widget, table_name, params_config, y_limits=(0, 200)):
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
        self.data_manager = data_manager
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

    def _init_plot_style(self):
        # 设置子图背景为黑色
        self.axes.set_facecolor('black')
        # 设置坐标轴刻度的颜色为白色
        self.axes.tick_params(axis='both', colors='white', width=4)
        # 设置四个坐标轴边框颜色为白色
        self.axes.spines['bottom'].set_color('white')
        self.axes.spines['bottom'].set_linewidth(1.0)
        self.axes.spines['left'].set_color('white')
        self.axes.spines['left'].set_linewidth(1.0)
        # 隐藏顶部和右侧边框
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)

        # 设置Y轴显示范围
        self.axes.set_ylim(self.y_limits)
        # 设置X轴时间格式为 小时:分钟:秒
        self.axes.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
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

    def update_jcj_plot(self,data):
        # 获取当前系统时间（精确到毫秒）
        now = datetime.datetime.now()
        # 计算X轴起始时间：当前时间往前推10分钟（用于显示时间窗口）
        x_start = now - datetime.timedelta(minutes=10)
        # X轴结束时间设置为当前时间（形成右边界）
        x_end = now
        # 通过数据管理器获取实时数据（self.table_name指定数据表）
        data = data
        # 数据有效性检查：如果没有获取到数据则退出本次更新
        if not data:
            return
        # 初始化历史数据存储结构（仅在首次运行时创建）
        if not hasattr(self, 'time_data'):
            self.time_data = []  # 存储时间戳的队列
            self.curve1_data = []  # 存储curve1数值的队列
            self.curve2_data = []  # 存储curve2数值的队列
            self.curve3_data = []  # 存储curve3数值的队列
            self.curve4_data = []  # 存储curve4数值的队列
            self.curve5_data = []  # 存储curve5数值的队列
            self.curve6_data = []  # 存储curve6数值的队列
        # 追加最新数据到队列末尾
        self.time_data.append(now)  # 当前时间戳入队
        # 从数据字典获取curve1参数值，若不存在则默认为0
        self.curve1_data.append(data.get(self.params_config['curve1'], 0))
        # 从数据字典获取curve2参数值，若不存在则默认为0
        self.curve2_data.append(data.get(self.params_config['curve2'], 0))
        # 从数据字典获取curve3参数值，若不存在则默认为0
        self.curve3_data.append(data.get(self.params_config['curve3'], 0))
        # 从数据字典获取curve4参数值，若不存在则默认为0
        self.curve4_data.append(data.get(self.params_config['curve4'], 0))
        # 从数据字典获取curve5参数值，若不存在则默认为0#
        self.curve5_data.append(data.get(self.params_config['curve5'], 0))
        # 从数据字典获取curve6参数值，若不存在则默认为0
        self.curve6_data.append(data.get(self.params_config['curve6'], 0))
        # 维护数据队列长度（保持10分钟窗口）
        # while循环会删除超过10分钟（600秒）的旧数据
        while self.time_data and (now - self.time_data[0]).seconds > 600:
            self.time_data.pop(0)  # 移除最旧的时间戳
            self.curve1_data.pop(0)  # 移除对应的curve1数据
            self.curve2_data.pop(0)  # 移除对应的curve2数据
            self.curve3_data.pop(0)  # 移除对应的curve3数据
            self.curve4_data.pop(0)  # 移除对应的curve4数据
            self.curve5_data.pop(0)  # 移除对应的curve5数据
            self.curve6_data.pop(0)  # 移除对应的curve6数据
        # 清空当前坐标系（准备绘制新帧）
        self.axes.cla()

        # 绘制时序曲线（需至少2个数据点才能形成线段）
        if len(self.time_data) > 1:
            # 绘制curve1曲线（红色实线）
            self.axes.plot(
                self.time_data,  # X轴数据序列（时间戳列表）
                self.curve1_data,  # Y轴数据序列（curve1数值列表）
                color='#FF0000',  # 十六进制颜色码（红色）
                linestyle='-',  # 线型：实线
                label='Curve1'  # 图例标签文本
            )
            # 绘制curve2曲线（黄色实线）
            self.axes.plot(
                self.time_data,  # X轴数据序列（时间戳列表）
                self.curve2_data,  # Y轴数据序列（curve2数值列表）
                color='#FFFF00',  # 十六进制颜色码（黄色）
                linestyle='-',  # 线型：实线
                label='Curve2'  # 图例标签文本
            )
            # 绘制curve3曲线（青蓝色实线）
            self.axes.plot(
                self.time_data,  # X轴数据序列（时间戳列表）
                self.curve3_data,  # Y轴数据序列（curve3数值列表）
                color='#00FFFF',  # 十六进制颜色码（青蓝色）
                linestyle='-',  # 线型：实线
                label='Curve3'  # 图例标签文本
            )
            # 绘制curve4曲线（绿色实线）
            self.axes.plot(
                self.time_data,
                self.curve4_data,
                color='#00FF00',  # 修正后的正确绿色值
                linestyle='-',
                label='Curve4'
            )
            # 绘制curve5曲线（黄色实线）
            self.axes.plot(
                self.time_data,  # X轴数据序列（时间戳列表）
                self.curve5_data,  # Y轴数据序列（curve5数值列表）
                color='#FFAA00',  # 十六进制颜色码（橙色）
                linestyle='-',  # 线型：实线
                label='Curve5'  # 图例标签文本
            )
            # 绘制curve6曲线（红色实线）
            self.axes.plot(
                self.time_data,  # X轴数据序列（时间戳列表）
                self.curve6_data,  # Y轴数据序列（curve6数值列表）
                color='#FF55FF',  # 十六进制颜色码（白色）
                linestyle='-',  # 线型：实线
                label='Curve6'  # 图例标签文本
            )
            # # 添加图例（显示曲线标签），将图例添加到条件判断内（只有存在曲线时才会创建图例）
            # self.axes.legend(
            #     loc='upper right',  # 图例位置：右上角
            #     facecolor='black',  # 背景色：黑色
            #     labelcolor='white'  # 文字颜色：白色
            # )

        # 设置X轴显示范围（固定10分钟窗口）
        self.axes.set_xlim([x_start, x_end])
        # 设置Y轴显示范围（根据初始化时设置的y_limits）
        self.axes.set_ylim(self.y_limits)

        # 强制刷新画布（更新图形界面显示）
        self.canvas.draw()

class RealTimeMainWindowCurve1(QWidget):
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
        self.data_manager = data_manager
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

    def _init_plot_style(self):
        # 设置子图背景为黑色
        self.axes.set_facecolor('black')
        # 设置坐标轴边框颜色为白色
        self.axes.spines['bottom'].set_color('white')
        self.axes.spines['bottom'].set_linewidth(1.0)
        self.axes.spines['left'].set_color('white')
        self.axes.spines['left'].set_linewidth(1.0)
        # 隐藏顶部和右侧边框
        self.axes.spines['top'].set_visible(False)
        self.axes.spines['right'].set_visible(False)

        # 设置Y轴显示范围
        self.axes.set_ylim(self.y_limits)
        # 设置X轴时间格式为 小时:分钟:秒
        self.axes.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        # left = 0：左边距为
        # 0 %（坐标轴紧贴图形左边界）
        # right = 1：右边距为
        # 100 %（坐标轴紧贴图形右边界）
        # top = 1：上边距为
        # 100 %（坐标轴紧贴图形上边界）
        # bottom = 0：下边距为
        # 0 %（坐标轴紧贴图形下边界）
        # 调整子图边距（新增以下两行）
        self.figure.subplots_adjust(left=0.08, right=0.92, top=0.92, bottom=0.08)  # 四周保留8%边距
        self.axes.set_position([0.1, 0.1, 0.8, 0.8])  # 坐标轴区域占80%空间


    def _setup_layout(self):
        # 创建垂直布局容器（用于在父容器中排列组件）
        layout = QVBoxLayout(self.parent_widget)
        # 设置父容器四周10像素边距
        layout.setContentsMargins(10, 10, 10, 10)
        # 将画布添加到布局中
        layout.addWidget(self.canvas)
        # 将布局设置到父容器
        self.parent_widget.setLayout(layout)
    def update_plot(self,data):
        # 获取当前系统时间（精确到毫秒）
        now = datetime.datetime.now()
        # 计算X轴起始时间：当前时间往前推10分钟（用于显示时间窗口）
        x_start = now - datetime.timedelta(minutes=10)
        # X轴结束时间设置为当前时间（形成右边界）
        x_end = now
        # 通过数据管理器获取实时数据（self.table_name指定数据表）
        data = data
        # 数据有效性检查：如果没有获取到数据则退出本次更新
        if not data:
            return
        # 初始化历史数据存储结构（仅在首次运行时创建）
        if not hasattr(self, 'time_data'):
            self.time_data = []  # 存储时间戳的队列
            self.curve1_data = []  # 存储curve1数值的队列
            self.curve2_data = []  # 存储curve2数值的队列
            self.curve3_data = []  # 存储curve3数值的队列
            self.curve4_data = []  # 存储curve4数值的队列
            self.curve5_data = []  # 存储curve5数值的队列
            self.curve6_data = []  # 存储curve6数值的队列

        # 追加最新数据到队列末尾
        self.time_data.append(now)  # 当前时间戳入队
        # 从数据字典获取curve1参数值，若不存在则默认为0
        self.curve1_data.append(data.get(self.params_config['curve1'], 0))
        # 从数据字典获取curve2参数值，若不存在则默认为0
        self.curve2_data.append(data.get(self.params_config['curve2'], 0))
        # 从数据字典获取curve3参数值，若不存在则默认为0
        self.curve3_data.append(data.get(self.params_config['curve3'], 0))
        # 从数据字典获取curve4参数值，若不存在则默认为0
        self.curve4_data.append(data.get(self.params_config['curve4'], 0))
        # 从数据字典获取curve5参数值，若不存在则默认为0
        self.curve5_data.append(data.get(self.params_config['curve5'], 0))
        # 从数据字典获取curve6参数值，若不存在则默认为0
        self.curve6_data.append(data.get(self.params_config['curve6'], 0))
        # 维护数据队列长度（保持10分钟窗口）
        # while循环会删除超过10分钟（600秒）的旧数据
        while self.time_data and (now - self.time_data[0]).seconds > 600:
            self.time_data.pop(0)  # 移除最旧的时间戳
            self.curve1_data.pop(0)  # 移除对应的curve1数据
            self.curve2_data.pop(0)  # 移除对应的curve2数据
            self.curve3_data.pop(0)  # 移除对应的curve3数据
            self.curve4_data.pop(0)  # 移除对应的curve4数据
            self.curve5_data.pop(0)  # 移除对应的curve5数据
            self.curve6_data.pop(0)  # 移除对应的curve6数据
        # 清空当前坐标系（准备绘制新帧）
        self.axes.cla()

        # 绘制时序曲线（需至少2个数据点才能形成线段）
        if len(self.time_data) > 1:
            self.axes.plot(
                self.time_data,  # X轴数据序列（时间戳列表）
                self.curve1_data,  # Y轴数据序列（curve1数值列表）
                color='#FF0000',  # 十六进制颜色码（红色）
                linestyle='-',  # 线型：实线
                label='Curve1'  # 图例标签文本
            )
            # 绘制curve2曲线（黄色实线）
            self.axes.plot(
                self.time_data,  # X轴数据序列（时间戳列表）
                self.curve2_data,  # Y轴数据序列（curve2数值列表）
                color='#FFFF00',  # 十六进制颜色码（黄色）
                linestyle='-',  # 线型：实线
                label='Curve2'  # 图例标签文本
            )
            # 绘制curve3曲线（青蓝色实线）
            self.axes.plot(
                self.time_data,  # X轴数据序列（时间戳列表）
                self.curve3_data,  # Y轴数据序列（curve3数值列表）
                color='#00FFFF',  # 十六进制颜色码（青蓝色）
                linestyle='-',  # 线型：实线
                label='Curve3'  # 图例标签文本
            )
            # 绘制curve4曲线（绿色实线）
            self.axes.plot(
                self.time_data, # X轴数据序列（时间戳列表）
                self.curve4_data,   # Y轴数据序列（curve3数值列表）
                color='#00FF00',  # 十六进制颜色码（绿色）
                linestyle='-',  # 线型：实线
                label='Curve4'  # 图例标签文本
            )
            # 绘制curve5曲线（黄色实线）
            self.axes.plot(
                self.time_data,  # X轴数据序列（时间戳列表）
                self.curve5_data,  # Y轴数据序列（curve5数值列表）
                color='#FFFF00',  # 十六进制颜色码（黄色）
                linestyle='-',  # 线型：实线
                label='Curve6'  # 图例标签文本
            )
            # 绘制curve6曲线（红色色实线）
            self.axes.plot(
                self.time_data,  # X轴数据序列（时间戳列表）
                self.curve6_data,  # Y轴数据序列（curve6数值列表）
                color='#FF0000',  # 十六进制颜色码（红色）
                linestyle='-',  # 线型：实线
                label='Curve6'  # 图例标签文本
            )
            # # 添加图例（显示曲线标签），将图例添加到条件判断内（只有存在曲线时才会创建图例）
            # self.axes.legend(
            #     loc='upper right',  # 图例位置：右上角
            #     facecolor='black',  # 背景色：黑色
            #     labelcolor='white'  # 文字颜色：白色
            # )

        # 设置X轴显示范围（固定10分钟窗口）
        self.axes.set_xlim([x_start, x_end])
        # 设置Y轴显示范围（根据初始化时设置的y_limits）
        self.axes.set_ylim(self.y_limits)

        # 强制刷新画布（更新图形界面显示）
        self.canvas.draw()