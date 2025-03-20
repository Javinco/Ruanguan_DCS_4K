# 导入PyQt5界面组件
from PyQt5.QtWidgets import QWidget, QVBoxLayout  # QWidget基础控件，QVBoxLayout垂直布局管理器
# 导入matplotlib绘图组件
from matplotlib.figure import Figure  # 图形容器基类
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas  # Qt兼容的画布组件
import matplotlib.dates as mdates  # 日期格式化模块
import matplotlib.ticker as mticker
from Data_Manager import historical_data_manager  # 自定义数据管理模块

class HistoricalCurvePlotter(QWidget):
    def __init__(self, parent_widget, table_name, params_config, y_limits=(-1, 1)):
        """增强型历史曲线构造器
        Args:
            parent_widget: 父级容器控件 - 用于承载本组件的父级GUI容器
            table_name: 数据库表名 - 指定数据来源的数据库表名称
            params_config: 曲线配置字典 - 格式示例：
                {
                    'curve1': {
                        'field': 'parameter1',  # 数据库字段名 - 对应数据库表的列名
                        'color': '#FF0000',     # 曲线颜色 - 十六进制颜色代码
                        'linestyle': '-',       # 线型 - 支持matplotlib线型参数
                        'label': '压力曲线'      # 显示标签 - 图例中显示的文本
                    },
                    # ...其他曲线配置
                }
            y_limits: Y轴范围元组 - 控制Y轴显示范围 (最小值, 最大值)
        """
        super().__init__()  # 调用QWidget父类构造器
        self.parent_widget = parent_widget  # 存储父级控件引用
        self.table_name = table_name  # 存储数据表名称
        self.params_config = params_config  # 存储曲线配置字典
        self.y_limits = y_limits  # 存储Y轴范围设置
        self.data_manager = historical_data_manager  # 数据管理器实例

        # Matplotlib图形初始化
        self.figure = Figure(facecolor='black')  # 创建黑色背景的图形对象
        self.canvas = FigureCanvas(self.figure)  # 创建Qt兼容的画布组件
        self.axes = self.figure.add_subplot(111)  # 添加1x1网格的第一个子图

        # 样式初始化
        self._init_plot_style()  # 调用样式初始化方法
        self._setup_layout()  # 调用布局设置方法

    def _init_plot_style(self):
        """初始化与实时曲线一致的视觉样式"""
        # 坐标系样式
        self.axes.set_facecolor('black')  # 设置子图背景色为黑色
        self.axes.tick_params(axis='both', colors='white', width=4)  # 设置刻度颜色和宽度

        # 坐标轴边框样式
        for spine in ['bottom', 'left']:  # 遍历底部和左侧坐标轴
            self.axes.spines[spine].set_color('white')  # 设置坐标轴颜色为白色
            self.axes.spines[spine].set_linewidth(1.0)  # 设置坐标轴线宽
        for spine in ['top', 'right']:  # 遍历顶部和右侧坐标轴
            self.axes.spines[spine].set_visible(False)  # 隐藏坐标轴

        # 坐标范围与格式
        self.axes.set_ylim(self.y_limits)  # 设置Y轴显示范围
        self.axes.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))  # 设置时间显示格式

        # 边距调整（与RealTimeMainWindowCurve1一致）
        self.figure.subplots_adjust(left=0.08, right=0.92, top=0.92, bottom=0.08)  # 调整图形边距
        self.axes.set_position([0.1, 0.1, 0.8, 0.8])  # 设置子图在画布中的位置和大小

    def _setup_layout(self):
        """布局设置（与实时曲线一致）"""
        layout = QVBoxLayout(self.parent_widget)  # 创建垂直布局管理器
        layout.setContentsMargins(10, 10, 10, 10)  # 设置布局边距（左，上，右，下）
        layout.addWidget(self.canvas)  # 将画布添加到布局
        self.parent_widget.setLayout(layout)  # 为父控件应用布局

    def update_plot(self, start_time, end_time):
        """增强型历史曲线更新方法"""
        # 从数据管理器获取指定时间范围的历史数据
        data = self.data_manager.get_historical_data(
            self.table_name, start_time, end_time
        )

        if not data:  # 无数据时处理
            self.axes.cla()  # 清空坐标系
            self.canvas.draw()  # 重绘画布
            return

        self.axes.cla()  # 清空旧图形
        timestamps = [item['timestamp'] for item in data]  # 提取时间戳列表

        # 遍历曲线配置绘制各条曲线
        for curve_name, config in self.params_config.items():
            values = [item.get(config['field'], 0) for item in data]  # 安全获取字段值
            self.axes.plot(  # 绘制曲线
                timestamps,
                values,
                color=config.get('color', '#FFFFFF'),  # 颜色默认白色
                linestyle=config.get('linestyle', '-'),  # 线型默认实线
                label=config.get('label', curve_name)  # 标签默认使用曲线名
            )
            # 设置X轴刻度（固定5个等距刻度）
            if len(timestamps) >= 2:  # 数据有效性检查：至少需要2个时间点才能生成范围
                # 生成5个等分时间点（包含首尾）
                import numpy as np  # 临时导入numpy用于数值计算（实际应在文件顶部导入）
                x_ticks = np.linspace(  # 生成线性等分数列
                    mdates.date2num(timestamps[0]),  # 将起始时间转为matplotlib数值格式
                    mdates.date2num(timestamps[-1]),  # 将结束时间转为matplotlib数值格式
                    5  # 指定生成5个等分点
                )
                self.axes.xaxis.set_major_locator(  # 设置主刻度定位器
                    mticker.FixedLocator(x_ticks)  # 使用固定位置的刻度（mticker已顶部导入）
                )

            # 设置坐标格式（继承原有逻辑）
            self.axes.xaxis.set_major_formatter(  # 应用时间格式化器
                mdates.DateFormatter('%H:%M:%S')  # 保持时分秒显示格式
            )
            # 设置X轴范围（根据实际数据时间范围）
            self.axes.set_xlim([  # 控制坐标轴显示范围
                timestamps[0],  # 取第一个数据点的时间戳作为起点
                timestamps[-1]  # 取最后一个数据点的时间戳作为终点
            ])
        self.axes.set_ylim(self.y_limits)  # Y轴数值范围

        self.canvas.draw()  # 更新画布显示