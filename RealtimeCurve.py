from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import QObject, pyqtSignal, QThread
import pyqtgraph as pg
from Data_Manager import data_manager
import datetime
from collections import deque
import numpy as np
import time


# ---------------------------------曲线数据处理工作线程类---------------------------------
class CurveDataProcessor(QObject):
    """曲线数据处理工作线程类，负责处理数据并准备绘图参数"""
    # 定义信号，用于将处理结果传递给主线程
    data_processed = pyqtSignal(dict)  # 参数：处理后的绘图数据
    finished = pyqtSignal()  # 完成信号

    def __init__(self, params_config, visible_curves, time_interval_minutes, curve_colors):
        """初始化曲线数据处理工作线程
        参数:
            params_config: 参数配置字典
            visible_curves: 曲线可见性字典
            time_interval_minutes: 时间间隔（分钟）
            curve_colors: 曲线颜色列表
        """
        super().__init__()
        self.params_config = params_config
        self.visible_curves = visible_curves
        self.time_interval_minutes = time_interval_minutes
        self.curve_colors = curve_colors
        self.running = True

        # 计算最大数据点数量（基于时间间隔和0.1秒采样率）
        max_points = self.time_interval_minutes * 600
        self.time_data = deque(maxlen=max_points)
        self.curve_data = {f'curve{i}': deque(maxlen=max_points) for i in range(1, 7)}

    def process_data(self, data):
        """处理新的数据点
        参数:
            data: 新的数据字典
        """
        if not self.running or not data:
            return

        # 获取当前系统时间戳（转换为秒）
        now = datetime.datetime.now()
        timestamp = now.timestamp()

        # 追加最新数据到队列末尾
        self.time_data.append(timestamp)

        # 循环追加所有曲线数据
        for i in range(1, 7):
            curve_key = f'curve{i}'
            param_name = self.params_config.get(curve_key)
            if param_name:
                # 获取数据值，确保不为None
                value = data.get(param_name, 0)
                # 验证数据类型，确保为数值类型
                if value is None:
                    value = 0
                try:
                    # 尝试转换为浮点数
                    value = float(value)
                except (ValueError, TypeError):
                    value = 0.0
                self.curve_data[curve_key].append(value)

        # 准备绘图数据
        if len(self.time_data) > 1:
            plot_data = self._prepare_plot_data(timestamp)
            # 发送处理结果信号
            self.data_processed.emit(plot_data)

    def _prepare_plot_data(self, current_timestamp):
        """准备绘图数据
        参数:
            current_timestamp: 当前时间戳
        返回:
            dict: 包含绘图所需所有数据的字典
        """
        # 计算时间范围
        x_start = current_timestamp - (self.time_interval_minutes * 60)
        x_end = current_timestamp

        # 准备曲线数据
        curves_to_draw = []

        for i in range(1, 7):
            curve_key = f'curve{i}'

            # 检查曲线是否应该可见
            if not self.visible_curves.get(curve_key, True):
                continue

            if curve_key in self.curve_data and len(self.curve_data[curve_key]) > 0:
                # 前16条为实线，后13条为虚线
                linestyle = 'solid' if i <= 16 else 'dashed'
                color = self.curve_colors[i - 1]

                # 获取数据并进行验证
                time_list = list(self.time_data)
                curve_list = list(self.curve_data[curve_key])

                # 确保数据长度一致
                min_length = min(len(time_list), len(curve_list))
                if min_length > 0:
                    time_array = np.array(time_list[-min_length:], dtype=np.float64)
                    curve_array = np.array(curve_list[-min_length:], dtype=np.float64)

                    # 验证数组中没有None值
                    if not (np.isnan(time_array).any() or np.isnan(curve_array).any()):
                        curves_to_draw.append({
                            'curve_key': curve_key,
                            'time_data': time_array,
                            'curve_data': curve_array,
                            'color': color,
                            'linestyle': linestyle,
                            'index': i
                        })

        return {
            'x_start': x_start,
            'x_end': x_end,
            'curves': curves_to_draw,
            'timestamp': current_timestamp
        }

    def update_config(self, params_config=None, visible_curves=None, time_interval_minutes=None):
        """更新配置参数"""
        if params_config is not None:
            self.params_config = params_config
        if visible_curves is not None:
            self.visible_curves = visible_curves
        if time_interval_minutes is not None:
            self.time_interval_minutes = time_interval_minutes
            # 重新计算最大数据点数量
            max_points = self.time_interval_minutes * 600
            # 更新deque的最大长度
            self.time_data = deque(self.time_data, maxlen=max_points)
            for i in range(1, 7):
                curve_key = f'curve{i}'
                self.curve_data[curve_key] = deque(self.curve_data[curve_key], maxlen=max_points)

    def stop(self):
        """停止线程运行"""
        self.running = False
        self.finished.emit()


class RealTimeCurvePlotter(QWidget):
    def __init__(self, parent_widget, params_config, colors, y_limits=(-1, 1)):
        # 调用父类QWidget的初始化方法
        super().__init__()
        # 存储父容器窗口引用（用于界面布局）
        self.data_thread = None
        self.data_processor = None
        self.parent_widget = parent_widget
        # 参数配置字典（包含曲线和报警线的参数名称）
        self.params_config = params_config
        # Y轴显示范围（例如：-1到1）
        self.y_limits = y_limits
        # 添加时间间隔属性，默认为10分钟
        self.time_interval_minutes = 10
        # 创建数据管理器实例（用于数据库操作）
        self.data_manager = data_manager

        # 创建PyQtGraph绘图组件
        self.plot_widget = pg.PlotWidget()
        self._init_plot_style()
        # 设置界面布局
        self._setup_layout()

        # 添加曲线可见性控制字典，默认所有曲线可见
        self.visible_curves = {f'curve{i}': True for i in range(1, 7)}
        # 初始化曲线对象字典，存储所有曲线的PlotDataItem对象
        self.curve_objects = {f'curve{i}': None for i in range(1, 7)}
        # 定义30种对比鲜明的颜色（适配黑色背景）
        self.curve_colors = colors
        # 新增：尾段图层/状态缓存与刷新策略
        self.curve_tail_objects = {f'curve{i}': None for i in range(1, 7)}  # 尾段曲线（高频少点）
        self.curve_last_len = {f'curve{i}':  0 for i in range(1, 7)}         # 已绘制的累计点数
        self.tail_length_points = 100                                        # 尾段长度（可调）
        self.full_refresh_interval_ms = 1000                                  # 历史层全量刷新周期
        self._last_full_refresh_ts_ms = 0                                     # 上次历史层刷新时间戳(ms)
        # 新增：记录每条曲线最后一次绘制的数据的“最后时间戳”，用于在滑动窗口满后仍能识别新数据
        self.curve_last_x = {f'curve{i}': None for i in range(1, 7)}

        # 初始化数据处理线程
        self._init_data_processor()

    def _init_data_processor(self):
        """初始化数据处理线程"""
        # 创建线程对象
        self.data_thread = QThread()
        # 创建数据处理工作对象
        self.data_processor = CurveDataProcessor(
            self.params_config,
            self.visible_curves,
            self.time_interval_minutes,
            self.curve_colors
        )

        # 将工作对象移动到新线程
        self.data_processor.moveToThread(self.data_thread)

        # 信号连接
        self.data_processor.data_processed.connect(self._handle_processed_data)
        self.data_processor.finished.connect(self.data_thread.quit)
        self.data_processor.finished.connect(self.data_processor.deleteLater)
        self.data_thread.finished.connect(self.data_thread.deleteLater)

        # 启动线程
        self.data_thread.start()

    def _init_plot_style(self):
        """初始化PyQtGraph绘图样式"""
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
        """设置界面布局"""
        # 创建垂直布局容器（用于在父容器中排列组件）
        layout = QVBoxLayout(self.parent_widget)
        # 设置布局边距为0（不留空白）
        layout.setContentsMargins(0, 0, 0, 0)
        # 将绘图组件添加到布局中
        layout.addWidget(self.plot_widget)
        # 将布局设置到父容器
        self.parent_widget.setLayout(layout)

    def set_time_interval(self, minutes):
        """设置曲线显示的时间间隔（分钟）"""
        try:
            self.time_interval_minutes = max(1, int(minutes))
            # 更新数据处理器的配置
            if hasattr(self, 'data_processor'):
                self.data_processor.update_config(time_interval_minutes=self.time_interval_minutes)
        except (ValueError, TypeError):
            self.time_interval_minutes = 10

    def set_curve_visibility(self, curve_index, visible):
        """设置指定曲线的可见性
        Args:
            curve_index: 曲线索引（1-30）
            visible: 是否可见（True/False）
        """
        curve_key = f'curve{curve_index}'
        self.visible_curves[curve_key] = visible

        # 立即更新曲线可见性（同步历史层与尾段层）
        if self.curve_objects[curve_key] is not None:
            self.curve_objects[curve_key].setVisible(visible)
        if self.curve_tail_objects[curve_key] is not None:
            self.curve_tail_objects[curve_key].setVisible(visible)

        # 更新数据处理器的配置
        if hasattr(self, 'data_processor'):
            self.data_processor.update_config(visible_curves=self.visible_curves)

    def update_plot(self, data):
        """更新曲线数据（现在只负责将数据传递给子线程）"""
        if hasattr(self, 'data_processor') and data:
            # 将数据处理任务交给子线程
            self.data_processor.process_data(data)

    def _handle_processed_data(self, plot_data):
        """处理来自子线程的绘图数据（在主线程中执行绘图操作）
        采用“历史+尾段”增量绘制策略：
        - 历史层：低频全量刷新（带下采样）
        - 尾段层：高频只绘制最近tail_length_points个点
        """
        try:
            now_ms = int(time.time() * 1000)
            do_full_refresh = (now_ms - self._last_full_refresh_ts_ms) >= self.full_refresh_interval_ms

            # 隐藏不可见曲线（历史层 + 尾段层）
            for i in range(1, 7):
                curve_key = f'curve{i}'
                if not self.visible_curves.get(curve_key, True):
                    if self.curve_objects[curve_key] is not None:
                        self.curve_objects[curve_key].setVisible(False)
                    if self.curve_tail_objects[curve_key] is not None:
                        self.curve_tail_objects[curve_key].setVisible(False)

            # 绘制可见曲线
            for curve_info in plot_data['curves']:
                curve_key = curve_info['curve_key']

                # 验证数据有效性
                if len(curve_info['time_data']) == 0 or len(curve_info['curve_data']) == 0:
                    continue

                # 初始化曲线对象：历史层 + 尾段层
                if self.curve_objects[curve_key] is None:
                    # 历史层（细线，低频全量刷新）
                    pen_style = pg.QtCore.Qt.SolidLine if curve_info['linestyle'] == 'solid' else pg.QtCore.Qt.DashLine
                    pen_history = pg.mkPen(color=curve_info['color'], width=2, style=pen_style)
                    history_curve = self.plot_widget.plot(
                        np.array([], dtype=np.float64),
                        np.array([], dtype=np.float64),
                        pen=pen_history,
                        name=f"Curve{curve_info['index']}_hist"
                    )
                    # 尾段层（稍粗线，覆盖在历史层之上，频繁更新少量点）
                    pen_tail = pg.mkPen(color=curve_info['color'], width=2, style=pen_style)
                    tail_curve = self.plot_widget.plot(
                        np.array([], dtype=np.float64),
                        np.array([], dtype=np.float64),
                        pen=pen_tail,
                        name=f"Curve{curve_info['index']}_tail"
                    )
                    # 确保尾段层在历史层之上
                    history_curve.setZValue(0)
                    tail_curve.setZValue(1)

                    # 可选：尽量减少主线程处理量（存在版本差异，做异常保护）
                    try:
                        history_curve.setClipToView(True)  # 仅绘制可视区数据
                    except Exception:   # type: ignore[attr-defined]
                        pass
                    try:
                        history_curve.setDownsampling(auto=True)  # 自动下采样
                    except Exception:   # type: ignore[attr-defined]
                        pass

                    self.curve_objects[curve_key] = history_curve
                    self.curve_tail_objects[curve_key] = tail_curve
                    self.curve_last_len[curve_key] = 0
                    # 初始化最后时间戳
                    self.curve_last_x[curve_key] = None

                # 当前数据
                time_arr = curve_info['time_data']
                y_arr = curve_info['curve_data']
                n = len(time_arr)


                # 使用“最后时间戳”判断是否有新数据（即便滑窗满、长度不变也能识别）
                last_x_seen = self.curve_last_x.get(curve_key, None)
                current_last_x = time_arr[-1]
                if last_x_seen is not None and current_last_x <= last_x_seen:
                    # 无新增点，保持可见但不重绘
                    self.curve_objects[curve_key].setVisible(True)
                    self.curve_tail_objects[curve_key].setVisible(True)
                    continue

                # 1) 更新尾段层（高频少量点）
                tail_len = min(self.tail_length_points, n)
                tail_time = time_arr[-tail_len:]
                tail_y = y_arr[-tail_len:]
                self.curve_tail_objects[curve_key].setData(tail_time, tail_y)
                self.curve_tail_objects[curve_key].setVisible(True)

                # 2) 低频刷新历史层（全量但带动态下采样）
                if do_full_refresh:
                    # 动态下采样步长，限制历史层点数上限（比如 <= 2000）
                    max_hist_points = 2000
                    step = max(1, n // max_hist_points)
                    hist_time = time_arr[::step]
                    hist_y = y_arr[::step]
                    self.curve_objects[curve_key].setData(hist_time, hist_y)
                    self.curve_objects[curve_key].setVisible(True)

                # 记录“最后时间戳”（代替“累计点数”作为新数据判定依据）
                self.curve_last_x[curve_key] = current_last_x
                self.curve_last_len[curve_key] = n  # 可留作参考，但更新逻辑不再依赖它

            # 仅在历史层刷新时更新X轴范围，避免每帧都触发布局计算
            if do_full_refresh:
                self.plot_widget.getPlotItem().setXRange(plot_data['x_start'], plot_data['x_end'])
                self._last_full_refresh_ts_ms = now_ms

        except Exception as e:
            print(f"绘图处理异常: {str(e)}")

    def cleanup(self):
        """清理资源"""
        try:
            if hasattr(self, 'data_processor') and self.data_processor is not None:
                self.data_processor.stop()
                self.data_processor = None  # type: ignore[attr-defined]

        except Exception as e:
                print(f"data_processor清理异常: {str(e)}")
        try:
            if hasattr(self, 'data_thread') and self.data_thread is not None:
                self.data_thread.quit()
                self.data_thread.wait()
                self.data_thread.deleteLater()  # 添加线程清理
                self.data_thread = None # type: ignore[attr-defined]
        except Exception as e:
                print(f"data_thread清理异常: {str(e)}")

    def __del__(self):
        """析构函数，确保资源清理"""
        self.cleanup()