# 导入PyQt5界面组件
from PyQt5.QtWidgets import QWidget, QVBoxLayout  # QWidget基础控件，QVBoxLayout垂直布局管理器
# 导入PyQtGraph绘图组件（替换matplotlib）
import pyqtgraph as pg
import numpy as np  # 导入numpy用于数值计算
from DataManager import historical_data_manager  # 自定义数据管理模块
import datetime

class HistoricalCurvePlotter(QWidget):
    def __init__(self, parent_widget, table_name, params_config, colors, y_limits=(-1, 1)):
        """历史单Y轴曲线构造器
        Args:
            parent_widget: 父级容器控件 - 用于承载本组件的父级GUI容器
            table_name: 数据库表名 - 指定数据来源的数据库表名称
            params_config: 曲线参数配置字典 - 格式为{'curve1': 'parameter1', 'curve2': 'parameter2', ...}
            y_limits: Y轴范围元组 - 控制Y轴显示范围 (最小值, 最大值)
        """
        super().__init__()  # 调用QWidget父类构造器
        self.parent_widget = parent_widget  # 存储父级控件引用
        self.table_name = table_name  # 存储数据表名称
        self.params_config = params_config  # 存储曲线配置字典
        self.y_limits = y_limits  # 存储Y轴范围设置
        self.data_manager = historical_data_manager  # 数据管理器实例

        # PyQtGraph图形初始化（替换matplotlib）
        self.plot_widget = pg.PlotWidget()
        self._init_plot_style()
        self._setup_layout()

        # 添加曲线可见性控制字典，默认所有曲线可见
        self.visible_curves = {f'curve{i}': True for i in range(1, 31)}
        # 初始化曲线对象字典，存储所有曲线的PlotDataItem对象
        self.curve_objects = {f'curve{i}': None for i in range(1, 31)}

        # 定义30种对比鲜明的颜色（适配黑色背景）
        self.curve_colors = colors

    def _init_plot_style(self):
        """初始化PyQtGraph绘图样式（参照RealtimeCurve.py）"""
        # 设置背景为黑色
        self.plot_widget.setBackground('black')

        # 获取绘图项
        plot_item = self.plot_widget.getPlotItem()

        # 设置坐标轴样式
        plot_item.getAxis('left').setPen(pg.mkPen(color='white', width=1))
        plot_item.getAxis('bottom').setPen(pg.mkPen(color='white', width=1))
        plot_item.getAxis('left').setTextPen(pg.mkPen(color='white'))
        plot_item.getAxis('bottom').setTextPen(pg.mkPen(color='white'))

        # 隐藏顶部和右侧坐标轴
        plot_item.hideAxis('top')
        plot_item.hideAxis('right')

        # 设置Y轴显示范围
        plot_item.setYRange(self.y_limits[0], self.y_limits[1])

        # 设置网格
        plot_item.showGrid(x=False, y=False)

        # 设置时间轴格式
        axis = pg.DateAxisItem(orientation='bottom')
        axis.setPen(pg.mkPen(color='white', width=1))
        axis.setTextPen(pg.mkPen(color='white'))
        plot_item.setAxisItems({'bottom': axis})

        # 禁用自动范围调整以提高性能
        plot_item.enableAutoRange(axis=pg.ViewBox.XAxis, enable=False)
        plot_item.enableAutoRange(axis=pg.ViewBox.YAxis, enable=False)

    def _setup_layout(self):
        """布局设置（与实时曲线一致）"""
        layout = QVBoxLayout(self.parent_widget)  # 创建垂直布局管理器
        layout.setContentsMargins(0, 0, 0, 0)  # 设置布局边距为0（不留空白）
        layout.addWidget(self.plot_widget)  # 将绘图组件添加到布局
        self.parent_widget.setLayout(layout)  # 为父控件应用布局

    def set_curve_visibility(self, curve_index, visible):
        """设置指定曲线的可见性
        Args:
            curve_index: 曲线索引（1-30）
            visible: 是否可见（True/False）
        """
        curve_key = f'curve{curve_index}'
        self.visible_curves[curve_key] = visible

        # 立即更新曲线可见性
        if self.curve_objects[curve_key] is not None:
            self.curve_objects[curve_key].setVisible(visible)

    def update_plot(self, start_time, end_time):
        """历史曲线更新方法
        Args:
            start_time: 查询起始时间
            end_time: 查询结束时间
        """
        # 从数据管理器获取指定时间范围的历史数据
        data = self.data_manager.get_historical_data(
            self.table_name, start_time, end_time
        )

        if not data:  # 无数据时处理
            # 清空所有曲线
            for curve_obj in self.curve_objects.values():
                if curve_obj is not None:
                    self.plot_widget.removeItem(curve_obj)
            self.curve_objects = {f'curve{i}': None for i in range(1, 31)}
            return

        # 清空现有曲线
        for curve_obj in self.curve_objects.values():
            if curve_obj is not None:
                self.plot_widget.removeItem(curve_obj)
        self.curve_objects = {f'curve{i}': None for i in range(1, 31)}

        # 提取时间戳列表并转换为时间戳格式
        timestamps = []
        for item in data:
            if isinstance(item['timestamp'], datetime.datetime):
                timestamps.append(item['timestamp'].timestamp())
            else:
                # 如果已经是时间戳格式，直接使用
                timestamps.append(item['timestamp'])

        # 循环绘制曲线
        for i in range(1, 31):
            curve_key = f'curve{i}'
            param_name = self.params_config.get(curve_key)
            if not param_name:  # 如果没有配置该曲线，跳过
                continue

            # 检查曲线是否应该可见
            if not self.visible_curves.get(curve_key, True):
                continue  # 如果不可见，跳过绘制

            # 安全获取字段值并确保为数值类型
            values = []
            for item in data:
                value = item.get(param_name, 0)
                if value is None:
                    value = 0
                try:
                    value = float(value)
                except (ValueError, TypeError):
                    value = 0.0
                values.append(value)

            # 转换为numpy数组
            time_array = np.array(timestamps, dtype=np.float64)
            value_array = np.array(values, dtype=np.float64)

            # 验证数组中没有None值
            if not (np.isnan(time_array).any() or np.isnan(value_array).any()) and len(time_array) > 0:
                # 设置线型（前16条为实线，后面为虚线）
                pen_style = pg.QtCore.Qt.SolidLine if i <= 16 else pg.QtCore.Qt.DashLine
                pen = pg.mkPen(color=self.curve_colors[i - 1], width=2, style=pen_style)

                # 绘制曲线
                curve_obj = self.plot_widget.plot(
                    time_array,
                    value_array,
                    pen=pen,
                    name=f"Curve{i}"
                )
                self.curve_objects[curve_key] = curve_obj

        # 设置X轴范围（根据实际数据时间范围）
        if len(timestamps) >= 2:
            self.plot_widget.getPlotItem().setXRange(timestamps[0], timestamps[-1])

        # 设置Y轴显示范围（根据初始化时设置的y_limits）
        self.plot_widget.getPlotItem().setYRange(self.y_limits[0], self.y_limits[1])