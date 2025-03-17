from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.dates as mdates
from Data_Manager import HistoricalDataManager


class HistoricalCurvePlotter(QWidget):
    def __init__(self, parent_widget, table_name, params_config, y_limits):
        """构造器初始化
        Args:
            parent_widget: 父级控件 - 用于界面布局的容器
            table_name: 数据表名 - 指定要查询的数据库表
            params_config: 参数配置 - 字典格式 {曲线名: 字段名}
            y_limits: Y轴范围 - 元组格式 (最小值, 最大值)
        """
        super().__init__()  # 调用父类QWidget初始化
        self.parent_widget = parent_widget  # 保存父控件引用
        self.table_name = table_name  # 存储数据表名称
        self.params_config = params_config  # 存储参数配置字典
        self.data_manager = HistoricalDataManager()  # 实例化历史数据管理器

        # 创建matplotlib图形对象（黑色背景）
        self.figure = Figure(facecolor='black')
        # 创建Qt兼容的画布组件
        self.canvas = FigureCanvas(self.figure)
        # 添加子图（1行1列第1个）
        self.axes = self.figure.add_subplot(111)
        # 初始化图表样式
        self._init_plot_style(y_limits)
        # 设置布局
        self._setup_layout()

    def _init_plot_style(self, y_limits):
        """初始化图表视觉样式"""
        self.axes.set_facecolor('black')  # 设置子图背景色为黑
        # 设置刻度样式：颜色白，线宽4
        self.axes.tick_params(axis='both', colors='white', width=4)
        # 设置坐标轴颜色为白
        self.axes.spines['bottom'].set_color('white')  # 底部坐标轴
        self.axes.spines['left'].set_color('white')    # 左侧坐标轴
        self.axes.set_ylim(y_limits)  # 设置Y轴显示范围
        # 设置X轴时间为时分秒格式
        self.axes.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    def _setup_layout(self):
        """设置控件布局"""
        layout = QVBoxLayout(self.parent_widget)  # 创建垂直布局
        layout.setContentsMargins(0, 0, 0, 0)     # 去除布局边距
        layout.addWidget(self.canvas)             # 将画布加入布局
        self.parent_widget.setLayout(layout)      # 为父控件应用布局

    def update_plot(self, start_time, end_time):
        """更新历史曲线
        Args:
            start_time: 查询起始时间（datetime对象）
            end_time: 查询结束时间（datetime对象）
        """
        # 获取时间段内的历史数据
        data = self.data_manager.get_historical_data(self.table_name, start_time, end_time)
        # 无数据处理
        if not data:
            print(f"[{self.table_name}] {start_time}~{end_time} 无历史数据")
            self.axes.cla()  # 清空坐标轴内容
            self.canvas.draw()  # 重绘画布（显示空白）
            return

        self.axes.cla()  # 清空旧图形
        # 提取时间戳列表（从数据字典的timestamp键）
        timestamps = [item['timestamp'] for item in data]

        # 遍历参数配置绘制各条曲线
        for curve_name, param in self.params_config.items():
            # 安全获取参数值（若字段不存在则返回0）
            values = [item.get(param, 0) for item in data]
            # 绘制曲线：X轴时间，Y轴数值，添加图例标签
            self.axes.plot(timestamps, values, label=curve_name)

        self.canvas.draw()  # 更新画布显示新图形