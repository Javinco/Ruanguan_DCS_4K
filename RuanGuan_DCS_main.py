# 导入系统模块
import sys
from datetime import datetime, timedelta
import socket

# 从PyQt5导入需要的组件
from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog, QTableWidgetItem
from PyQt5.QtCore import Qt, QTimer, QObject, pyqtSignal, QThread
# 导入自动生成的UI界面类
from Ui_MainWindow import Ui_MainWindow
from Ui_pop_parameter import Ui_Dialog_Pop_Parameter
from Ui_pop_parameter_factory1_2 import Ui_Dialog_Pop_Parameter_Factory1Device2
from Ui_pop_parameter_factory1_3 import Ui_Dialog_Pop_Parameter_Factory1Device3
from Ui_pop_parameter_factory1_4 import Ui_Dialog_Pop_Parameter_Factory1Device4
from Ui_pop_parameter_factory2_1 import Ui_Dialog_Pop_Parameter_Factory2Device1
from Ui_pop_parameter_factory2_2 import Ui_Dialog_Pop_Parameter_Factory2Device2
from Ui_pop_parameter_factory2_3 import Ui_Dialog_Pop_Parameter_Factory2Device3
from Ui_pop_historical_parameter import Ui_Dialog_Pop_Historical_Parameter
from Ui_pop_historical_parameter_factory1_2 import Ui_Dialog_Pop_Historical_Parameter_Factory1Device2
from Ui_pop_historical_parameter_factory1_3 import Ui_Dialog_Pop_Historical_Parameter_Factory1Device3
from Ui_pop_historical_parameter_factory1_4 import Ui_Dialog_Pop_Historical_Parameter_Factory1Device4
from Ui_pop_historical_parameter_factory2_1 import Ui_Dialog_Pop_Historical_Parameter_Factory2Device1
from Ui_pop_historical_parameter_factory2_2 import Ui_Dialog_Pop_Historical_Parameter_Factory2Device2
from Ui_pop_historical_parameter_factory2_3 import Ui_Dialog_Pop_Historical_Parameter_Factory2Device3
from Ui_pop_alarm import Ui_Dialog_alarm
from Data_Manager import data_manager, inserter,historical_data_manager
from Ruanguan_Curve import RealTimeCurvePlotter, RealTimeJcjCurvePlotter,RealTimeMainWindowCurve1
from Ruanguan_Historical import HistoricalCurvePlotter


# ---------------------------------参数弹窗类（继承QDialog和UI类）---------------------------------
class ParameterDialog(QDialog, Ui_Dialog_Pop_Parameter):
    def __init__(self):
        # 调用QDialog父类构造方法
        super().__init__()
        # 初始化UI界面
        self.param_mapping = None
        self.setWindowFlags(Qt.FramelessWindowHint)  # 设置无边框窗口样式（隐藏标题栏和边框）
        self.setAttribute(Qt.WA_TranslucentBackground)  # 启用透明背景属性（实现半透明/异形窗口效果）
        self.setupUi(self)  # 调用 UI 设计的 setupUi 方法

        self.dialog_historical = None  # 定义创建用于存储历史数据曲线弹窗的实例
        self.pushButton_historical_curve.clicked.connect(self.show_dialog_pop_historical_parameter)  # 连接按钮点击信号

        # 初始化位置记录变量
        self.dialog_original_pos = None  # 窗口原始位置
        self.drag_start_pos = None  # 鼠标拖动起始位置
        # 绑定鼠标事件到自身方法
        self.mousePressEvent = self.dialog_mouse_press  # 按下事件处理
        self.mouseMoveEvent = self.dialog_mouse_move  # 移动事件处理
        # 设置窗口居中属性
        self.center_dialog()  # 初始居中显示
        # 初始化时间功能
        self.timer = QTimer(self)  # 创建定时器对象
        self.timer.timeout.connect(self.update_time)  # type: ignore[attr-defined] # 连接定时信号
        self.timer.start(1000)  # 启动定时器（1秒间隔）
        self.update_time()  # 立即更新时间显示

        # 创建线程管理器字典
        self.threads = {}
        # 需要监控的表名列表
        self.tables_to_monitor = [
            "factory1_1_realtime_data_jcj",
            "factory1_1_realtime_data_fjj",
            "factory1_1_realtime_data_zdj",
            "factory1_1_set_data_jcj",
            "factory1_1_set_data_fjj",
            "factory1_1_set_data_zdj",
            "factory1_1_set_data_curve"
        ]

        # 启动数据更新线程
        self._start_data_update_thread(self.tables_to_monitor)
        # # 添加管径实时曲线（示例配置）
        # self.curve_plotter = RealTimeCurvePlotter(
        #     parent_widget=self.widget_pop_parameter_curve1,  # 对应UI中的曲线容器
        #     table_name="factory1_1_set_data_curve",
        #     params_config={
        #         'curve3': 'parameter3',
        #         'curve1': 'parameter1',
        #         'curve6': 'parameter6',
        #         'curve4': 'parameter4',
        #         'curve2': 'parameter2',
        #         'curve5': 'parameter5'
        #     },
        #     y_limits=(-1, 1)
        # )

        # # 添加挤出机参数实时曲线（示例配置）
        # self.curve_jcj = RealTimeJcjCurvePlotter(
        #     parent_widget=self.widget_pop_parameter_curve2,  # 对应UI中的曲线容器
        #     table_name="factory1_1_realtime_data_jcj",
        #     params_config={
        #         'curve1': 'parameter3',
        #         'curve2': 'parameter4',
        #         'curve3': 'parameter5',
        #         'curve4': 'parameter6',
        #         'curve5': 'parameter9',
        #         'curve6': 'parameter10'
        #     },
        #     y_limits=(0, 200)
        # )


    # ------------------------- 数据更新线程启动方法 -------------------------
    # 添加新方法：启动数据更新线程
    def _start_data_update_thread(self, tables_to_monitor):
        """启动数据更新线程
        参数:
            tables_to_monitor: 需要监控的表名列表
        """
        # 创建线程对象
        thread = QThread()
        # 创建工作线程实例
        worker = DataUpdateWorker(tables_to_monitor)

        # 将工作对象移动到新线程
        worker.moveToThread(thread)

        # 信号连接
        thread.started.connect(worker.run)  # type: ignore[attr-defined]# 线程启动时执行run方法
        worker.finished.connect(thread.quit)  # type: ignore[attr-defined]# 工作完成时退出线程
        worker.finished.connect(worker.deleteLater)  # type: ignore[attr-defined]# 工作完成后销毁worker对象
        thread.finished.connect(thread.deleteLater) # type: ignore[attr-defined] # 线程退出后销毁线程对象

        # 连接数据更新信号到处理方法
        worker.data_updated.connect(self._handle_data_update)   # type: ignore[attr-defined]

        # 存储线程引用
        self.threads['data_update1'] = (thread, worker)

        # 启动线程
        thread.start()

    # 添加新方法：处理数据更新
    def _handle_data_update(self, table_name, data):
        """处理从子线程接收到的数据更新
        参数:
            table_name: 表名
            data: 数据字典
        """
        # 创建策略映射字典（与原来相同）
        update_strategies = {
            "factory1_1_realtime_data_jcj": self._update_jcj_realtime,
            "factory1_1_realtime_data_fjj": self._update_fjj_realtime,
            "factory1_1_realtime_data_zdj": self._update_zdj_realtime,
            "factory1_1_set_data_jcj": self._update_jcj_set,
            "factory1_1_set_data_fjj": self._update_fjj_set,
            "factory1_1_set_data_zdj": self._update_zdj_set,
            "factory1_1_set_data_curve": self._update_curve_set
        }

        # 获取并执行对应的更新策略
        if strategy := update_strategies.get(table_name):
            if isinstance(strategy, list):  # 处理多个方法的情况
                for method in strategy:
                    method(data)    # type: ignore[attr-defined]
            else:
                strategy(data)  # type: ignore[attr-defined]
    # 分解原有的大更新方法为多个私有方法
    def _update_jcj_realtime(self, data):
        """更新挤出机实时数据"""
        self.label_10.setText(str(data.get('parameter1', '')))
        self.label_14.setText(str(data.get('parameter2', '')))
        self.label_18.setText(str(data.get('parameter3', '')))
        self.label_22.setText(str(data.get('parameter4', '')))
        self.label_26.setText(str(data.get('parameter5', '')))
        self.label_30.setText(str(data.get('parameter6', '')))
        self.label_34.setText(str(data.get('parameter7', '')))
        self.label_38.setText(str(data.get('parameter8', '')))
        self.label_42.setText(str(data.get('parameter9', '')))
        self.label_46.setText(str(data.get('parameter10', '')))
        self.label_50.setText(str(data.get('parameter11', '')))
        self.label_116.setText(str(data.get('parameter3', '')))
        self.label_117.setText(str(data.get('parameter4', '')))
        self.label_118.setText(str(data.get('parameter5', '')))
        self.label_119.setText(str(data.get('parameter6', '')))
        self.label_104.setText(str(data.get('parameter9', '')))
        self.label_105.setText(str(data.get('parameter10', '')))    # 使用get方法提供默认值
    def _update_fjj_realtime(self, data):
        """更新挤出机实时数据"""
        self.label_53.setText(str(data.get('parameter12', '')))
        self.label_57.setText(str(data.get('parameter13', '')))
        self.label_61.setText(str(data.get('parameter14', '')))
        self.label_65.setText(str(data.get('parameter15', '')))     # 使用get方法提供默认值
    def _update_zdj_realtime(self, data):
        """更新挤出机实时数据"""
        self.label_73.setText(str(data.get('parameter16', '')))
        self.label_77.setText(str(data.get('parameter17', '')))
        self.label_81.setText(str(data.get('parameter18', '')))
        self.label_85.setText(str(data.get('parameter19', '')))
        self.label_89.setText(str(data.get('parameter20', '')))
        self.label_93.setText(str(data.get('parameter21', '')))       # 使用get方法提供默认值
    def _update_jcj_set(self, data):
        """更新挤出机实时数据"""
        self.lineEdit_4.setText(str(data.get('parameter1', '')))
        self.lineEdit_5.setText(str(data.get('parameter2', '')))
        self.lineEdit_6.setText(str(data.get('parameter3', '')))
        self.lineEdit_7.setText(str(data.get('parameter4', '')))
        self.lineEdit_8.setText(str(data.get('parameter5', '')))
        self.lineEdit_10.setText(str(data.get('parameter6', '')))   # 使用get方法提供默认值
    def _update_fjj_set(self, data):
        """更新挤出机实时数据"""
        self.lineEdit_13.setText(str(data.get('parameter1', '')))
        self.lineEdit_14.setText(str(data.get('parameter2', '')))
        self.lineEdit_16.setText(str(data.get('parameter3', '')))   # 使用get方法提供默认值
    def _update_zdj_set(self, data):
        """更新挤出机实时数据"""
        self.lineEdit_17.setText(str(data.get('parameter1', '')))
        self.lineEdit_18.setText(str(data.get('parameter2', '')))
        self.lineEdit_19.setText(str(data.get('parameter3', '')))
        self.lineEdit_20.setText(str(data.get('parameter4', '')))   # 使用get方法提供默认值
    def _update_curve_set(self, data):
        """更新挤出机实时数据"""
        self.lineEdit_23.setText(str(data.get('parameter1', '')))
        self.lineEdit_48.setText(str(data.get('parameter2', '')))
        self.label_114.setText(str(data.get('parameter3', '')))
        self.label_115.setText(str(data.get('parameter4', '')))
        self.lineEdit_51.setText(str(data.get('parameter5', '')))
        self.lineEdit_52.setText(str(data.get('parameter6', '')))   # 使用get方法提供默认值
    def show_dialog_pop_historical_parameter(self):
        """显示历史参数弹窗的方法"""
        self.hide()  # 隐藏当前窗口
        # 检查历史参数弹窗是否已存在
        if self.dialog_historical:
            # 如果弹窗已最小化或隐藏，则恢复显示
            if self.dialog_historical.isMinimized():
                self.dialog_historical.showNormal()  # 从最小化状态恢复
            elif not self.dialog_historical.isVisible():
                self.dialog_historical.show()  # 如果不可见则显示
            # 如果已经可见，则将其置于前台
            self.dialog_historical.activateWindow()  # 激活窗口（置于前台）
            self.dialog_historical.raise_()  # 提升窗口层级

    def center_dialog(self):
        """将弹窗居中显示的方法"""
        # 获取主屏幕尺寸
        screen = QApplication.primaryScreen().geometry()
        # 计算居中坐标（屏幕宽度-窗口宽度）/2
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        # 移动窗口到计算位置
        self.move(x, y)

    def dialog_mouse_press(self, event):
        """处理鼠标按下事件（用于窗口拖动）"""
        # 判断点击位置是否在标题栏区域内
        point_in_title = self.widget_title.rect().contains(event.pos())
        # 当左键点击且位置在标题栏时
        if event.button() == Qt.LeftButton and point_in_title:
            # 记录全局鼠标位置（屏幕坐标系）
            self.drag_start_pos = event.globalPos()
            # 保存窗口当前位置
            self.dialog_original_pos = self.pos()
            # 接受事件，阻止事件传递
            event.accept()
        else:
            # 忽略非标题栏区域的点击
            event.ignore()

    def dialog_mouse_move(self, event):
        """处理鼠标移动事件（实现窗口拖动）"""
        # 当满足三个条件时处理拖动：
        # 1. 左键保持按下状态
        # 2. 存在初始拖动位置记录
        # 3. 鼠标在标题栏区域
        if (event.buttons() & Qt.LeftButton and
                hasattr(self, 'drag_start_pos') and
                self.widget_title.rect().contains(event.pos())):

            # 计算位置偏移量（当前鼠标位置 - 起始位置）
            delta = event.globalPos() - self.drag_start_pos
            # 移动窗口到新位置（原始位置 + 偏移量）
            self.move(self.dialog_original_pos + delta)
            # 接受事件，确保操作流畅
            event.accept()
        else:
            # 忽略无效拖动操作
            event.ignore()

    # 参数弹窗类新增关闭事件处理
    # 重写窗口关闭事件处理方法（当窗口被关闭时自动触发）
    # 重写关闭事件，确保线程正确停止
    def closeEvent(self, event):
        """处理关闭事件：关闭关联的历史参数弹窗和停止所有线程"""
        # 停止数据更新线程
        if hasattr(self, 'threads'):
            for key, (thread, worker) in self.threads.items():
                if hasattr(worker, 'stop'):
                    worker.stop()

        # 检查是否存在历史参数弹窗实例
        if self.dialog_historical:
            self.dialog_historical.close()

        super().closeEvent(event)  # 调用父类的关闭事件处理

    @staticmethod  # 静态方法，不依赖实例对象
    def get_localtime():
        """获取本地时间的静态方法"""
        from datetime import datetime , timedelta
        now = datetime.now()  # 获取当前时间对象
        start_time = now - timedelta(minutes=10)  # 计算起始时间（当前时间向前10分钟）
        # 返回格式化后的日期和时间字符串
        return start_time.strftime("%H:%M:%S"), now.strftime("%H:%M:%S")

    def update_time(self):
        """更新时间显示的方法"""
        time_start_str, time_end_str = self.get_localtime()  # 解包日期时间
        self.label_106.setText(time_start_str)  # 更新日期标签
        self.label_107.setText(time_end_str)  # 更新时间标签
        self.label_112.setText(time_start_str)  # 更新日期标签
        self.label_113.setText(time_end_str)  # 更新时间标签

class ParameterDialogFactory1Device2(QDialog, Ui_Dialog_Pop_Parameter_Factory1Device2):
    def __init__(self):
        # 调用QDialog父类构造方法
        super().__init__()
        # 初始化UI界面
        self.param_mapping = None
        self.setWindowFlags(Qt.FramelessWindowHint)  # 设置无边框窗口样式（隐藏标题栏和边框）
        self.setAttribute(Qt.WA_TranslucentBackground)  # 启用透明背景属性（实现半透明/异形窗口效果）
        self.setupUi(self)  # 调用 UI 设计的 setupUi 方法

        self.dialog_historical = None  # 定义创建用于存储历史数据曲线弹窗的实例
        self.pushButton_historical_curve.clicked.connect(self.show_dialog_pop_historical_parameter)  # 连接按钮点击信号

        # 初始化位置记录变量
        self.dialog_original_pos = None  # 窗口原始位置
        self.drag_start_pos = None  # 鼠标拖动起始位置
        # 绑定鼠标事件到自身方法
        self.mousePressEvent = self.dialog_mouse_press  # 按下事件处理
        self.mouseMoveEvent = self.dialog_mouse_move  # 移动事件处理
        # 设置窗口居中属性
        self.center_dialog()  # 初始居中显示
        # 初始化时间功能
        self.timer = QTimer(self)  # 创建定时器对象
        self.timer.timeout.connect(self.update_time)  # type: ignore[attr-defined] # 连接定时信号
        self.timer.start(1000)  # 启动定时器（1秒间隔）
        self.update_time()  # 立即更新时间显示
        # 创建线程管理器字典
        self.threads = {}
        # 需要监控的表名列表
        self.tables_to_monitor = [
            "factory1_2_realtime_data_jcj",
            "factory1_2_realtime_data_fjj",
            "factory1_2_realtime_data_zdj",
            "factory1_2_set_data_jcj",
            "factory1_2_set_data_fjj",
            "factory1_2_set_data_zdj",
            "factory1_2_set_data_curve"
        ]

        # 启动数据更新线程
        self._start_data_update_thread(self.tables_to_monitor)
        # # 添加管径实时曲线（示例配置）
        # self.curve_plotter = RealTimeCurvePlotter(
        #     parent_widget=self.widget_pop_parameter_curve1,  # 对应UI中的曲线容器
        #     table_name="factory1_2_set_data_curve",
        #     params_config={
        #         'curve3': 'parameter3',
        #         'curve1': 'parameter1',
        #         'curve6': 'parameter6',
        #         'curve4': 'parameter4',
        #         'curve2': 'parameter2',
        #         'curve5': 'parameter5'
        #     },
        #     y_limits=(-1, 1)
        # )
        #
        # # 添加挤出机参数实时曲线（示例配置）
        # self.curve_jcj = RealTimeJcjCurvePlotter(
        #     parent_widget=self.widget_pop_parameter_curve2,  # 对应UI中的曲线容器
        #     table_name="factory1_2_realtime_data_jcj",
        #     params_config={
        #         'curve1': 'parameter3',
        #         'curve2': 'parameter4',
        #         'curve3': 'parameter5',
        #         'curve4': 'parameter6',
        #         'curve5': 'parameter9',
        #         'curve6': 'parameter10'
        #     },
        #     y_limits=(0, 200)
        # )


    # ------------------------- 数据更新线程启动方法 -------------------------
    # 添加新方法：启动数据更新线程
    def _start_data_update_thread(self, tables_to_monitor):
        """启动数据更新线程
        参数:
            tables_to_monitor: 需要监控的表名列表
        """
        # 创建线程对象
        thread = QThread()
        # 创建工作线程实例
        worker = DataUpdateWorker(tables_to_monitor)

        # 将工作对象移动到新线程
        worker.moveToThread(thread)

        # 信号连接
        thread.started.connect(worker.run)  # type: ignore[attr-defined]# 线程启动时执行run方法
        worker.finished.connect(thread.quit)  # type: ignore[attr-defined]# 工作完成时退出线程
        worker.finished.connect(worker.deleteLater)  # type: ignore[attr-defined]# 工作完成后销毁worker对象
        thread.finished.connect(thread.deleteLater)  # type: ignore[attr-defined]# 线程退出后销毁线程对象

        # 连接数据更新信号到处理方法
        worker.data_updated.connect(self._handle_data_update)   # type: ignore[attr-defined]

        # 存储线程引用
        self.threads['data_update2'] = (thread, worker)

        # 启动线程
        thread.start()

    # 添加新方法：处理数据更新
    def _handle_data_update(self, table_name, data):
        """处理从子线程接收到的数据更新
        参数:
            table_name: 表名
            data: 数据字典
        """
        # 创建策略映射字典（与原来相同）
        update_strategies = {
            "factory1_2_realtime_data_jcj": self._update_jcj_realtime,
            "factory1_2_realtime_data_fjj": self._update_fjj_realtime,
            "factory1_2_realtime_data_zdj": self._update_zdj_realtime,
            "factory1_2_set_data_jcj": self._update_jcj_set,
            "factory1_2_set_data_fjj": self._update_fjj_set,
            "factory1_2_set_data_zdj": self._update_zdj_set,
            "factory1_2_set_data_curve": self._update_curve_set
        }

        # 获取并执行对应的更新策略
        if strategy := update_strategies.get(table_name):
            if isinstance(strategy, list):  # 处理多个方法的情况
                for method in strategy:
                    method(data)    # type: ignore[attr-defined]
            else:
                strategy(data)  # type: ignore[attr-defined]
    # 分解原有的大更新方法为多个私有方法
    def _update_jcj_realtime(self, data):
        """更新挤出机实时数据"""
        self.label_10.setText(str(data.get('parameter1', '')))
        self.label_14.setText(str(data.get('parameter2', '')))
        self.label_18.setText(str(data.get('parameter3', '')))
        self.label_22.setText(str(data.get('parameter4', '')))
        self.label_26.setText(str(data.get('parameter5', '')))
        self.label_30.setText(str(data.get('parameter6', '')))
        self.label_34.setText(str(data.get('parameter7', '')))
        self.label_38.setText(str(data.get('parameter8', '')))
        self.label_42.setText(str(data.get('parameter9', '')))
        self.label_46.setText(str(data.get('parameter10', '')))
        self.label_50.setText(str(data.get('parameter11', '')))
        self.label_116.setText(str(data.get('parameter3', '')))
        self.label_117.setText(str(data.get('parameter4', '')))
        self.label_118.setText(str(data.get('parameter5', '')))
        self.label_119.setText(str(data.get('parameter6', '')))
        self.label_104.setText(str(data.get('parameter9', '')))
        self.label_105.setText(str(data.get('parameter10', '')))    # 使用get方法提供默认值
    def _update_fjj_realtime(self, data):
        """更新挤出机实时数据"""
        self.label_53.setText(str(data.get('parameter12', '')))
        self.label_57.setText(str(data.get('parameter13', '')))
        self.label_61.setText(str(data.get('parameter14', '')))
        self.label_65.setText(str(data.get('parameter15', '')))     # 使用get方法提供默认值
    def _update_zdj_realtime(self, data):
        """更新挤出机实时数据"""
        self.label_73.setText(str(data.get('parameter16', '')))
        self.label_77.setText(str(data.get('parameter17', '')))
        self.label_81.setText(str(data.get('parameter18', '')))
        self.label_85.setText(str(data.get('parameter19', '')))
        self.label_89.setText(str(data.get('parameter20', '')))
        self.label_93.setText(str(data.get('parameter21', '')))     # 使用get方法提供默认值
    def _update_jcj_set(self, data):
        """更新挤出机实时数据"""
        self.lineEdit_4.setText(str(data.get('parameter1', '')))
        self.lineEdit_5.setText(str(data.get('parameter2', '')))
        self.lineEdit_6.setText(str(data.get('parameter3', '')))
        self.lineEdit_7.setText(str(data.get('parameter4', '')))
        self.lineEdit_8.setText(str(data.get('parameter5', '')))
        self.lineEdit_10.setText(str(data.get('parameter6', '')))   # 使用get方法提供默认值
    def _update_fjj_set(self, data):
        """更新挤出机实时数据"""
        self.lineEdit_13.setText(str(data.get('parameter1', '')))
        self.lineEdit_14.setText(str(data.get('parameter2', '')))
        self.lineEdit_16.setText(str(data.get('parameter3', '')))   # 使用get方法提供默认值
    def _update_zdj_set(self, data):
        """更新挤出机实时数据"""
        self.lineEdit_17.setText(str(data.get('parameter1', '')))
        self.lineEdit_18.setText(str(data.get('parameter2', '')))
        self.lineEdit_19.setText(str(data.get('parameter3', '')))
        self.lineEdit_20.setText(str(data.get('parameter4', '')))   # 使用get方法提供默认值
    def _update_curve_set(self, data):
        """更新挤出机实时数据"""
        self.lineEdit_23.setText(str(data.get('parameter1', '')))
        self.lineEdit_48.setText(str(data.get('parameter2', '')))
        self.label_114.setText(str(data.get('parameter3', '')))
        self.label_115.setText(str(data.get('parameter4', '')))
        self.lineEdit_51.setText(str(data.get('parameter5', '')))
        self.lineEdit_52.setText(str(data.get('parameter6', '')))   # 使用get方法提供默认值
    def show_dialog_pop_historical_parameter(self):
        """显示历史参数弹窗的方法"""
        self.hide()  # 隐藏当前窗口
        # 检查历史参数弹窗是否已存在
        if self.dialog_historical:
            # 如果弹窗已最小化或隐藏，则恢复显示
            if self.dialog_historical.isMinimized():
                self.dialog_historical.showNormal()  # 从最小化状态恢复
            elif not self.dialog_historical.isVisible():
                self.dialog_historical.show()  # 如果不可见则显示
            # 如果已经可见，则将其置于前台
            self.dialog_historical.activateWindow()  # 激活窗口（置于前台）
            self.dialog_historical.raise_()  # 提升窗口层级

    def center_dialog(self):
        """将弹窗居中显示的方法"""
        # 获取主屏幕尺寸
        screen = QApplication.primaryScreen().geometry()
        # 计算居中坐标（屏幕宽度-窗口宽度）/2
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        # 移动窗口到计算位置
        self.move(x, y)

    def dialog_mouse_press(self, event):
        """处理鼠标按下事件（用于窗口拖动）"""
        # 判断点击位置是否在标题栏区域内
        point_in_title = self.widget_title.rect().contains(event.pos())
        # 当左键点击且位置在标题栏时
        if event.button() == Qt.LeftButton and point_in_title:
            # 记录全局鼠标位置（屏幕坐标系）
            self.drag_start_pos = event.globalPos()
            # 保存窗口当前位置
            self.dialog_original_pos = self.pos()
            # 接受事件，阻止事件传递
            event.accept()
        else:
            # 忽略非标题栏区域的点击
            event.ignore()

    def dialog_mouse_move(self, event):
        """处理鼠标移动事件（实现窗口拖动）"""
        # 当满足三个条件时处理拖动：
        # 1. 左键保持按下状态
        # 2. 存在初始拖动位置记录
        # 3. 鼠标在标题栏区域
        if (event.buttons() & Qt.LeftButton and
                hasattr(self, 'drag_start_pos') and
                self.widget_title.rect().contains(event.pos())):

            # 计算位置偏移量（当前鼠标位置 - 起始位置）
            delta = event.globalPos() - self.drag_start_pos
            # 移动窗口到新位置（原始位置 + 偏移量）
            self.move(self.dialog_original_pos + delta)
            # 接受事件，确保操作流畅
            event.accept()
        else:
            # 忽略无效拖动操作
            event.ignore()

    # 参数弹窗类新增关闭事件处理
    # 重写窗口关闭事件处理方法（当窗口被关闭时自动触发）
    def closeEvent(self, event):
        """处理关闭事件：关闭关联的历史参数弹窗和停止所有线程"""
        # 停止数据更新线程
        if hasattr(self, 'threads'):
            for key, (thread, worker) in self.threads.items():
                if hasattr(worker, 'stop'):
                    worker.stop()

        # 检查是否存在历史参数弹窗实例
        if self.dialog_historical:
            self.dialog_historical.close()

        super().closeEvent(event)  # 调用父类的关闭事件处理

    @staticmethod  # 静态方法，不依赖实例对象
    def get_localtime():
        """获取本地时间的静态方法"""
        from datetime import datetime , timedelta
        now = datetime.now()  # 获取当前时间对象
        start_time = now - timedelta(minutes=10)  # 计算起始时间（当前时间向前10分钟）
        # 返回格式化后的日期和时间字符串
        return start_time.strftime("%H:%M:%S"), now.strftime("%H:%M:%S")

    def update_time(self):
        """更新时间显示的方法"""
        time_start_str, time_end_str = self.get_localtime()  # 解包日期时间
        self.label_106.setText(time_start_str)  # 更新日期标签
        self.label_107.setText(time_end_str)  # 更新时间标签
        self.label_112.setText(time_start_str)  # 更新日期标签
        self.label_113.setText(time_end_str)  # 更新时间标签

class ParameterDialogFactory1Device3(QDialog, Ui_Dialog_Pop_Parameter_Factory1Device3):
    def __init__(self):
        # 调用QDialog父类构造方法
        super().__init__()
        # 初始化UI界面
        self.param_mapping = None
        self.setWindowFlags(Qt.FramelessWindowHint)  # 设置无边框窗口样式（隐藏标题栏和边框）
        self.setAttribute(Qt.WA_TranslucentBackground)  # 启用透明背景属性（实现半透明/异形窗口效果）
        self.setupUi(self)  # 调用 UI 设计的 setupUi 方法

        self.dialog_historical = None  # 定义创建用于存储历史数据曲线弹窗的实例
        self.pushButton_historical_curve.clicked.connect(self.show_dialog_pop_historical_parameter)  # 连接按钮点击信号

        # 初始化位置记录变量
        self.dialog_original_pos = None  # 窗口原始位置
        self.drag_start_pos = None  # 鼠标拖动起始位置
        # 绑定鼠标事件到自身方法
        self.mousePressEvent = self.dialog_mouse_press  # 按下事件处理
        self.mouseMoveEvent = self.dialog_mouse_move  # 移动事件处理
        # 设置窗口居中属性
        self.center_dialog()  # 初始居中显示
        # 初始化时间功能
        self.timer = QTimer(self)  # 创建定时器对象
        self.timer.timeout.connect(self.update_time)  # type: ignore[attr-defined] # 连接定时信号
        self.timer.start(1000)  # 启动定时器（1秒间隔）
        self.update_time()  # 立即更新时间显示
        # 创建线程管理器字典
        self.threads = {}
        # 需要监控的表名列表
        self.tables_to_monitor = [
            "factory1_3_realtime_data_jcj",
            "factory1_3_realtime_data_fjj",
            "factory1_3_realtime_data_zdj",
            "factory1_3_set_data_jcj",
            "factory1_3_set_data_fjj",
            "factory1_3_set_data_zdj",
            "factory1_3_set_data_curve"
        ]

        # 启动数据更新线程
        self._start_data_update_thread(self.tables_to_monitor)
        # # 添加管径实时曲线（示例配置）
        # self.curve_plotter = RealTimeCurvePlotter(
        #     parent_widget=self.widget_pop_parameter_curve1,  # 对应UI中的曲线容器
        #     table_name="factory1_3_set_data_curve",
        #     params_config={
        #         'curve3': 'parameter3',
        #         'curve1': 'parameter1',
        #         'curve6': 'parameter6',
        #         'curve4': 'parameter4',
        #         'curve2': 'parameter2',
        #         'curve5': 'parameter5'
        #     },
        #     y_limits=(-1, 1)
        # )
        #
        # # 添加挤出机参数实时曲线（示例配置）
        # self.curve_jcj = RealTimeJcjCurvePlotter(
        #     parent_widget=self.widget_pop_parameter_curve2,  # 对应UI中的曲线容器
        #     table_name="factory1_3_realtime_data_jcj",
        #     params_config={
        #         'curve1': 'parameter3',
        #         'curve2': 'parameter4',
        #         'curve3': 'parameter5',
        #         'curve4': 'parameter6',
        #         'curve5': 'parameter9',
        #         'curve6': 'parameter10'
        #     },
        #     y_limits=(0, 200)
        # )


    # ------------------------- 数据更新线程启动方法 -------------------------
    # 添加新方法：启动数据更新线程
    def _start_data_update_thread(self, tables_to_monitor):
        """启动数据更新线程
        参数:
            tables_to_monitor: 需要监控的表名列表
        """
        # 创建线程对象
        thread = QThread()
        # 创建工作线程实例
        worker = DataUpdateWorker(tables_to_monitor)

        # 将工作对象移动到新线程
        worker.moveToThread(thread)

        # 信号连接
        thread.started.connect(worker.run) # type: ignore[attr-defined] # 线程启动时执行run方法
        worker.finished.connect(thread.quit)    # type: ignore[attr-defined]    # 工作完成时退出线程
        worker.finished.connect(worker.deleteLater)  # type: ignore[attr-defined]   # 工作完成后销毁worker对象
        thread.finished.connect(thread.deleteLater)     # type: ignore[attr-defined]    # 线程退出后销毁线程对象

        # 连接数据更新信号到处理方法
        worker.data_updated.connect(self._handle_data_update)   # type: ignore[attr-defined]

        # 存储线程引用
        self.threads['data_update3'] = (thread, worker)

        # 启动线程
        thread.start()

    # 添加新方法：处理数据更新
    def _handle_data_update(self, table_name, data):
        """处理从子线程接收到的数据更新
        参数:
            table_name: 表名
            data: 数据字典
        """
        # 创建策略映射字典（与原来相同）
        update_strategies = {
            "factory1_3_realtime_data_jcj": self._update_jcj_realtime,
            "factory1_3_realtime_data_fjj": self._update_fjj_realtime,
            "factory1_3_realtime_data_zdj": self._update_zdj_realtime,
            "factory1_3_set_data_jcj": self._update_jcj_set,
            "factory1_3_set_data_fjj": self._update_fjj_set,
            "factory1_3_set_data_zdj": self._update_zdj_set,
            "factory1_3_set_data_curve": self._update_curve_set
        }

        # 获取并执行对应的更新策略
        if strategy := update_strategies.get(table_name):
            if isinstance(strategy, list):  # 处理多个方法的情况
                for method in strategy:
                    method(data)    # type: ignore[attr-defined]
            else:
                strategy(data)  # type: ignore[attr-defined]
    # 分解原有的大更新方法为多个私有方法
    def _update_jcj_realtime(self, data):
        """更新挤出机实时数据"""
        self.label_10.setText(str(data.get('parameter1', '')))
        self.label_14.setText(str(data.get('parameter2', '')))
        self.label_18.setText(str(data.get('parameter3', '')))
        self.label_22.setText(str(data.get('parameter4', '')))
        self.label_26.setText(str(data.get('parameter5', '')))
        self.label_30.setText(str(data.get('parameter6', '')))
        self.label_34.setText(str(data.get('parameter7', '')))
        self.label_38.setText(str(data.get('parameter8', '')))
        self.label_42.setText(str(data.get('parameter9', '')))
        self.label_46.setText(str(data.get('parameter10', '')))
        self.label_50.setText(str(data.get('parameter11', '')))
        self.label_116.setText(str(data.get('parameter3', '')))
        self.label_117.setText(str(data.get('parameter4', '')))
        self.label_118.setText(str(data.get('parameter5', '')))
        self.label_119.setText(str(data.get('parameter6', '')))
        self.label_104.setText(str(data.get('parameter9', '')))
        self.label_105.setText(str(data.get('parameter10', '')))   # 使用get方法提供默认值
    def _update_fjj_realtime(self, data):
        """更新挤出机实时数据"""
        self.label_53.setText(str(data.get('parameter12', '')))
        self.label_57.setText(str(data.get('parameter13', '')))
        self.label_61.setText(str(data.get('parameter14', '')))
        self.label_65.setText(str(data.get('parameter15', '')))  # 使用get方法提供默认值
    def _update_zdj_realtime(self, data):
        """更新挤出机实时数据"""
        self.label_73.setText(str(data.get('parameter16', '')))
        self.label_77.setText(str(data.get('parameter17', '')))
        self.label_81.setText(str(data.get('parameter18', '')))
        self.label_85.setText(str(data.get('parameter19', '')))
        self.label_89.setText(str(data.get('parameter20', '')))
        self.label_93.setText(str(data.get('parameter21', '')))  # 使用get方法提供默认值
    def _update_jcj_set(self, data):
        """更新挤出机实时数据"""
        self.lineEdit_4.setText(str(data.get('parameter1', '')))
        self.lineEdit_5.setText(str(data.get('parameter2', '')))
        self.lineEdit_6.setText(str(data.get('parameter3', '')))
        self.lineEdit_7.setText(str(data.get('parameter4', '')))
        self.lineEdit_8.setText(str(data.get('parameter5', '')))
        self.lineEdit_10.setText(str(data.get('parameter6', '')))  # 使用get方法提供默认值
    def _update_fjj_set(self, data):
        """更新挤出机实时数据"""
        self.lineEdit_13.setText(str(data.get('parameter1', '')))
        self.lineEdit_14.setText(str(data.get('parameter2', '')))
        self.lineEdit_16.setText(str(data.get('parameter3', '')))     # 使用get方法提供默认值
    def _update_zdj_set(self, data):
        """更新挤出机实时数据"""
        self.lineEdit_17.setText(str(data.get('parameter1', '')))
        self.lineEdit_18.setText(str(data.get('parameter2', '')))
        self.lineEdit_19.setText(str(data.get('parameter3', '')))
        self.lineEdit_20.setText(str(data.get('parameter4', '')))  # 使用get方法提供默认值
    def _update_curve_set(self, data):
        """更新挤出机实时数据"""
        self.lineEdit_23.setText(str(data.get('parameter1', '')))
        self.lineEdit_48.setText(str(data.get('parameter2', '')))
        self.label_114.setText(str(data.get('parameter3', '')))
        self.label_115.setText(str(data.get('parameter4', '')))
        self.lineEdit_51.setText(str(data.get('parameter5', '')))
        self.lineEdit_52.setText(str(data.get('parameter6', '')))  # 使用get方法提供默认值
    def show_dialog_pop_historical_parameter(self):
        """显示历史参数弹窗的方法"""
        self.hide()  # 隐藏当前窗口
        # 检查历史参数弹窗是否已存在
        if self.dialog_historical:
            # 如果弹窗已最小化或隐藏，则恢复显示
            if self.dialog_historical.isMinimized():
                self.dialog_historical.showNormal()  # 从最小化状态恢复
            elif not self.dialog_historical.isVisible():
                self.dialog_historical.show()  # 如果不可见则显示
            # 如果已经可见，则将其置于前台
            self.dialog_historical.activateWindow()  # 激活窗口（置于前台）
            self.dialog_historical.raise_()  # 提升窗口层级

    def center_dialog(self):
        """将弹窗居中显示的方法"""
        # 获取主屏幕尺寸
        screen = QApplication.primaryScreen().geometry()
        # 计算居中坐标（屏幕宽度-窗口宽度）/2
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        # 移动窗口到计算位置
        self.move(x, y)

    def dialog_mouse_press(self, event):
        """处理鼠标按下事件（用于窗口拖动）"""
        # 判断点击位置是否在标题栏区域内
        point_in_title = self.widget_title.rect().contains(event.pos())
        # 当左键点击且位置在标题栏时
        if event.button() == Qt.LeftButton and point_in_title:
            # 记录全局鼠标位置（屏幕坐标系）
            self.drag_start_pos = event.globalPos()
            # 保存窗口当前位置
            self.dialog_original_pos = self.pos()
            # 接受事件，阻止事件传递
            event.accept()
        else:
            # 忽略非标题栏区域的点击
            event.ignore()

    def dialog_mouse_move(self, event):
        """处理鼠标移动事件（实现窗口拖动）"""
        # 当满足三个条件时处理拖动：
        # 1. 左键保持按下状态
        # 2. 存在初始拖动位置记录
        # 3. 鼠标在标题栏区域
        if (event.buttons() & Qt.LeftButton and
                hasattr(self, 'drag_start_pos') and
                self.widget_title.rect().contains(event.pos())):

            # 计算位置偏移量（当前鼠标位置 - 起始位置）
            delta = event.globalPos() - self.drag_start_pos
            # 移动窗口到新位置（原始位置 + 偏移量）
            self.move(self.dialog_original_pos + delta)
            # 接受事件，确保操作流畅
            event.accept()
        else:
            # 忽略无效拖动操作
            event.ignore()

    # 参数弹窗类新增关闭事件处理
    # 重写窗口关闭事件处理方法（当窗口被关闭时自动触发）
    def closeEvent(self, event):
        """处理关闭事件：关闭关联的历史参数弹窗和停止所有线程"""
        # 停止数据更新线程
        if hasattr(self, 'threads'):
            for key, (thread, worker) in self.threads.items():
                if hasattr(worker, 'stop'):
                    worker.stop()

        # 检查是否存在历史参数弹窗实例
        if self.dialog_historical:
            self.dialog_historical.close()

        super().closeEvent(event)  # 调用父类的关闭事件处理

    @staticmethod  # 静态方法，不依赖实例对象
    def get_localtime():
        """获取本地时间的静态方法"""
        from datetime import datetime , timedelta
        now = datetime.now()  # 获取当前时间对象
        start_time = now - timedelta(minutes=10)  # 计算起始时间（当前时间向前10分钟）
        # 返回格式化后的日期和时间字符串
        return start_time.strftime("%H:%M:%S"), now.strftime("%H:%M:%S")

    def update_time(self):
        """更新时间显示的方法"""
        time_start_str, time_end_str = self.get_localtime()  # 解包日期时间
        self.label_106.setText(time_start_str)  # 更新日期标签
        self.label_107.setText(time_end_str)  # 更新时间标签
        self.label_112.setText(time_start_str)  # 更新日期标签
        self.label_113.setText(time_end_str)  # 更新时间标签

class ParameterDialogFactory1Device4(QDialog, Ui_Dialog_Pop_Parameter_Factory1Device4):
    def __init__(self):
        # 调用QDialog父类构造方法
        super().__init__()
        # 初始化UI界面
        self.param_mapping = None
        self.setWindowFlags(Qt.FramelessWindowHint)  # 设置无边框窗口样式（隐藏标题栏和边框）
        self.setAttribute(Qt.WA_TranslucentBackground)  # 启用透明背景属性（实现半透明/异形窗口效果）
        self.setupUi(self)  # 调用 UI 设计的 setupUi 方法

        self.dialog_historical = None  # 定义创建用于存储历史数据曲线弹窗的实例
        self.pushButton_historical_curve.clicked.connect(self.show_dialog_pop_historical_parameter)  # 连接按钮点击信号

        # 初始化位置记录变量
        self.dialog_original_pos = None  # 窗口原始位置
        self.drag_start_pos = None  # 鼠标拖动起始位置
        # 绑定鼠标事件到自身方法
        self.mousePressEvent = self.dialog_mouse_press  # 按下事件处理
        self.mouseMoveEvent = self.dialog_mouse_move  # 移动事件处理
        # 设置窗口居中属性
        self.center_dialog()  # 初始居中显示
        # 初始化时间功能
        self.timer = QTimer(self)  # 创建定时器对象
        self.timer.timeout.connect(self.update_time)  # type: ignore[attr-defined] # 连接定时信号
        self.timer.start(1000)  # 启动定时器（1秒间隔）
        self.update_time()  # 立即更新时间显示
        # 创建线程管理器字典
        self.threads = {}
        # 需要监控的表名列表
        self.tables_to_monitor = [
            "factory1_4_realtime_data_jcj",
            "factory1_4_realtime_data_fjj",
            "factory1_4_realtime_data_zdj",
            "factory1_4_set_data_jcj",
            "factory1_4_set_data_fjj",
            "factory1_4_set_data_zdj",
            "factory1_4_set_data_curve"
        ]

        # 启动数据更新线程
        self._start_data_update_thread(self.tables_to_monitor)
        # # 添加管径实时曲线（示例配置）
        # self.curve_plotter = RealTimeCurvePlotter(
        #     parent_widget=self.widget_pop_parameter_curve1,  # 对应UI中的曲线容器
        #     table_name="factory1_4_set_data_curve",
        #     params_config={
        #         'curve3': 'parameter3',
        #         'curve1': 'parameter1',
        #         'curve6': 'parameter6',
        #         'curve4': 'parameter4',
        #         'curve2': 'parameter2',
        #         'curve5': 'parameter5'
        #     },
        #     y_limits=(-1, 1)
        # )
        #
        # # 添加挤出机参数实时曲线（示例配置）
        # self.curve_jcj = RealTimeJcjCurvePlotter(
        #     parent_widget=self.widget_pop_parameter_curve2,  # 对应UI中的曲线容器
        #     table_name="factory1_4_realtime_data_jcj",
        #     params_config={
        #         'curve1': 'parameter3',
        #         'curve2': 'parameter4',
        #         'curve3': 'parameter5',
        #         'curve4': 'parameter6',
        #         'curve5': 'parameter9',
        #         'curve6': 'parameter10'
        #     },
        #     y_limits=(0, 200)
        # )


    # ------------------------- 数据更新线程启动方法 -------------------------
    # 添加新方法：启动数据更新线程
    def _start_data_update_thread(self, tables_to_monitor):
        """启动数据更新线程
        参数:
            tables_to_monitor: 需要监控的表名列表
        """
        # 创建线程对象
        thread = QThread()
        # 创建工作线程实例
        worker = DataUpdateWorker(tables_to_monitor)

        # 将工作对象移动到新线程
        worker.moveToThread(thread)

        # 信号连接
        thread.started.connect(worker.run)  # type: ignore[attr-defined]# 线程启动时执行run方法
        worker.finished.connect(thread.quit)  # type: ignore[attr-defined]# 工作完成时退出线程
        worker.finished.connect(worker.deleteLater)  # type: ignore[attr-defined]# 工作完成后销毁worker对象
        thread.finished.connect(thread.deleteLater)  # type: ignore[attr-defined]# 线程退出后销毁线程对象

        # 连接数据更新信号到处理方法
        worker.data_updated.connect(self._handle_data_update)   # type: ignore[attr-defined]

        # 存储线程引用
        self.threads['data_update4'] = (thread, worker)

        # 启动线程
        thread.start()

    # 添加新方法：处理数据更新
    def _handle_data_update(self, table_name, data):
        """处理从子线程接收到的数据更新
        参数:
            table_name: 表名
            data: 数据字典
        """
        # 创建策略映射字典（与原来相同）
        update_strategies = {
            "factory1_4_realtime_data_jcj": self._update_jcj_realtime,
            "factory1_4_realtime_data_fjj": self._update_fjj_realtime,
            "factory1_4_realtime_data_zdj": self._update_zdj_realtime,
            "factory1_4_set_data_jcj": self._update_jcj_set,
            "factory1_4_set_data_fjj": self._update_fjj_set,
            "factory1_4_set_data_zdj": self._update_zdj_set,
            "factory1_4_set_data_curve": self._update_curve_set
        }

        # 获取并执行对应的更新策略
        if strategy := update_strategies.get(table_name):
            if isinstance(strategy, list):  # 处理多个方法的情况
                for method in strategy:
                    method(data)    # type: ignore[attr-defined]
            else:
                strategy(data)  # type: ignore[attr-defined]
    # 分解原有的大更新方法为多个私有方法
    def _update_jcj_realtime(self, data):
        """更新挤出机实时数据"""
        self.label_10.setText(str(data.get('parameter1', '')))
        self.label_14.setText(str(data.get('parameter2', '')))
        self.label_18.setText(str(data.get('parameter3', '')))
        self.label_22.setText(str(data.get('parameter4', '')))
        self.label_26.setText(str(data.get('parameter5', '')))
        self.label_30.setText(str(data.get('parameter6', '')))
        self.label_34.setText(str(data.get('parameter7', '')))
        self.label_38.setText(str(data.get('parameter8', '')))
        self.label_42.setText(str(data.get('parameter9', '')))
        self.label_46.setText(str(data.get('parameter10', '')))
        self.label_50.setText(str(data.get('parameter11', '')))
        self.label_116.setText(str(data.get('parameter3', '')))
        self.label_117.setText(str(data.get('parameter4', '')))
        self.label_118.setText(str(data.get('parameter5', '')))
        self.label_119.setText(str(data.get('parameter6', '')))
        self.label_104.setText(str(data.get('parameter9', '')))
        self.label_105.setText(str(data.get('parameter10', '')))  # 使用get方法提供默认值
    def _update_fjj_realtime(self, data):
        """更新挤出机实时数据"""
        self.label_53.setText(str(data.get('parameter12', '')))
        self.label_57.setText(str(data.get('parameter13', '')))
        self.label_61.setText(str(data.get('parameter14', '')))
        self.label_65.setText(str(data.get('parameter15', '')))  # 使用get方法提供默认值
    def _update_zdj_realtime(self, data):
        """更新挤出机实时数据"""
        self.label_73.setText(str(data.get('parameter16', '')))
        self.label_77.setText(str(data.get('parameter17', '')))
        self.label_81.setText(str(data.get('parameter18', '')))
        self.label_85.setText(str(data.get('parameter19', '')))
        self.label_89.setText(str(data.get('parameter20', '')))
        self.label_93.setText(str(data.get('parameter21', '')))  # 使用get方法提供默认值
    def _update_jcj_set(self, data):
        """更新挤出机实时数据"""
        self.lineEdit_4.setText(str(data.get('parameter1', '')))
        self.lineEdit_5.setText(str(data.get('parameter2', '')))
        self.lineEdit_6.setText(str(data.get('parameter3', '')))
        self.lineEdit_7.setText(str(data.get('parameter4', '')))
        self.lineEdit_8.setText(str(data.get('parameter5', '')))
        self.lineEdit_10.setText(str(data.get('parameter6', '')))  # 使用get方法提供默认值
    def _update_fjj_set(self, data):
        """更新挤出机实时数据"""
        self.lineEdit_13.setText(str(data.get('parameter1', '')))
        self.lineEdit_14.setText(str(data.get('parameter2', '')))
        self.lineEdit_16.setText(str(data.get('parameter3', '')))  # 使用get方法提供默认值
    def _update_zdj_set(self, data):
        """更新挤出机实时数据"""
        self.lineEdit_17.setText(str(data.get('parameter1', '')))
        self.lineEdit_18.setText(str(data.get('parameter2', '')))
        self.lineEdit_19.setText(str(data.get('parameter3', '')))
        self.lineEdit_20.setText(str(data.get('parameter4', '')))  # 使用get方法提供默认值
    def _update_curve_set(self, data):
        """更新挤出机实时数据"""
        self.lineEdit_23.setText(str(data.get('parameter1', '')))
        self.lineEdit_48.setText(str(data.get('parameter2', '')))
        self.label_114.setText(str(data.get('parameter3', '')))
        self.label_115.setText(str(data.get('parameter4', '')))
        self.lineEdit_51.setText(str(data.get('parameter5', '')))
        self.lineEdit_52.setText(str(data.get('parameter6', '')))  # 使用get方法提供默认值
    def show_dialog_pop_historical_parameter(self):
        """显示历史参数弹窗的方法"""
        self.hide()  # 隐藏当前窗口
        # 检查历史参数弹窗是否已存在
        if self.dialog_historical:
            # 如果弹窗已最小化或隐藏，则恢复显示
            if self.dialog_historical.isMinimized():
                self.dialog_historical.showNormal()  # 从最小化状态恢复
            elif not self.dialog_historical.isVisible():
                self.dialog_historical.show()  # 如果不可见则显示
            # 如果已经可见，则将其置于前台
            self.dialog_historical.activateWindow()  # 激活窗口（置于前台）
            self.dialog_historical.raise_()  # 提升窗口层级

    def center_dialog(self):
        """将弹窗居中显示的方法"""
        # 获取主屏幕尺寸
        screen = QApplication.primaryScreen().geometry()
        # 计算居中坐标（屏幕宽度-窗口宽度）/2
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        # 移动窗口到计算位置
        self.move(x, y)

    def dialog_mouse_press(self, event):
        """处理鼠标按下事件（用于窗口拖动）"""
        # 判断点击位置是否在标题栏区域内
        point_in_title = self.widget_title.rect().contains(event.pos())
        # 当左键点击且位置在标题栏时
        if event.button() == Qt.LeftButton and point_in_title:
            # 记录全局鼠标位置（屏幕坐标系）
            self.drag_start_pos = event.globalPos()
            # 保存窗口当前位置
            self.dialog_original_pos = self.pos()
            # 接受事件，阻止事件传递
            event.accept()
        else:
            # 忽略非标题栏区域的点击
            event.ignore()

    def dialog_mouse_move(self, event):
        """处理鼠标移动事件（实现窗口拖动）"""
        # 当满足三个条件时处理拖动：
        # 1. 左键保持按下状态
        # 2. 存在初始拖动位置记录
        # 3. 鼠标在标题栏区域
        if (event.buttons() & Qt.LeftButton and
                hasattr(self, 'drag_start_pos') and
                self.widget_title.rect().contains(event.pos())):

            # 计算位置偏移量（当前鼠标位置 - 起始位置）
            delta = event.globalPos() - self.drag_start_pos
            # 移动窗口到新位置（原始位置 + 偏移量）
            self.move(self.dialog_original_pos + delta)
            # 接受事件，确保操作流畅
            event.accept()
        else:
            # 忽略无效拖动操作
            event.ignore()

    # 参数弹窗类新增关闭事件处理
    # 重写窗口关闭事件处理方法（当窗口被关闭时自动触发）
    def closeEvent(self, event):
        """处理关闭事件：关闭关联的历史参数弹窗和停止所有线程"""
        # 停止数据更新线程
        if hasattr(self, 'threads'):
            for key, (thread, worker) in self.threads.items():
                if hasattr(worker, 'stop'):
                    worker.stop()

        # 检查是否存在历史参数弹窗实例
        if self.dialog_historical:
            self.dialog_historical.close()

        super().closeEvent(event)  # 调用父类的关闭事件处理

    @staticmethod  # 静态方法，不依赖实例对象
    def get_localtime():
        """获取本地时间的静态方法"""
        from datetime import datetime , timedelta
        now = datetime.now()  # 获取当前时间对象
        start_time = now - timedelta(minutes=10)  # 计算起始时间（当前时间向前10分钟）
        # 返回格式化后的日期和时间字符串
        return start_time.strftime("%H:%M:%S"), now.strftime("%H:%M:%S")

    def update_time(self):
        """更新时间显示的方法"""
        time_start_str, time_end_str = self.get_localtime()  # 解包日期时间
        self.label_106.setText(time_start_str)  # 更新日期标签
        self.label_107.setText(time_end_str)  # 更新时间标签
        self.label_112.setText(time_start_str)  # 更新日期标签
        self.label_113.setText(time_end_str)  # 更新时间标签

class ParameterDialogFactory2Device1(QDialog, Ui_Dialog_Pop_Parameter_Factory2Device1):
    def __init__(self):
        # 调用QDialog父类构造方法
        super().__init__()
        # 初始化UI界面
        self.param_mapping = None
        self.setWindowFlags(Qt.FramelessWindowHint)  # 设置无边框窗口样式（隐藏标题栏和边框）
        self.setAttribute(Qt.WA_TranslucentBackground)  # 启用透明背景属性（实现半透明/异形窗口效果）
        self.setupUi(self)  # 调用 UI 设计的 setupUi 方法

        self.dialog_historical = None  # 定义创建用于存储历史数据曲线弹窗的实例
        self.pushButton_historical_curve.clicked.connect(self.show_dialog_pop_historical_parameter)  # 连接按钮点击信号

        # 初始化位置记录变量
        self.dialog_original_pos = None  # 窗口原始位置
        self.drag_start_pos = None  # 鼠标拖动起始位置
        # 绑定鼠标事件到自身方法
        self.mousePressEvent = self.dialog_mouse_press  # 按下事件处理
        self.mouseMoveEvent = self.dialog_mouse_move  # 移动事件处理
        # 设置窗口居中属性
        self.center_dialog()  # 初始居中显示
        # 初始化时间功能
        self.timer = QTimer(self)  # 创建定时器对象
        self.timer.timeout.connect(self.update_time)  # type: ignore[attr-defined] # 连接定时信号
        self.timer.start(1000)  # 启动定时器（1秒间隔）
        self.update_time()  # 立即更新时间显示
        # 创建线程管理器字典
        self.threads = {}
        # 需要监控的表名列表
        self.tables_to_monitor = [
            "factory2_1_realtime_data_jcj",
            "factory2_1_realtime_data_fjj",
            "factory2_1_realtime_data_zdj",
            "factory2_1_set_data_jcj",
            "factory2_1_set_data_fjj",
            "factory2_1_set_data_zdj",
            "factory2_1_set_data_curve"
        ]

        # 启动数据更新线程
        self._start_data_update_thread(self.tables_to_monitor)
        # # 添加管径实时曲线（示例配置）
        # self.curve_plotter = RealTimeCurvePlotter(
        #     parent_widget=self.widget_pop_parameter_curve1,  # 对应UI中的曲线容器
        #     table_name="factory2_1_set_data_curve",
        #     params_config={
        #         'curve3': 'parameter3',
        #         'curve1': 'parameter1',
        #         'curve6': 'parameter6',
        #         'curve4': 'parameter4',
        #         'curve2': 'parameter2',
        #         'curve5': 'parameter5'
        #     },
        #     y_limits=(-1, 1)
        # )
        #
        # # 添加挤出机参数实时曲线（示例配置）
        # self.curve_jcj = RealTimeJcjCurvePlotter(
        #     parent_widget=self.widget_pop_parameter_curve2,  # 对应UI中的曲线容器
        #     table_name="factory2_1_realtime_data_jcj",
        #     params_config={
        #         'curve1': 'parameter3',
        #         'curve2': 'parameter4',
        #         'curve3': 'parameter5',
        #         'curve4': 'parameter6',
        #         'curve5': 'parameter9',
        #         'curve6': 'parameter10'
        #     },
        #     y_limits=(0, 200)
        # )


    # ------------------------- 数据更新线程启动方法 ------------------------
    # 添加新方法：启动数据更新线程
    def _start_data_update_thread(self, tables_to_monitor):
        """启动数据更新线程
        参数:
            tables_to_monitor: 需要监控的表名列表
        """
        # 创建线程对象
        thread = QThread()
        # 创建工作线程实例
        worker = DataUpdateWorker(tables_to_monitor)

        # 将工作对象移动到新线程
        worker.moveToThread(thread)

        # 信号连接
        thread.started.connect(worker.run)  # type: ignore[attr-defined]# 线程启动时执行run方法
        worker.finished.connect(thread.quit)  # type: ignore[attr-defined]# 工作完成时退出线程
        worker.finished.connect(worker.deleteLater)  # type: ignore[attr-defined]# 工作完成后销毁worker对象
        thread.finished.connect(thread.deleteLater)  # type: ignore[attr-defined]# 线程退出后销毁线程对象

        # 连接数据更新信号到处理方法
        worker.data_updated.connect(self._handle_data_update)   # type: ignore[attr-defined]

        # 存储线程引用
        self.threads['data_update5'] = (thread, worker)

        # 启动线程
        thread.start()

    # 添加新方法：处理数据更新
    def _handle_data_update(self, table_name, data):
        """处理从子线程接收到的数据更新
        参数:
            table_name: 表名
            data: 数据字典
        """
        # 创建策略映射字典（与原来相同）
        update_strategies = {
            "factory2_1_realtime_data_jcj": self._update_jcj_realtime,
            "factory2_1_realtime_data_fjj": self._update_fjj_realtime,
            "factory2_1_realtime_data_zdj": self._update_zdj_realtime,
            "factory2_1_set_data_jcj": self._update_jcj_set,
            "factory2_1_set_data_fjj": self._update_fjj_set,
            "factory2_1_set_data_zdj": self._update_zdj_set,
            "factory2_1_set_data_curve": self._update_curve_set
        }

        # 获取并执行对应的更新策略
        if strategy := update_strategies.get(table_name):
            if isinstance(strategy, list):  # 处理多个方法的情况
                for method in strategy:
                    method(data)    # type: ignore[attr-defined]
            else:
                strategy(data)  # type: ignore[attr-defined]
    # 分解原有的大更新方法为多个私有方法
    def _update_jcj_realtime(self, data):
        """更新挤出机实时数据"""
        self.label_10.setText(str(data.get('parameter1', '')))
        self.label_14.setText(str(data.get('parameter2', '')))
        self.label_18.setText(str(data.get('parameter3', '')))
        self.label_22.setText(str(data.get('parameter4', '')))
        self.label_26.setText(str(data.get('parameter5', '')))
        self.label_30.setText(str(data.get('parameter6', '')))
        self.label_34.setText(str(data.get('parameter7', '')))
        self.label_38.setText(str(data.get('parameter8', '')))
        self.label_42.setText(str(data.get('parameter9', '')))
        self.label_46.setText(str(data.get('parameter10', '')))
        self.label_50.setText(str(data.get('parameter11', '')))
        self.label_116.setText(str(data.get('parameter3', '')))
        self.label_117.setText(str(data.get('parameter4', '')))
        self.label_118.setText(str(data.get('parameter5', '')))
        self.label_119.setText(str(data.get('parameter6', '')))
        self.label_104.setText(str(data.get('parameter9', '')))
        self.label_105.setText(str(data.get('parameter10', '')))  # 使用get方法提供默认值
    def _update_fjj_realtime(self, data):
        """更新挤出机实时数据"""
        self.label_53.setText(str(data.get('parameter12', '')))
        self.label_57.setText(str(data.get('parameter13', '')))
        self.label_61.setText(str(data.get('parameter14', '')))
        self.label_65.setText(str(data.get('parameter15', '')))  # 使用get方法提供默认值
    def _update_zdj_realtime(self, data):
        """更新挤出机实时数据"""
        self.label_73.setText(str(data.get('parameter16', '')))
        self.label_77.setText(str(data.get('parameter17', '')))
        self.label_81.setText(str(data.get('parameter18', '')))
        self.label_85.setText(str(data.get('parameter19', '')))
        self.label_89.setText(str(data.get('parameter20', '')))
        self.label_93.setText(str(data.get('parameter21', '')))  # 使用get方法提供默认值
    def _update_jcj_set(self, data):
        """更新挤出机实时数据"""
        self.lineEdit_4.setText(str(data.get('parameter1', '')))
        self.lineEdit_5.setText(str(data.get('parameter2', '')))
        self.lineEdit_6.setText(str(data.get('parameter3', '')))
        self.lineEdit_7.setText(str(data.get('parameter4', '')))
        self.lineEdit_8.setText(str(data.get('parameter5', '')))
        self.lineEdit_10.setText(str(data.get('parameter6', '')))  # 使用get方法提供默认值
    def _update_fjj_set(self, data):
        """更新挤出机实时数据"""
        self.lineEdit_13.setText(str(data.get('parameter1', '')))
        self.lineEdit_14.setText(str(data.get('parameter2', '')))
        self.lineEdit_16.setText(str(data.get('parameter3', '')))  # 使用get方法提供默认值
    def _update_zdj_set(self, data):
        """更新挤出机实时数据"""
        self.lineEdit_17.setText(str(data.get('parameter1', '')))
        self.lineEdit_18.setText(str(data.get('parameter2', '')))
        self.lineEdit_19.setText(str(data.get('parameter3', '')))
        self.lineEdit_20.setText(str(data.get('parameter4', '')))  # 使用get方法提供默认值
    def _update_curve_set(self, data):
        """更新挤出机实时数据"""
        self.lineEdit_23.setText(str(data.get('parameter1', '')))
        self.lineEdit_48.setText(str(data.get('parameter2', '')))
        self.label_114.setText(str(data.get('parameter3', '')))
        self.label_115.setText(str(data.get('parameter4', '')))
        self.lineEdit_51.setText(str(data.get('parameter5', '')))
        self.lineEdit_52.setText(str(data.get('parameter6', '')))  # 使用get方法提供默认值
    def show_dialog_pop_historical_parameter(self):
        """显示历史参数弹窗的方法"""
        self.hide()  # 隐藏当前窗口
        # 检查历史参数弹窗是否已存在
        if self.dialog_historical:
            # 如果弹窗已最小化或隐藏，则恢复显示
            if self.dialog_historical.isMinimized():
                self.dialog_historical.showNormal()  # 从最小化状态恢复
            elif not self.dialog_historical.isVisible():
                self.dialog_historical.show()  # 如果不可见则显示
            # 如果已经可见，则将其置于前台
            self.dialog_historical.activateWindow()  # 激活窗口（置于前台）
            self.dialog_historical.raise_()  # 提升窗口层级

    def center_dialog(self):
        """将弹窗居中显示的方法"""
        # 获取主屏幕尺寸
        screen = QApplication.primaryScreen().geometry()
        # 计算居中坐标（屏幕宽度-窗口宽度）/2
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        # 移动窗口到计算位置
        self.move(x, y)

    def dialog_mouse_press(self, event):
        """处理鼠标按下事件（用于窗口拖动）"""
        # 判断点击位置是否在标题栏区域内
        point_in_title = self.widget_title.rect().contains(event.pos())
        # 当左键点击且位置在标题栏时
        if event.button() == Qt.LeftButton and point_in_title:
            # 记录全局鼠标位置（屏幕坐标系）
            self.drag_start_pos = event.globalPos()
            # 保存窗口当前位置
            self.dialog_original_pos = self.pos()
            # 接受事件，阻止事件传递
            event.accept()
        else:
            # 忽略非标题栏区域的点击
            event.ignore()

    def dialog_mouse_move(self, event):
        """处理鼠标移动事件（实现窗口拖动）"""
        # 当满足三个条件时处理拖动：
        # 1. 左键保持按下状态
        # 2. 存在初始拖动位置记录
        # 3. 鼠标在标题栏区域
        if (event.buttons() & Qt.LeftButton and
                hasattr(self, 'drag_start_pos') and
                self.widget_title.rect().contains(event.pos())):

            # 计算位置偏移量（当前鼠标位置 - 起始位置）
            delta = event.globalPos() - self.drag_start_pos
            # 移动窗口到新位置（原始位置 + 偏移量）
            self.move(self.dialog_original_pos + delta)
            # 接受事件，确保操作流畅
            event.accept()
        else:
            # 忽略无效拖动操作
            event.ignore()

    # 参数弹窗类新增关闭事件处理
    # 重写窗口关闭事件处理方法（当窗口被关闭时自动触发）
    def closeEvent(self, event):
        """处理关闭事件：关闭关联的历史参数弹窗和停止所有线程"""
        # 停止数据更新线程
        if hasattr(self, 'threads'):
            for key, (thread, worker) in self.threads.items():
                if hasattr(worker, 'stop'):
                    worker.stop()

        # 检查是否存在历史参数弹窗实例
        if self.dialog_historical:
            self.dialog_historical.close()

        super().closeEvent(event)  # 调用父类的关闭事件处理

    @staticmethod  # 静态方法，不依赖实例对象
    def get_localtime():
        """获取本地时间的静态方法"""
        from datetime import datetime , timedelta
        now = datetime.now()  # 获取当前时间对象
        start_time = now - timedelta(minutes=10)  # 计算起始时间（当前时间向前10分钟）
        # 返回格式化后的日期和时间字符串
        return start_time.strftime("%H:%M:%S"), now.strftime("%H:%M:%S")

    def update_time(self):
        """更新时间显示的方法"""
        time_start_str, time_end_str = self.get_localtime()  # 解包日期时间
        self.label_106.setText(time_start_str)  # 更新日期标签
        self.label_107.setText(time_end_str)  # 更新时间标签
        self.label_112.setText(time_start_str)  # 更新日期标签
        self.label_113.setText(time_end_str)  # 更新时间标签

class ParameterDialogFactory2Device2(QDialog, Ui_Dialog_Pop_Parameter_Factory2Device2):
    def __init__(self):
        # 调用QDialog父类构造方法
        super().__init__()
        # 初始化UI界面
        self.param_mapping = None
        self.setWindowFlags(Qt.FramelessWindowHint)  # 设置无边框窗口样式（隐藏标题栏和边框）
        self.setAttribute(Qt.WA_TranslucentBackground)  # 启用透明背景属性（实现半透明/异形窗口效果）
        self.setupUi(self)  # 调用 UI 设计的 setupUi 方法

        self.dialog_historical = None  # 定义创建用于存储历史数据曲线弹窗的实例
        self.pushButton_historical_curve.clicked.connect(self.show_dialog_pop_historical_parameter)  # 连接按钮点击信号

        # 初始化位置记录变量
        self.dialog_original_pos = None  # 窗口原始位置
        self.drag_start_pos = None  # 鼠标拖动起始位置
        # 绑定鼠标事件到自身方法
        self.mousePressEvent = self.dialog_mouse_press  # 按下事件处理
        self.mouseMoveEvent = self.dialog_mouse_move  # 移动事件处理
        # 设置窗口居中属性
        self.center_dialog()  # 初始居中显示
        # 初始化时间功能
        self.timer = QTimer(self)  # 创建定时器对象
        self.timer.timeout.connect(self.update_time)  # type: ignore[attr-defined] # 连接定时信号
        self.timer.start(1000)  # 启动定时器（1秒间隔）
        self.update_time()  # 立即更新时间显示
        # 创建线程管理器字典
        self.threads = {}
        # 需要监控的表名列表
        self.tables_to_monitor = [
            "factory2_2_realtime_data_jcj",
            "factory2_2_realtime_data_fjj",
            "factory2_2_realtime_data_zdj",
            "factory2_2_set_data_jcj",
            "factory2_2_set_data_fjj",
            "factory2_2_set_data_zdj",
            "factory2_2_set_data_curve"
        ]

        # 启动数据更新线程
        self._start_data_update_thread(self.tables_to_monitor)
        # # 添加管径实时曲线（示例配置）
        # self.curve_plotter = RealTimeCurvePlotter(
        #     parent_widget=self.widget_pop_parameter_curve1,  # 对应UI中的曲线容器
        #     table_name="factory2_2_set_data_curve",
        #     params_config={
        #         'curve3': 'parameter3',
        #         'curve1': 'parameter1',
        #         'curve6': 'parameter6',
        #         'curve4': 'parameter4',
        #         'curve2': 'parameter2',
        #         'curve5': 'parameter5'
        #     },
        #     y_limits=(-1, 1)
        # )
        #
        # # 添加挤出机参数实时曲线（示例配置）
        # self.curve_jcj = RealTimeJcjCurvePlotter(
        #     parent_widget=self.widget_pop_parameter_curve2,  # 对应UI中的曲线容器
        #     table_name="factory2_2_realtime_data_jcj",
        #     params_config={
        #         'curve1': 'parameter3',
        #         'curve2': 'parameter4',
        #         'curve3': 'parameter5',
        #         'curve4': 'parameter6',
        #         'curve5': 'parameter9',
        #         'curve6': 'parameter10'
        #     },
        #     y_limits=(0, 200)
        # )


    # ------------------------- 数据更新线程启动方法 -------------------------
    # 添加新方法：启动数据更新线程
    def _start_data_update_thread(self, tables_to_monitor):
        """启动数据更新线程
        参数:
            tables_to_monitor: 需要监控的表名列表
        """
        # 创建线程对象
        thread = QThread()
        # 创建工作线程实例
        worker = DataUpdateWorker(tables_to_monitor)

        # 将工作对象移动到新线程
        worker.moveToThread(thread)

        # 信号连接
        thread.started.connect(worker.run)  # type: ignore[attr-defined]# 线程启动时执行run方法
        worker.finished.connect(thread.quit)  # type: ignore[attr-defined]# 工作完成时退出线程
        worker.finished.connect(worker.deleteLater)  # type: ignore[attr-defined]# 工作完成后销毁worker对象
        thread.finished.connect(thread.deleteLater)  # type: ignore[attr-defined]# 线程退出后销毁线程对象

        # 连接数据更新信号到处理方法
        worker.data_updated.connect(self._handle_data_update)   # type: ignore[attr-defined]

        # 存储线程引用
        self.threads['data_update6'] = (thread, worker)

        # 启动线程
        thread.start()

    # 添加新方法：处理数据更新
    def _handle_data_update(self, table_name, data):
        """处理从子线程接收到的数据更新
        参数:
            table_name: 表名
            data: 数据字典
        """
        # 创建策略映射字典（与原来相同）
        update_strategies = {
            "factory2_2_realtime_data_jcj": self._update_jcj_realtime,
            "factory2_2_realtime_data_fjj": self._update_fjj_realtime,
            "factory2_2_realtime_data_zdj": self._update_zdj_realtime,
            "factory2_2_set_data_jcj": self._update_jcj_set,
            "factory2_2_set_data_fjj": self._update_fjj_set,
            "factory2_2_set_data_zdj": self._update_zdj_set,
            "factory2_2_set_data_curve": self._update_curve_set
        }

        # 获取并执行对应的更新策略
        if strategy := update_strategies.get(table_name):
            if isinstance(strategy, list):  # 处理多个方法的情况
                for method in strategy:
                    method(data)    # type: ignore[attr-defined]
            else:
                strategy(data)  # type: ignore[attr-defined]
    # 分解原有的大更新方法为多个私有方法
    def _update_jcj_realtime(self, data):
        """更新挤出机实时数据"""
        self.label_10.setText(str(data.get('parameter1', '')))
        self.label_14.setText(str(data.get('parameter2', '')))
        self.label_18.setText(str(data.get('parameter3', '')))
        self.label_22.setText(str(data.get('parameter4', '')))
        self.label_26.setText(str(data.get('parameter5', '')))
        self.label_30.setText(str(data.get('parameter6', '')))
        self.label_34.setText(str(data.get('parameter7', '')))
        self.label_38.setText(str(data.get('parameter8', '')))
        self.label_42.setText(str(data.get('parameter9', '')))
        self.label_46.setText(str(data.get('parameter10', '')))
        self.label_50.setText(str(data.get('parameter11', '')))
        self.label_116.setText(str(data.get('parameter3', '')))
        self.label_117.setText(str(data.get('parameter4', '')))
        self.label_118.setText(str(data.get('parameter5', '')))
        self.label_119.setText(str(data.get('parameter6', '')))
        self.label_104.setText(str(data.get('parameter9', '')))
        self.label_105.setText(str(data.get('parameter10', '')))  # 使用get方法提供默认值
    def _update_fjj_realtime(self, data):
        """更新挤出机实时数据"""
        self.label_53.setText(str(data.get('parameter12', '')))
        self.label_57.setText(str(data.get('parameter13', '')))
        self.label_61.setText(str(data.get('parameter14', '')))
        self.label_65.setText(str(data.get('parameter15', '')))  # 使用get方法提供默认值
    def _update_zdj_realtime(self, data):
        """更新挤出机实时数据"""
        self.label_73.setText(str(data.get('parameter16', '')))
        self.label_77.setText(str(data.get('parameter17', '')))
        self.label_81.setText(str(data.get('parameter18', '')))
        self.label_85.setText(str(data.get('parameter19', '')))
        self.label_89.setText(str(data.get('parameter20', '')))
        self.label_93.setText(str(data.get('parameter21', '')))  # 使用get方法提供默认值
    def _update_jcj_set(self, data):
        """更新挤出机实时数据"""
        self.lineEdit_4.setText(str(data.get('parameter1', '')))
        self.lineEdit_5.setText(str(data.get('parameter2', '')))
        self.lineEdit_6.setText(str(data.get('parameter3', '')))
        self.lineEdit_7.setText(str(data.get('parameter4', '')))
        self.lineEdit_8.setText(str(data.get('parameter5', '')))
        self.lineEdit_10.setText(str(data.get('parameter6', '')))  # 使用get方法提供默认值
    def _update_fjj_set(self, data):
        """更新挤出机实时数据"""
        self.lineEdit_13.setText(str(data.get('parameter1', '')))
        self.lineEdit_14.setText(str(data.get('parameter2', '')))
        self.lineEdit_16.setText(str(data.get('parameter3', '')))  # 使用get方法提供默认值
    def _update_zdj_set(self, data):
        """更新挤出机实时数据"""
        self.lineEdit_17.setText(str(data.get('parameter1', '')))
        self.lineEdit_18.setText(str(data.get('parameter2', '')))
        self.lineEdit_19.setText(str(data.get('parameter3', '')))
        self.lineEdit_20.setText(str(data.get('parameter4', '')))  # 使用get方法提供默认值
    def _update_curve_set(self, data):
        """更新挤出机实时数据"""
        self.lineEdit_23.setText(str(data.get('parameter1', '')))
        self.lineEdit_48.setText(str(data.get('parameter2', '')))
        self.label_114.setText(str(data.get('parameter3', '')))
        self.label_115.setText(str(data.get('parameter4', '')))
        self.lineEdit_51.setText(str(data.get('parameter5', '')))
        self.lineEdit_52.setText(str(data.get('parameter6', '')))  # 使用get方法提供默认值
    def show_dialog_pop_historical_parameter(self):
        """显示历史参数弹窗的方法"""
        self.hide()  # 隐藏当前窗口
        # 检查历史参数弹窗是否已存在
        if self.dialog_historical:
            # 如果弹窗已最小化或隐藏，则恢复显示
            if self.dialog_historical.isMinimized():
                self.dialog_historical.showNormal()  # 从最小化状态恢复
            elif not self.dialog_historical.isVisible():
                self.dialog_historical.show()  # 如果不可见则显示
            # 如果已经可见，则将其置于前台
            self.dialog_historical.activateWindow()  # 激活窗口（置于前台）
            self.dialog_historical.raise_()  # 提升窗口层级

    def center_dialog(self):
        """将弹窗居中显示的方法"""
        # 获取主屏幕尺寸
        screen = QApplication.primaryScreen().geometry()
        # 计算居中坐标（屏幕宽度-窗口宽度）/2
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        # 移动窗口到计算位置
        self.move(x, y)

    def dialog_mouse_press(self, event):
        """处理鼠标按下事件（用于窗口拖动）"""
        # 判断点击位置是否在标题栏区域内
        point_in_title = self.widget_title.rect().contains(event.pos())
        # 当左键点击且位置在标题栏时
        if event.button() == Qt.LeftButton and point_in_title:
            # 记录全局鼠标位置（屏幕坐标系）
            self.drag_start_pos = event.globalPos()
            # 保存窗口当前位置
            self.dialog_original_pos = self.pos()
            # 接受事件，阻止事件传递
            event.accept()
        else:
            # 忽略非标题栏区域的点击
            event.ignore()

    def dialog_mouse_move(self, event):
        """处理鼠标移动事件（实现窗口拖动）"""
        # 当满足三个条件时处理拖动：
        # 1. 左键保持按下状态
        # 2. 存在初始拖动位置记录
        # 3. 鼠标在标题栏区域
        if (event.buttons() & Qt.LeftButton and
                hasattr(self, 'drag_start_pos') and
                self.widget_title.rect().contains(event.pos())):

            # 计算位置偏移量（当前鼠标位置 - 起始位置）
            delta = event.globalPos() - self.drag_start_pos
            # 移动窗口到新位置（原始位置 + 偏移量）
            self.move(self.dialog_original_pos + delta)
            # 接受事件，确保操作流畅
            event.accept()
        else:
            # 忽略无效拖动操作
            event.ignore()

    # 参数弹窗类新增关闭事件处理
    # 重写窗口关闭事件处理方法（当窗口被关闭时自动触发）
    def closeEvent(self, event):
        """处理关闭事件：关闭关联的历史参数弹窗和停止所有线程"""
        # 停止数据更新线程
        if hasattr(self, 'threads'):
            for key, (thread, worker) in self.threads.items():
                if hasattr(worker, 'stop'):
                    worker.stop()

        # 检查是否存在历史参数弹窗实例
        if self.dialog_historical:
            self.dialog_historical.close()

        super().closeEvent(event)  # 调用父类的关闭事件处理

    @staticmethod  # 静态方法，不依赖实例对象
    def get_localtime():
        """获取本地时间的静态方法"""
        from datetime import datetime , timedelta
        now = datetime.now()  # 获取当前时间对象
        start_time = now - timedelta(minutes=10)  # 计算起始时间（当前时间向前10分钟）
        # 返回格式化后的日期和时间字符串
        return start_time.strftime("%H:%M:%S"), now.strftime("%H:%M:%S")

    def update_time(self):
        """更新时间显示的方法"""
        time_start_str, time_end_str = self.get_localtime()  # 解包日期时间
        self.label_106.setText(time_start_str)  # 更新日期标签
        self.label_107.setText(time_end_str)  # 更新时间标签
        self.label_112.setText(time_start_str)  # 更新日期标签
        self.label_113.setText(time_end_str)  # 更新时间标签

class ParameterDialogFactory2Device3(QDialog, Ui_Dialog_Pop_Parameter_Factory2Device3):
    def __init__(self):
        # 调用QDialog父类构造方法
        super().__init__()
        # 初始化UI界面
        self.param_mapping = None
        self.setWindowFlags(Qt.FramelessWindowHint)  # 设置无边框窗口样式（隐藏标题栏和边框）
        self.setAttribute(Qt.WA_TranslucentBackground)  # 启用透明背景属性（实现半透明/异形窗口效果）
        self.setupUi(self)  # 调用 UI 设计的 setupUi 方法

        self.dialog_historical = None  # 定义创建用于存储历史数据曲线弹窗的实例
        self.pushButton_historical_curve.clicked.connect(self.show_dialog_pop_historical_parameter)  # 连接按钮点击信号

        # 初始化位置记录变量
        self.dialog_original_pos = None  # 窗口原始位置
        self.drag_start_pos = None  # 鼠标拖动起始位置
        # 绑定鼠标事件到自身方法
        self.mousePressEvent = self.dialog_mouse_press  # 按下事件处理
        self.mouseMoveEvent = self.dialog_mouse_move  # 移动事件处理
        # 设置窗口居中属性
        self.center_dialog()  # 初始居中显示
        # 初始化时间功能
        self.timer = QTimer(self)  # 创建定时器对象
        self.timer.timeout.connect(self.update_time)  # type: ignore[attr-defined] # 连接定时信号
        self.timer.start(1000)  # 启动定时器（1秒间隔）
        self.update_time()  # 立即更新时间显示
        # 创建线程管理器字典
        self.threads = {}
        # 需要监控的表名列表
        self.tables_to_monitor = [
            "factory2_3_realtime_data_jcj",
            "factory2_3_realtime_data_fjj",
            "factory2_3_realtime_data_zdj",
            "factory2_3_set_data_jcj",
            "factory2_3_set_data_fjj",
            "factory2_3_set_data_zdj",
            "factory2_3_set_data_curve"
        ]

        # 启动数据更新线程
        self._start_data_update_thread(self.tables_to_monitor)
        # # 添加管径实时曲线（示例配置）
        # self.curve_plotter = RealTimeCurvePlotter(
        #     parent_widget=self.widget_pop_parameter_curve1,  # 对应UI中的曲线容器
        #     table_name="factory2_3_set_data_curve",
        #     params_config={
        #         'curve3': 'parameter3',
        #         'curve1': 'parameter1',
        #         'curve6': 'parameter6',
        #         'curve4': 'parameter4',
        #         'curve2': 'parameter2',
        #         'curve5': 'parameter5'
        #     },
        #     y_limits=(-1, 1)
        # )
        #
        # # 添加挤出机参数实时曲线（示例配置）
        # self.curve_jcj = RealTimeJcjCurvePlotter(
        #     parent_widget=self.widget_pop_parameter_curve2,  # 对应UI中的曲线容器
        #     table_name="factory2_3_realtime_data_jcj",
        #     params_config={
        #         'curve1': 'parameter3',
        #         'curve2': 'parameter4',
        #         'curve3': 'parameter5',
        #         'curve4': 'parameter6',
        #         'curve5': 'parameter9',
        #         'curve6': 'parameter10'
        #     },
        #     y_limits=(0, 200)
        # )


    # ------------------------- 数据更新线程启动方法 -------------------------
    # 添加新方法：启动数据更新线程
    def _start_data_update_thread(self, tables_to_monitor):
        """启动数据更新线程
        参数:
            tables_to_monitor: 需要监控的表名列表
        """
        # 创建线程对象
        thread = QThread()
        # 创建工作线程实例
        worker = DataUpdateWorker(tables_to_monitor)

        # 将工作对象移动到新线程
        worker.moveToThread(thread)

        # 信号连接
        thread.started.connect(worker.run)  # type: ignore[attr-defined]# 线程启动时执行run方法
        worker.finished.connect(thread.quit)  # type: ignore[attr-defined]# 工作完成时退出线程
        worker.finished.connect(worker.deleteLater)  # type: ignore[attr-defined]# 工作完成后销毁worker对象
        thread.finished.connect(thread.deleteLater)  # type: ignore[attr-defined]# 线程退出后销毁线程对象

        # 连接数据更新信号到处理方法
        worker.data_updated.connect(self._handle_data_update)# type: ignore[attr-defined]

        # 存储线程引用
        self.threads['data_update7'] = (thread, worker)

        # 启动线程
        thread.start()

    # 添加新方法：处理数据更新
    def _handle_data_update(self, table_name, data):
        """处理从子线程接收到的数据更新
        参数:
            table_name: 表名
            data: 数据字典
        """
        # 创建策略映射字典（与原来相同）
        update_strategies = {
            "factory2_3_realtime_data_jcj": self._update_jcj_realtime,
            "factory2_3_realtime_data_fjj": self._update_fjj_realtime,
            "factory2_3_realtime_data_zdj": self._update_zdj_realtime,
            "factory2_3_set_data_jcj": self._update_jcj_set,
            "factory2_3_set_data_fjj": self._update_fjj_set,
            "factory2_3_set_data_zdj": self._update_zdj_set,
            "factory2_3_set_data_curve": self._update_curve_set
        }

        # 获取并执行对应的更新策略
        if strategy := update_strategies.get(table_name):
            if isinstance(strategy, list):  # 处理多个方法的情况
                for method in strategy:
                    method(data)    # type: ignore[attr-defined]
            else:
                strategy(data)  # type: ignore[attr-defined]
    # 分解原有的大更新方法为多个私有方法
    def _update_jcj_realtime(self, data):
        """更新挤出机实时数据"""
        self.label_10.setText(str(data.get('parameter1', '')))
        self.label_14.setText(str(data.get('parameter2', '')))
        self.label_18.setText(str(data.get('parameter3', '')))
        self.label_22.setText(str(data.get('parameter4', '')))
        self.label_26.setText(str(data.get('parameter5', '')))
        self.label_30.setText(str(data.get('parameter6', '')))
        self.label_34.setText(str(data.get('parameter7', '')))
        self.label_38.setText(str(data.get('parameter8', '')))
        self.label_42.setText(str(data.get('parameter9', '')))
        self.label_46.setText(str(data.get('parameter10', '')))
        self.label_50.setText(str(data.get('parameter11', '')))
        self.label_116.setText(str(data.get('parameter3', '')))
        self.label_117.setText(str(data.get('parameter4', '')))
        self.label_118.setText(str(data.get('parameter5', '')))
        self.label_119.setText(str(data.get('parameter6', '')))
        self.label_104.setText(str(data.get('parameter9', '')))
        self.label_105.setText(str(data.get('parameter10', '')))  # 使用get方法提供默认值
    def _update_fjj_realtime(self, data):
        """更新挤出机实时数据"""
        self.label_53.setText(str(data.get('parameter12', '')))
        self.label_57.setText(str(data.get('parameter13', '')))
        self.label_61.setText(str(data.get('parameter14', '')))
        self.label_65.setText(str(data.get('parameter15', '')))  # 使用get方法提供默认值
    def _update_zdj_realtime(self, data):
        """更新挤出机实时数据"""
        self.label_73.setText(str(data.get('parameter16', '')))
        self.label_77.setText(str(data.get('parameter17', '')))
        self.label_81.setText(str(data.get('parameter18', '')))
        self.label_85.setText(str(data.get('parameter19', '')))
        self.label_89.setText(str(data.get('parameter20', '')))
        self.label_93.setText(str(data.get('parameter21', '')))  # 使用get方法提供默认值
    def _update_jcj_set(self, data):
        """更新挤出机实时数据"""
        self.lineEdit_4.setText(str(data.get('parameter1', '')))
        self.lineEdit_5.setText(str(data.get('parameter2', '')))
        self.lineEdit_6.setText(str(data.get('parameter3', '')))
        self.lineEdit_7.setText(str(data.get('parameter4', '')))
        self.lineEdit_8.setText(str(data.get('parameter5', '')))
        self.lineEdit_10.setText(str(data.get('parameter6', '')))  # 使用get方法提供默认值
    def _update_fjj_set(self, data):
        """更新挤出机实时数据"""
        self.lineEdit_13.setText(str(data.get('parameter1', '')))
        self.lineEdit_14.setText(str(data.get('parameter2', '')))
        self.lineEdit_16.setText(str(data.get('parameter3', '')))  # 使用get方法提供默认值
    def _update_zdj_set(self, data):
        """更新挤出机实时数据"""
        self.lineEdit_17.setText(str(data.get('parameter1', '')))
        self.lineEdit_18.setText(str(data.get('parameter2', '')))
        self.lineEdit_19.setText(str(data.get('parameter3', '')))
        self.lineEdit_20.setText(str(data.get('parameter4', '')))  # 使用get方法提供默认值
    def _update_curve_set(self, data):
        """更新挤出机实时数据"""
        self.lineEdit_23.setText(str(data.get('parameter1', '')))
        self.lineEdit_48.setText(str(data.get('parameter2', '')))
        self.label_114.setText(str(data.get('parameter3', '')))
        self.label_115.setText(str(data.get('parameter4', '')))
        self.lineEdit_51.setText(str(data.get('parameter5', '')))
        self.lineEdit_52.setText(str(data.get('parameter6', '')))  # 使用get方法提供默认值
    def show_dialog_pop_historical_parameter(self):
        """显示历史参数弹窗的方法"""
        self.hide()  # 隐藏当前窗口
        # 检查历史参数弹窗是否已存在
        if self.dialog_historical:
            # 如果弹窗已最小化或隐藏，则恢复显示
            if self.dialog_historical.isMinimized():
                self.dialog_historical.showNormal()  # 从最小化状态恢复
            elif not self.dialog_historical.isVisible():
                self.dialog_historical.show()  # 如果不可见则显示
            # 如果已经可见，则将其置于前台
            self.dialog_historical.activateWindow()  # 激活窗口（置于前台）
            self.dialog_historical.raise_()  # 提升窗口层级

    def center_dialog(self):
        """将弹窗居中显示的方法"""
        # 获取主屏幕尺寸
        screen = QApplication.primaryScreen().geometry()
        # 计算居中坐标（屏幕宽度-窗口宽度）/2
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        # 移动窗口到计算位置
        self.move(x, y)

    def dialog_mouse_press(self, event):
        """处理鼠标按下事件（用于窗口拖动）"""
        # 判断点击位置是否在标题栏区域内
        point_in_title = self.widget_title.rect().contains(event.pos())
        # 当左键点击且位置在标题栏时
        if event.button() == Qt.LeftButton and point_in_title:
            # 记录全局鼠标位置（屏幕坐标系）
            self.drag_start_pos = event.globalPos()
            # 保存窗口当前位置
            self.dialog_original_pos = self.pos()
            # 接受事件，阻止事件传递
            event.accept()
        else:
            # 忽略非标题栏区域的点击
            event.ignore()

    def dialog_mouse_move(self, event):
        """处理鼠标移动事件（实现窗口拖动）"""
        # 当满足三个条件时处理拖动：
        # 1. 左键保持按下状态
        # 2. 存在初始拖动位置记录
        # 3. 鼠标在标题栏区域
        if (event.buttons() & Qt.LeftButton and
                hasattr(self, 'drag_start_pos') and
                self.widget_title.rect().contains(event.pos())):

            # 计算位置偏移量（当前鼠标位置 - 起始位置）
            delta = event.globalPos() - self.drag_start_pos
            # 移动窗口到新位置（原始位置 + 偏移量）
            self.move(self.dialog_original_pos + delta)
            # 接受事件，确保操作流畅
            event.accept()
        else:
            # 忽略无效拖动操作
            event.ignore()

    # 参数弹窗类新增关闭事件处理
    # 重写窗口关闭事件处理方法（当窗口被关闭时自动触发）
    def closeEvent(self, event):
        """处理关闭事件：关闭关联的历史参数弹窗和停止所有线程"""
        # 停止数据更新线程
        if hasattr(self, 'threads'):
            for key, (thread, worker) in self.threads.items():
                if hasattr(worker, 'stop'):
                    worker.stop()

        # 检查是否存在历史参数弹窗实例
        if self.dialog_historical:
            self.dialog_historical.close()

        super().closeEvent(event)  # 调用父类的关闭事件处理

    @staticmethod  # 静态方法，不依赖实例对象
    def get_localtime():
        """获取本地时间的静态方法"""
        from datetime import datetime , timedelta
        now = datetime.now()  # 获取当前时间对象
        start_time = now - timedelta(minutes=10)  # 计算起始时间（当前时间向前10分钟）
        # 返回格式化后的日期和时间字符串
        return start_time.strftime("%H:%M:%S"), now.strftime("%H:%M:%S")

    def update_time(self):
        """更新时间显示的方法"""
        time_start_str, time_end_str = self.get_localtime()  # 解包日期时间
        self.label_106.setText(time_start_str)  # 更新日期标签
        self.label_107.setText(time_end_str)  # 更新时间标签
        self.label_112.setText(time_start_str)  # 更新日期标签
        self.label_113.setText(time_end_str)  # 更新时间标签

# ---------------------------------历史参数弹窗类（继承QDialog和UI类）---------------------------------
class HistoricalParameterDialog(QDialog, Ui_Dialog_Pop_Historical_Parameter):
    def __init__(self):
        # 调用父类构造方法
        super().__init__()
        # 初始化UI界面
        self.threads = {}
        self.setWindowFlags(Qt.FramelessWindowHint)  # 设置无边框窗口样式（隐藏标题栏和边框）
        self.setAttribute(Qt.WA_TranslucentBackground)  # 启用透明背景属性（实现半透明/异形窗口效果）
        self.setupUi(self)

        self.dialog_realtime = None  # 定义创建用于存储历史数据曲线弹窗的实例
        self.pushButton_realtime.clicked.connect(self.show_dialog_pop_parameter)  # 连接按钮点击信号

        # 初始化位置记录变量
        self.dialog_original_pos = None  # 窗口原始位置
        self.drag_start_pos = None  # 鼠标拖动起始位置
        # 绑定鼠标事件到自身方法
        self.mousePressEvent = self.dialog_mouse_press  # 按下事件处理
        self.mouseMoveEvent = self.dialog_mouse_move  # 移动事件处理
        # 设置窗口居中属性
        self.center_dialog()  # 初始居中显示
        self.dateTimeEdit.setDateTime(datetime.now())
        # 连接查询按钮
        self.pushButton_historical_query.clicked.connect(self.handle_historical_query)
        # 初始化历史曲线
        self._init_historical_curves()

    def _init_historical_curves(self):
        """初始化历史曲线组件"""
        # 管径历史曲线 (创建历史曲线绘制组件)
        self.hist_curve1 = HistoricalCurvePlotter(
            self.widget_pop_historical_parameter_curve1,  # 指定父容器控件
            "factory1_1_set_data_curve",  # 对应的数据库表名
            {'curve1': {'field': 'parameter1', 'color': '#FF0000'},
                        'curve2': {'field': 'parameter2', 'color': '#FFFF00'},
                        'curve3': {'field': 'parameter3', 'color': '#00FFFF'},
                        'curve4': {'field': 'parameter4', 'color': '#00FF00'},
                        'curve5': {'field': 'parameter5', 'color': '#FFFF00'},
                        'curve6': {'field': 'parameter6', 'color': '#FF0000'}
             },  # 曲线参数映射配置
            (-1, 1)  # Y轴显示范围
        )

        # 挤出机历史曲线 (第二组历史曲线)
        self.hist_curve2 = HistoricalCurvePlotter(
            self.widget_pop_historical_parameter_curve2,  # 第二个曲线容器的父控件
            "factory1_1_realtime_data_jcj",  # 挤出机实时数据表
            {'curve1': {'field': 'parameter3', 'color': '#FF0000'},
             'curve2': {'field': 'parameter4', 'color': '#FFFF00'},
             'curve3': {'field': 'parameter5', 'color': '#00FFFF'},
             'curve4': {'field': 'parameter6', 'color': '#00FF00'},
             'curve5': {'field': 'parameter9', 'color': '#FFAA00'},
             'curve6': {'field': 'parameter10', 'color': '#FF55FF'}
             },  # 参数映射关系
            (0, 200)  # Y轴最大范围200
        )

    def handle_historical_query(self):
        """处理历史查询按钮点击事件的核心方法"""
        # 获取界面选择的时间（转换为Python datetime对象）
        query_time = self.dateTimeEdit.dateTime().toPyDateTime()
        # 计算结束时间（格式化成SQL可识别的字符串）
        end_time = query_time.strftime("%Y-%m-%d %H:%M:%S")
        # 计算起始时间（当前查询时间前推10分钟）
        start_time = (query_time - timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")
        # 更新两条历史曲线（触发重绘）
        self.hist_curve1.update_plot(start_time, end_time)  # 更新管径曲线
        self.hist_curve2.update_plot(start_time, end_time)  # 更新挤出机曲线

        # 更新参数显示（精确到秒的查询）
        self._update_parameters(
        query_time.strftime("%Y-%m-%d %H:%M:%S"),
        start_time,
        end_time)

    def _update_parameters(self, exact_time, start_time, end_time):
        """更新指定时间点的参数显示
        Args:
            exact_time: 精确时间字符串（格式：YYYY-MM-DD HH:MM:SS）
        """
        # 定义需要查询的数据表列表
        tables = ["factory1_1_realtime_data_jcj", "factory1_1_realtime_data_fjj", "factory1_1_realtime_data_zdj" , "factory1_1_set_data_curve",
                  "factory1_1_set_data_jcj", "factory1_1_set_data_fjj", "factory1_1_set_data_zdj"]

        # 创建线程对象
        thread = QThread()
        # 创建工作线程实例
        worker = HistoricalDataQueryWorker(tables, exact_time, start_time, end_time)

        # 将工作对象移动到新线程
        worker.moveToThread(thread)

        # 信号连接
        thread.started.connect(worker.run)  # type: ignore[attr-defined]
        worker.finished.connect(thread.quit)    # type: ignore[attr-defined]
        worker.finished.connect(worker.deleteLater)# type: ignore[attr-defined]
        thread.finished.connect(thread.deleteLater)# type: ignore[attr-defined]

        # 连接数据更新信号到处理方法
        worker.data_ready.connect(self._handle_historical_data)# type: ignore[attr-defined]

        # 存储线程引用
        self.threads['historical_query'] = (thread, worker)

        # 启动线程
        thread.start()
    def _handle_historical_data(self, result_data):
        """处理从子线程接收到的历史数据
        Args:
            result_data: 包含表名和数据的字典 {table_name: data}
        """
        # 遍历所有返回的数据
        for table_name, data in result_data.items():
            # 如果有返回数据（即使只有一条）
            if data:
                # 更新界面标签（取第一条/唯一一条数据）
                self._update_ui_labels(table_name, data)
    def _update_ui_labels(self, table_name, data):
        """根据数据表名更新对应的UI标签
        Args:
            table_name: 数据表名称（用于分支判断）
            data: 单条历史数据记录（字典格式）
        """
        # 挤出机实时数据表处理分支
        if table_name == "factory1_1_realtime_data_jcj":
            # 更新参数1显示（label_10标签）
            self.label_10.setText(str(data.get('parameter1', '')))  # 使用空字符串作为默认值
            # 更新参数2显示（label_14标签）
            self.label_14.setText(str(data.get('parameter2', '')))
            self.label_18.setText(str(data.get('parameter3', '')))
            self.label_22.setText(str(data.get('parameter4', '')))
            self.label_26.setText(str(data.get('parameter5', '')))
            self.label_30.setText(str(data.get('parameter6', '')))
            self.label_34.setText(str(data.get('parameter7', '')))
            self.label_38.setText(str(data.get('parameter8', '')))
            self.label_42.setText(str(data.get('parameter9', '')))
            self.label_46.setText(str(data.get('parameter10', '')))
            self.label_50.setText(str(data.get('parameter11', '')))
            self.label_123.setText(str(data.get('parameter3', '')))
            self.label_127.setText(str(data.get('parameter4', '')))
            self.label_125.setText(str(data.get('parameter5', '')))
            self.label_126.setText(str(data.get('parameter6', '')))
            self.label_128.setText(str(data.get('parameter9', '')))
            self.label_124.setText(str(data.get('parameter10', '')))  # 使用get方法提供默认值
        # 放卷机实时数据表处理分支
        elif table_name == "factory1_1_realtime_data_fjj":
            # 更新参数12显示（label_53标签）
            self.label_53.setText(str(data.get('parameter12', '')))
            self.label_57.setText(str(data.get('parameter13', '')))
            self.label_61.setText(str(data.get('parameter14', '')))
            self.label_65.setText(str(data.get('parameter15', '')))  # 使用get方法提供默认值
        # 自动机历史数据表处理分支
        elif table_name == "factory1_1_realtime_data_zdj":
            self.label_73.setText(str(data.get('parameter16', '')))
            self.label_77.setText(str(data.get('parameter17', '')))
            self.label_81.setText(str(data.get('parameter18', '')))
            self.label_85.setText(str(data.get('parameter19', '')))
            self.label_89.setText(str(data.get('parameter20', '')))
            self.label_93.setText(str(data.get('parameter21', '')))  # 使用get方法提供默认值
        elif table_name == "factory1_1_set_data_jcj":
            self.label_104.setText(str(data.get('parameter1', '')))
            self.label_105.setText(str(data.get('parameter2', '')))
            self.label_106.setText(str(data.get('parameter3', '')))
            self.label_107.setText(str(data.get('parameter4', '')))
            self.label_108.setText(str(data.get('parameter5', '')))
            self.label_115.setText(str(data.get('parameter6', '')))  # 使用get方法提供默认值
        elif table_name == "factory1_1_set_data_fjj":
            self.label_109.setText(str(data.get('parameter1', '')))
            self.label_110.setText(str(data.get('parameter2', '')))
            self.label_111.setText(str(data.get('parameter3', '')))  # 使用get方法提供默认值
        elif table_name == "factory1_1_set_data_zdj":
            self.label_112.setText(str(data.get('parameter1', '')))
            self.label_113.setText(str(data.get('parameter2', '')))
            self.label_114.setText(str(data.get('parameter3', '')))
            self.label_116.setText(str(data.get('parameter4', '')))  # 使用get方法提供默认值
        elif table_name == "factory1_1_set_data_curve":
            self.label_117.setText(str(data.get('parameter1', '')))
            self.label_118.setText(str(data.get('parameter2', '')))
            self.label_114.setText(str(data.get('parameter3', '')))
            self.label_115.setText(str(data.get('parameter4', '')))
            self.label_121.setText(str(data.get('parameter5', '')))
            self.label_122.setText(str(data.get('parameter6', '')))  # 使用get方法提供默认值
    def show_dialog_pop_parameter(self):
        """隐藏当前历史数据窗口，显示实时参数弹窗的方法"""
        self.hide()  # 隐藏当前窗口
        # 检查实时参数弹窗是否已存在
        if self.dialog_realtime:
            # 如果弹窗已最小化或隐藏，则恢复显示
            if self.dialog_realtime.isMinimized():
                self.dialog_realtime.showNormal()  # 从最小化状态恢复
            elif not self.dialog_realtime.isVisible():
                self.dialog_realtime.show()  # 如果不可见则显示
            # 如果已经可见，则将其置于前台
            self.dialog_realtime.activateWindow()  # 激活窗口（置于前台）
            self.dialog_realtime.raise_()  # 提升窗口层级

    def center_dialog(self):
        """将弹窗居中显示的方法"""
        # 获取主屏幕尺寸
        screen = QApplication.primaryScreen().geometry()
        # 计算居中坐标（屏幕宽度-窗口宽度）/2
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        # 移动窗口到计算位置
        self.move(x, y)

    def dialog_mouse_press(self, event):
        """处理鼠标按下事件（用于窗口拖动）"""
        # 判断点击位置是否在标题栏区域内
        point_in_title = self.widget_historical_title.rect().contains(event.pos())
        # 当左键点击且位置在标题栏时
        if event.button() == Qt.LeftButton and point_in_title:
            # 记录全局鼠标位置（屏幕坐标系）
            self.drag_start_pos = event.globalPos()
            # 保存窗口当前位置
            self.dialog_original_pos = self.pos()
            # 接受事件，阻止事件传递
            event.accept()
        else:
            # 忽略非标题栏区域的点击
            event.ignore()

    def dialog_mouse_move(self, event):
        """处理鼠标移动事件（实现窗口拖动）"""
        # 当满足三个条件时处理拖动：
        # 1. 左键保持按下状态
        # 2. 存在初始拖动位置记录
        # 3. 鼠标在标题栏区域
        if (event.buttons() & Qt.LeftButton and
                hasattr(self, 'drag_start_pos') and
                self.widget_historical_title.rect().contains(event.pos())):

            # 计算位置偏移量（当前鼠标位置 - 起始位置）
            delta = event.globalPos() - self.drag_start_pos
            # 移动窗口到新位置（原始位置 + 偏移量）
            self.move(self.dialog_original_pos + delta)
            # 接受事件，确保操作流畅
            event.accept()
        else:
            # 忽略无效拖动操作
            event.ignore()

    # 历史参数弹窗类新增关闭事件处理
    # 重写窗口关闭事件处理方法（当窗口被关闭时自动触发）
    def closeEvent(self, event):
        """处理关闭事件：关闭关联的实时参数弹窗"""
        # 检查是否存在实时参数弹窗实例
        if self.dialog_realtime:  # 判断dialog_realtime是否已初始化
            self.dialog_realtime.close()  # 调用实时弹窗的关闭方法
        super().closeEvent(event)  # 调用父类QDialog的关闭事件处理，确保正常关闭流程

class HistoricalParameterDialogFactory1Device2(QDialog, Ui_Dialog_Pop_Historical_Parameter_Factory1Device2):
    def __init__(self):
        # 调用父类构造方法
        super().__init__()
        # 初始化UI界面
        self.threads = {}
        self.setWindowFlags(Qt.FramelessWindowHint)  # 设置无边框窗口样式（隐藏标题栏和边框）
        self.setAttribute(Qt.WA_TranslucentBackground)  # 启用透明背景属性（实现半透明/异形窗口效果）
        self.setupUi(self)

        self.dialog_realtime = None  # 定义创建用于存储历史数据曲线弹窗的实例
        self.pushButton_realtime.clicked.connect(self.show_dialog_pop_parameter)  # 连接按钮点击信号

        # 初始化位置记录变量
        self.dialog_original_pos = None  # 窗口原始位置
        self.drag_start_pos = None  # 鼠标拖动起始位置
        # 绑定鼠标事件到自身方法
        self.mousePressEvent = self.dialog_mouse_press  # 按下事件处理
        self.mouseMoveEvent = self.dialog_mouse_move  # 移动事件处理
        # 设置窗口居中属性
        self.center_dialog()  # 初始居中显示
        self.dateTimeEdit.setDateTime(datetime.now())
        # 连接查询按钮
        self.pushButton_historical_query.clicked.connect(self.handle_historical_query)
        # 初始化历史曲线
        self._init_historical_curves()

    def _init_historical_curves(self):
        """初始化历史曲线组件"""
        # 管径历史曲线 (创建历史曲线绘制组件)
        self.hist_curve1 = HistoricalCurvePlotter(
            self.widget_pop_historical_parameter_curve1,  # 指定父容器控件
            "factory1_2_set_data_curve",  # 对应的数据库表名
            {'curve1': {'field': 'parameter1', 'color': '#FF0000'},
                        'curve2': {'field': 'parameter2', 'color': '#FFFF00'},
                        'curve3': {'field': 'parameter3', 'color': '#00FFFF'},
                        'curve4': {'field': 'parameter4', 'color': '#00FF00'},
                        'curve5': {'field': 'parameter5', 'color': '#FFFF00'},
                        'curve6': {'field': 'parameter6', 'color': '#FF0000'}
             },  # 曲线参数映射配置
            (-1, 1)  # Y轴显示范围
        )

        # 挤出机历史曲线 (第二组历史曲线)
        self.hist_curve2 = HistoricalCurvePlotter(
            self.widget_pop_historical_parameter_curve2,  # 第二个曲线容器的父控件
            "factory1_2_realtime_data_jcj",  # 挤出机实时数据表
            {'curve1': {'field': 'parameter3', 'color': '#FF0000'},
             'curve2': {'field': 'parameter4', 'color': '#FFFF00'},
             'curve3': {'field': 'parameter5', 'color': '#00FFFF'},
             'curve4': {'field': 'parameter6', 'color': '#00FF00'},
             'curve5': {'field': 'parameter9', 'color': '#FFAA00'},
             'curve6': {'field': 'parameter10', 'color': '#FF55FF'}
             },  # 参数映射关系
            (0, 200)  # Y轴最大范围200
        )

    def handle_historical_query(self):
        """处理历史查询按钮点击事件的核心方法"""
        # 获取界面选择的时间（转换为Python datetime对象）
        query_time = self.dateTimeEdit.dateTime().toPyDateTime()
        # 计算结束时间（格式化成SQL可识别的字符串）
        end_time = query_time.strftime("%Y-%m-%d %H:%M:%S")
        # 计算起始时间（当前查询时间前推10分钟）
        start_time = (query_time - timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")
        # 更新两条历史曲线（触发重绘）
        self.hist_curve1.update_plot(start_time, end_time)  # 更新管径曲线
        self.hist_curve2.update_plot(start_time, end_time)  # 更新挤出机曲线

        # 更新参数显示（精确到秒的查询）
        self._update_parameters(
        query_time.strftime("%Y-%m-%d %H:%M:%S"),
        start_time,
        end_time)

    def _update_parameters(self, exact_time, start_time, end_time):
        """更新指定时间点的参数显示
        Args:
            exact_time: 精确时间字符串（格式：YYYY-MM-DD HH:MM:SS）
        """
        # 定义需要查询的数据表列表
        tables = ["factory1_2_realtime_data_jcj", "factory1_2_realtime_data_fjj", "factory1_2_realtime_data_zdj" , "factory1_2_set_data_curve",
                  "factory1_2_set_data_jcj", "factory1_2_set_data_fjj", "factory1_2_set_data_zdj"]

        # 创建线程对象
        thread = QThread()
        # 创建工作线程实例
        worker = HistoricalDataQueryWorker(tables, exact_time, start_time, end_time)

        # 将工作对象移动到新线程
        worker.moveToThread(thread)

        # 信号连接
        thread.started.connect(worker.run)  # type: ignore[attr-defined]
        worker.finished.connect(thread.quit)    # type: ignore[attr-defined]
        worker.finished.connect(worker.deleteLater)# type: ignore[attr-defined]
        thread.finished.connect(thread.deleteLater)# type: ignore[attr-defined]

        # 连接数据更新信号到处理方法
        worker.data_ready.connect(self._handle_historical_data)# type: ignore[attr-defined]

        # 存储线程引用
        self.threads['historical_query'] = (thread, worker)

        # 启动线程
        thread.start()
    def _handle_historical_data(self, result_data):
        """处理从子线程接收到的历史数据
        Args:
            result_data: 包含表名和数据的字典 {table_name: data}
        """
        # 遍历所有返回的数据
        for table_name, data in result_data.items():
            # 如果有返回数据（即使只有一条）
            if data:
                # 更新界面标签（取第一条/唯一一条数据）
                self._update_ui_labels(table_name, data)

    def _update_ui_labels(self, table_name, data):
        """根据数据表名更新对应的UI标签
        Args:
            table_name: 数据表名称（用于分支判断）
            data: 单条历史数据记录（字典格式）
        """
        # 挤出机实时数据表处理分支
        if table_name == "factory1_2_realtime_data_jcj":
            # 更新参数1显示（label_10标签）
            self.label_10.setText(str(data.get('parameter1', '')))  # 使用空字符串作为默认值
            # 更新参数2显示（label_14标签）
            self.label_14.setText(str(data.get('parameter2', '')))
            self.label_18.setText(str(data.get('parameter3', '')))
            self.label_22.setText(str(data.get('parameter4', '')))
            self.label_26.setText(str(data.get('parameter5', '')))
            self.label_30.setText(str(data.get('parameter6', '')))
            self.label_34.setText(str(data.get('parameter7', '')))
            self.label_38.setText(str(data.get('parameter8', '')))
            self.label_42.setText(str(data.get('parameter9', '')))
            self.label_46.setText(str(data.get('parameter10', '')))
            self.label_50.setText(str(data.get('parameter11', '')))
            self.label_123.setText(str(data.get('parameter3', '')))
            self.label_127.setText(str(data.get('parameter4', '')))
            self.label_125.setText(str(data.get('parameter5', '')))
            self.label_126.setText(str(data.get('parameter6', '')))
            self.label_128.setText(str(data.get('parameter9', '')))
            self.label_124.setText(str(data.get('parameter10', '')))  # 使用get方法提供默认值
        # 放卷机实时数据表处理分支
        elif table_name == "factory1_2_realtime_data_fjj":
            # 更新参数12显示（label_53标签）
            self.label_53.setText(str(data.get('parameter12', '')))
            self.label_57.setText(str(data.get('parameter13', '')))
            self.label_61.setText(str(data.get('parameter14', '')))
            self.label_65.setText(str(data.get('parameter15', '')))  # 使用get方法提供默认值
        # 自动机历史数据表处理分支
        elif table_name == "factory1_2_realtime_data_zdj":
            self.label_73.setText(str(data.get('parameter16', '')))
            self.label_77.setText(str(data.get('parameter17', '')))
            self.label_81.setText(str(data.get('parameter18', '')))
            self.label_85.setText(str(data.get('parameter19', '')))
            self.label_89.setText(str(data.get('parameter20', '')))
            self.label_93.setText(str(data.get('parameter21', '')))  # 使用get方法提供默认值
        elif table_name == "factory1_2_set_data_jcj":
            self.label_104.setText(str(data.get('parameter1', '')))
            self.label_105.setText(str(data.get('parameter2', '')))
            self.label_106.setText(str(data.get('parameter3', '')))
            self.label_107.setText(str(data.get('parameter4', '')))
            self.label_108.setText(str(data.get('parameter5', '')))
            self.label_115.setText(str(data.get('parameter6', '')))  # 使用get方法提供默认值
        elif table_name == "factory1_2_set_data_fjj":
            self.label_109.setText(str(data.get('parameter1', '')))
            self.label_110.setText(str(data.get('parameter2', '')))
            self.label_111.setText(str(data.get('parameter3', '')))  # 使用get方法提供默认值
        elif table_name == "factory1_2_set_data_zdj":
            self.label_112.setText(str(data.get('parameter1', '')))
            self.label_113.setText(str(data.get('parameter2', '')))
            self.label_114.setText(str(data.get('parameter3', '')))
            self.label_116.setText(str(data.get('parameter4', '')))  # 使用get方法提供默认值
        elif table_name == "factory1_2_set_data_curve":
            self.label_117.setText(str(data.get('parameter1', '')))
            self.label_118.setText(str(data.get('parameter2', '')))
            self.label_114.setText(str(data.get('parameter3', '')))
            self.label_115.setText(str(data.get('parameter4', '')))
            self.label_121.setText(str(data.get('parameter5', '')))
            self.label_122.setText(str(data.get('parameter6', '')))  # 使用get方法提供默认值
    def show_dialog_pop_parameter(self):
        """隐藏当前历史数据窗口，显示实时参数弹窗的方法"""
        self.hide()  # 隐藏当前窗口
        # 检查实时参数弹窗是否已存在
        if self.dialog_realtime:
            # 如果弹窗已最小化或隐藏，则恢复显示
            if self.dialog_realtime.isMinimized():
                self.dialog_realtime.showNormal()  # 从最小化状态恢复
            elif not self.dialog_realtime.isVisible():
                self.dialog_realtime.show()  # 如果不可见则显示
            # 如果已经可见，则将其置于前台
            self.dialog_realtime.activateWindow()  # 激活窗口（置于前台）
            self.dialog_realtime.raise_()  # 提升窗口层级

    def center_dialog(self):
        """将弹窗居中显示的方法"""
        # 获取主屏幕尺寸
        screen = QApplication.primaryScreen().geometry()
        # 计算居中坐标（屏幕宽度-窗口宽度）/2
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        # 移动窗口到计算位置
        self.move(x, y)

    def dialog_mouse_press(self, event):
        """处理鼠标按下事件（用于窗口拖动）"""
        # 判断点击位置是否在标题栏区域内
        point_in_title = self.widget_historical_title.rect().contains(event.pos())
        # 当左键点击且位置在标题栏时
        if event.button() == Qt.LeftButton and point_in_title:
            # 记录全局鼠标位置（屏幕坐标系）
            self.drag_start_pos = event.globalPos()
            # 保存窗口当前位置
            self.dialog_original_pos = self.pos()
            # 接受事件，阻止事件传递
            event.accept()
        else:
            # 忽略非标题栏区域的点击
            event.ignore()

    def dialog_mouse_move(self, event):
        """处理鼠标移动事件（实现窗口拖动）"""
        # 当满足三个条件时处理拖动：
        # 1. 左键保持按下状态
        # 2. 存在初始拖动位置记录
        # 3. 鼠标在标题栏区域
        if (event.buttons() & Qt.LeftButton and
                hasattr(self, 'drag_start_pos') and
                self.widget_historical_title.rect().contains(event.pos())):

            # 计算位置偏移量（当前鼠标位置 - 起始位置）
            delta = event.globalPos() - self.drag_start_pos
            # 移动窗口到新位置（原始位置 + 偏移量）
            self.move(self.dialog_original_pos + delta)
            # 接受事件，确保操作流畅
            event.accept()
        else:
            # 忽略无效拖动操作
            event.ignore()

    # 历史参数弹窗类新增关闭事件处理
    # 重写窗口关闭事件处理方法（当窗口被关闭时自动触发）
    def closeEvent(self, event):
        """处理关闭事件：关闭关联的实时参数弹窗"""
        # 检查是否存在实时参数弹窗实例
        if self.dialog_realtime:  # 判断dialog_realtime是否已初始化
            self.dialog_realtime.close()  # 调用实时弹窗的关闭方法
        super().closeEvent(event)  # 调用父类QDialog的关闭事件处理，确保正常关闭流程

class HistoricalParameterDialogFactory1Device3(QDialog, Ui_Dialog_Pop_Historical_Parameter_Factory1Device3):
    def __init__(self):
        # 调用父类构造方法
        super().__init__()
        # 初始化UI界面
        self.threads = {}
        self.setWindowFlags(Qt.FramelessWindowHint)  # 设置无边框窗口样式（隐藏标题栏和边框）
        self.setAttribute(Qt.WA_TranslucentBackground)  # 启用透明背景属性（实现半透明/异形窗口效果）
        self.setupUi(self)

        self.dialog_realtime = None  # 定义创建用于存储历史数据曲线弹窗的实例
        self.pushButton_realtime.clicked.connect(self.show_dialog_pop_parameter)  # 连接按钮点击信号

        # 初始化位置记录变量
        self.dialog_original_pos = None  # 窗口原始位置
        self.drag_start_pos = None  # 鼠标拖动起始位置
        # 绑定鼠标事件到自身方法
        self.mousePressEvent = self.dialog_mouse_press  # 按下事件处理
        self.mouseMoveEvent = self.dialog_mouse_move  # 移动事件处理
        # 设置窗口居中属性
        self.center_dialog()  # 初始居中显示
        self.dateTimeEdit.setDateTime(datetime.now())
        # 连接查询按钮
        self.pushButton_historical_query.clicked.connect(self.handle_historical_query)
        # 初始化历史曲线
        self._init_historical_curves()

    def _init_historical_curves(self):
        """初始化历史曲线组件"""
        # 管径历史曲线 (创建历史曲线绘制组件)
        self.hist_curve1 = HistoricalCurvePlotter(
            self.widget_pop_historical_parameter_curve1,  # 指定父容器控件
            "factory1_3_set_data_curve",  # 对应的数据库表名
            {'curve1': {'field': 'parameter1', 'color': '#FF0000'},
                        'curve2': {'field': 'parameter2', 'color': '#FFFF00'},
                        'curve3': {'field': 'parameter3', 'color': '#00FFFF'},
                        'curve4': {'field': 'parameter4', 'color': '#00FF00'},
                        'curve5': {'field': 'parameter5', 'color': '#FFFF00'},
                        'curve6': {'field': 'parameter6', 'color': '#FF0000'}
             },  # 曲线参数映射配置
            (-1, 1)  # Y轴显示范围
        )

        # 挤出机历史曲线 (第二组历史曲线)
        self.hist_curve2 = HistoricalCurvePlotter(
            self.widget_pop_historical_parameter_curve2,  # 第二个曲线容器的父控件
            "factory1_3_realtime_data_jcj",  # 挤出机实时数据表
            {'curve1': {'field': 'parameter3', 'color': '#FF0000'},
             'curve2': {'field': 'parameter4', 'color': '#FFFF00'},
             'curve3': {'field': 'parameter5', 'color': '#00FFFF'},
             'curve4': {'field': 'parameter6', 'color': '#00FF00'},
             'curve5': {'field': 'parameter9', 'color': '#FFAA00'},
             'curve6': {'field': 'parameter10', 'color': '#FF55FF'}
             },  # 参数映射关系
            (0, 200)  # Y轴最大范围200
        )

    def handle_historical_query(self):
        """处理历史查询按钮点击事件的核心方法"""
        # 获取界面选择的时间（转换为Python datetime对象）
        query_time = self.dateTimeEdit.dateTime().toPyDateTime()
        # 计算结束时间（格式化成SQL可识别的字符串）
        end_time = query_time.strftime("%Y-%m-%d %H:%M:%S")
        # 计算起始时间（当前查询时间前推10分钟）
        start_time = (query_time - timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")
        # 更新两条历史曲线（触发重绘）
        self.hist_curve1.update_plot(start_time, end_time)  # 更新管径曲线
        self.hist_curve2.update_plot(start_time, end_time)  # 更新挤出机曲线

        # 更新参数显示（精确到秒的查询）
        self._update_parameters(
        query_time.strftime("%Y-%m-%d %H:%M:%S"),
        start_time,
        end_time)

    def _update_parameters(self, exact_time, start_time, end_time):
        """更新指定时间点的参数显示
        Args:
            exact_time: 精确时间字符串（格式：YYYY-MM-DD HH:MM:SS）
        """
        # 定义需要查询的数据表列表
        tables = ["factory1_3_realtime_data_jcj", "factory1_3_realtime_data_fjj", "factory1_3_realtime_data_zdj" , "factory1_3_set_data_curve",
                  "factory1_3_set_data_jcj", "factory1_3_set_data_fjj", "factory1_3_set_data_zdj"]

        # 创建线程对象
        thread = QThread()
        # 创建工作线程实例
        worker = HistoricalDataQueryWorker(tables, exact_time, start_time, end_time)

        # 将工作对象移动到新线程
        worker.moveToThread(thread)

        # 信号连接
        thread.started.connect(worker.run)  # type: ignore[attr-defined]
        worker.finished.connect(thread.quit)  # type: ignore[attr-defined]
        worker.finished.connect(worker.deleteLater)  # type: ignore[attr-defined]
        thread.finished.connect(thread.deleteLater)  # type: ignore[attr-defined]

        # 连接数据更新信号到处理方法
        worker.data_ready.connect(self._handle_historical_data)  # type: ignore[attr-defined]

        # 存储线程引用
        self.threads['historical_query'] = (thread, worker)

        # 启动线程
        thread.start()

    def _handle_historical_data(self, result_data):
        """处理从子线程接收到的历史数据
        Args:
            result_data: 包含表名和数据的字典 {table_name: data}
        """
        # 遍历所有返回的数据
        for table_name, data in result_data.items():
            # 如果有返回数据（即使只有一条）
            if data:
                # 更新界面标签（取第一条/唯一一条数据）
                self._update_ui_labels(table_name, data)

    def _update_ui_labels(self, table_name, data):
        """根据数据表名更新对应的UI标签
        Args:
            table_name: 数据表名称（用于分支判断）
            data: 单条历史数据记录（字典格式）
        """
        # 挤出机实时数据表处理分支
        if table_name == "factory1_3_realtime_data_jcj":
            # 更新参数1显示（label_10标签）
            self.label_10.setText(str(data.get('parameter1', '')))  # 使用空字符串作为默认值
            # 更新参数2显示（label_14标签）
            self.label_14.setText(str(data.get('parameter2', '')))
            self.label_18.setText(str(data.get('parameter3', '')))
            self.label_22.setText(str(data.get('parameter4', '')))
            self.label_26.setText(str(data.get('parameter5', '')))
            self.label_30.setText(str(data.get('parameter6', '')))
            self.label_34.setText(str(data.get('parameter7', '')))
            self.label_38.setText(str(data.get('parameter8', '')))
            self.label_42.setText(str(data.get('parameter9', '')))
            self.label_46.setText(str(data.get('parameter10', '')))
            self.label_50.setText(str(data.get('parameter11', '')))
            self.label_123.setText(str(data.get('parameter3', '')))
            self.label_127.setText(str(data.get('parameter4', '')))
            self.label_125.setText(str(data.get('parameter5', '')))
            self.label_126.setText(str(data.get('parameter6', '')))
            self.label_128.setText(str(data.get('parameter9', '')))
            self.label_124.setText(str(data.get('parameter10', '')))  # 使用get方法提供默认值
        # 放卷机实时数据表处理分支
        elif table_name == "factory1_3_realtime_data_fjj":
            # 更新参数12显示（label_53标签）
            self.label_53.setText(str(data.get('parameter12', '')))
            self.label_57.setText(str(data.get('parameter13', '')))
            self.label_61.setText(str(data.get('parameter14', '')))
            self.label_65.setText(str(data.get('parameter15', '')))  # 使用get方法提供默认值
        # 自动机历史数据表处理分支
        elif table_name == "factory1_3_realtime_data_zdj":
            self.label_73.setText(str(data.get('parameter16', '')))
            self.label_77.setText(str(data.get('parameter17', '')))
            self.label_81.setText(str(data.get('parameter18', '')))
            self.label_85.setText(str(data.get('parameter19', '')))
            self.label_89.setText(str(data.get('parameter20', '')))
            self.label_93.setText(str(data.get('parameter21', '')))  # 使用get方法提供默认值
        elif table_name == "factory1_3_set_data_jcj":
            self.label_104.setText(str(data.get('parameter1', '')))
            self.label_105.setText(str(data.get('parameter2', '')))
            self.label_106.setText(str(data.get('parameter3', '')))
            self.label_107.setText(str(data.get('parameter4', '')))
            self.label_108.setText(str(data.get('parameter5', '')))
            self.label_115.setText(str(data.get('parameter6', '')))  # 使用get方法提供默认值
        elif table_name == "factory1_3_set_data_fjj":
            self.label_109.setText(str(data.get('parameter1', '')))
            self.label_110.setText(str(data.get('parameter2', '')))
            self.label_111.setText(str(data.get('parameter3', '')))  # 使用get方法提供默认值
        elif table_name == "factory1_3_set_data_zdj":
            self.label_112.setText(str(data.get('parameter1', '')))
            self.label_113.setText(str(data.get('parameter2', '')))
            self.label_114.setText(str(data.get('parameter3', '')))
            self.label_116.setText(str(data.get('parameter4', '')))  # 使用get方法提供默认值
        elif table_name == "factory1_3_set_data_curve":
            self.label_117.setText(str(data.get('parameter1', '')))
            self.label_118.setText(str(data.get('parameter2', '')))
            self.label_114.setText(str(data.get('parameter3', '')))
            self.label_115.setText(str(data.get('parameter4', '')))
            self.label_121.setText(str(data.get('parameter5', '')))
            self.label_122.setText(str(data.get('parameter6', '')))  # 使用get方法提供默认值
    def show_dialog_pop_parameter(self):
        """隐藏当前历史数据窗口，显示实时参数弹窗的方法"""
        self.hide()  # 隐藏当前窗口
        # 检查实时参数弹窗是否已存在
        if self.dialog_realtime:
            # 如果弹窗已最小化或隐藏，则恢复显示
            if self.dialog_realtime.isMinimized():
                self.dialog_realtime.showNormal()  # 从最小化状态恢复
            elif not self.dialog_realtime.isVisible():
                self.dialog_realtime.show()  # 如果不可见则显示
            # 如果已经可见，则将其置于前台
            self.dialog_realtime.activateWindow()  # 激活窗口（置于前台）
            self.dialog_realtime.raise_()  # 提升窗口层级

    def center_dialog(self):
        """将弹窗居中显示的方法"""
        # 获取主屏幕尺寸
        screen = QApplication.primaryScreen().geometry()
        # 计算居中坐标（屏幕宽度-窗口宽度）/2
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        # 移动窗口到计算位置
        self.move(x, y)

    def dialog_mouse_press(self, event):
        """处理鼠标按下事件（用于窗口拖动）"""
        # 判断点击位置是否在标题栏区域内
        point_in_title = self.widget_historical_title.rect().contains(event.pos())
        # 当左键点击且位置在标题栏时
        if event.button() == Qt.LeftButton and point_in_title:
            # 记录全局鼠标位置（屏幕坐标系）
            self.drag_start_pos = event.globalPos()
            # 保存窗口当前位置
            self.dialog_original_pos = self.pos()
            # 接受事件，阻止事件传递
            event.accept()
        else:
            # 忽略非标题栏区域的点击
            event.ignore()

    def dialog_mouse_move(self, event):
        """处理鼠标移动事件（实现窗口拖动）"""
        # 当满足三个条件时处理拖动：
        # 1. 左键保持按下状态
        # 2. 存在初始拖动位置记录
        # 3. 鼠标在标题栏区域
        if (event.buttons() & Qt.LeftButton and
                hasattr(self, 'drag_start_pos') and
                self.widget_historical_title.rect().contains(event.pos())):

            # 计算位置偏移量（当前鼠标位置 - 起始位置）
            delta = event.globalPos() - self.drag_start_pos
            # 移动窗口到新位置（原始位置 + 偏移量）
            self.move(self.dialog_original_pos + delta)
            # 接受事件，确保操作流畅
            event.accept()
        else:
            # 忽略无效拖动操作
            event.ignore()

    # 历史参数弹窗类新增关闭事件处理
    # 重写窗口关闭事件处理方法（当窗口被关闭时自动触发）
    def closeEvent(self, event):
        """处理关闭事件：关闭关联的实时参数弹窗"""
        # 检查是否存在实时参数弹窗实例
        if self.dialog_realtime:  # 判断dialog_realtime是否已初始化
            self.dialog_realtime.close()  # 调用实时弹窗的关闭方法
        super().closeEvent(event)  # 调用父类QDialog的关闭事件处理，确保正常关闭流程

class HistoricalParameterDialogFactory1Device4(QDialog, Ui_Dialog_Pop_Historical_Parameter_Factory1Device4):
    def __init__(self):
        # 调用父类构造方法
        super().__init__()
        # 初始化UI界面
        self.threads = {}
        self.setWindowFlags(Qt.FramelessWindowHint)  # 设置无边框窗口样式（隐藏标题栏和边框）
        self.setAttribute(Qt.WA_TranslucentBackground)  # 启用透明背景属性（实现半透明/异形窗口效果）
        self.setupUi(self)

        self.dialog_realtime = None  # 定义创建用于存储历史数据曲线弹窗的实例
        self.pushButton_realtime.clicked.connect(self.show_dialog_pop_parameter)  # 连接按钮点击信号

        # 初始化位置记录变量
        self.dialog_original_pos = None  # 窗口原始位置
        self.drag_start_pos = None  # 鼠标拖动起始位置
        # 绑定鼠标事件到自身方法
        self.mousePressEvent = self.dialog_mouse_press  # 按下事件处理
        self.mouseMoveEvent = self.dialog_mouse_move  # 移动事件处理
        # 设置窗口居中属性
        self.center_dialog()  # 初始居中显示
        self.dateTimeEdit.setDateTime(datetime.now())
        # 连接查询按钮
        self.pushButton_historical_query.clicked.connect(self.handle_historical_query)
        # 初始化历史曲线
        self._init_historical_curves()

    def _init_historical_curves(self):
        """初始化历史曲线组件"""
        # 管径历史曲线 (创建历史曲线绘制组件)
        self.hist_curve1 = HistoricalCurvePlotter(
            self.widget_pop_historical_parameter_curve1,  # 指定父容器控件
            "factory1_4_set_data_curve",  # 对应的数据库表名
            {'curve1': {'field': 'parameter1', 'color': '#FF0000'},
                        'curve2': {'field': 'parameter2', 'color': '#FFFF00'},
                        'curve3': {'field': 'parameter3', 'color': '#00FFFF'},
                        'curve4': {'field': 'parameter4', 'color': '#00FF00'},
                        'curve5': {'field': 'parameter5', 'color': '#FFFF00'},
                        'curve6': {'field': 'parameter6', 'color': '#FF0000'}
             },  # 曲线参数映射配置
            (-1, 1)  # Y轴显示范围
        )

        # 挤出机历史曲线 (第二组历史曲线)
        self.hist_curve2 = HistoricalCurvePlotter(
            self.widget_pop_historical_parameter_curve2,  # 第二个曲线容器的父控件
            "factory1_4_realtime_data_jcj",  # 挤出机实时数据表
            {'curve1': {'field': 'parameter3', 'color': '#FF0000'},
             'curve2': {'field': 'parameter4', 'color': '#FFFF00'},
             'curve3': {'field': 'parameter5', 'color': '#00FFFF'},
             'curve4': {'field': 'parameter6', 'color': '#00FF00'},
             'curve5': {'field': 'parameter9', 'color': '#FFAA00'},
             'curve6': {'field': 'parameter10', 'color': '#FF55FF'}
             },  # 参数映射关系
            (0, 200)  # Y轴最大范围200
        )

    def handle_historical_query(self):
        """处理历史查询按钮点击事件的核心方法"""
        # 获取界面选择的时间（转换为Python datetime对象）
        query_time = self.dateTimeEdit.dateTime().toPyDateTime()
        # 计算结束时间（格式化成SQL可识别的字符串）
        end_time = query_time.strftime("%Y-%m-%d %H:%M:%S")
        # 计算起始时间（当前查询时间前推10分钟）
        start_time = (query_time - timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")
        # 更新两条历史曲线（触发重绘）
        self.hist_curve1.update_plot(start_time, end_time)  # 更新管径曲线
        self.hist_curve2.update_plot(start_time, end_time)  # 更新挤出机曲线

        # 更新参数显示（精确到秒的查询）
        self._update_parameters(
        query_time.strftime("%Y-%m-%d %H:%M:%S"),
        start_time,
        end_time)

    def _update_parameters(self, exact_time, start_time, end_time):
        """更新指定时间点的参数显示
        Args:
            exact_time: 精确时间字符串（格式：YYYY-MM-DD HH:MM:SS）
        """
        # 定义需要查询的数据表列表
        tables = ["factory1_4_realtime_data_jcj", "factory1_4_realtime_data_fjj", "factory1_4_realtime_data_zdj" , "factory1_4_set_data_curve",
                  "factory1_4_set_data_jcj", "factory1_4_set_data_fjj", "factory1_4_set_data_zdj"]

        # 创建线程对象
        thread = QThread()
        # 创建工作线程实例
        worker = HistoricalDataQueryWorker(tables, exact_time, start_time, end_time)

        # 将工作对象移动到新线程
        worker.moveToThread(thread)

        # 信号连接
        thread.started.connect(worker.run)  # type: ignore[attr-defined]
        worker.finished.connect(thread.quit)  # type: ignore[attr-defined]
        worker.finished.connect(worker.deleteLater)  # type: ignore[attr-defined]
        thread.finished.connect(thread.deleteLater)  # type: ignore[attr-defined]

        # 连接数据更新信号到处理方法
        worker.data_ready.connect(self._handle_historical_data)  # type: ignore[attr-defined]

        # 存储线程引用
        self.threads['historical_query'] = (thread, worker)

        # 启动线程
        thread.start()

    def _handle_historical_data(self, result_data):
        """处理从子线程接收到的历史数据
        Args:
            result_data: 包含表名和数据的字典 {table_name: data}
        """
        # 遍历所有返回的数据
        for table_name, data in result_data.items():
            # 如果有返回数据（即使只有一条）
            if data:
                # 更新界面标签（取第一条/唯一一条数据）
                self._update_ui_labels(table_name, data)

    def _update_ui_labels(self, table_name, data):
        """根据数据表名更新对应的UI标签
        Args:
            table_name: 数据表名称（用于分支判断）
            data: 单条历史数据记录（字典格式）
        """
        # 挤出机实时数据表处理分支
        if table_name == "factory1_4_realtime_data_jcj":
            # 更新参数1显示（label_10标签）
            self.label_10.setText(str(data.get('parameter1', '')))  # 使用空字符串作为默认值
            # 更新参数2显示（label_14标签）
            self.label_14.setText(str(data.get('parameter2', '')))
            self.label_18.setText(str(data.get('parameter3', '')))
            self.label_22.setText(str(data.get('parameter4', '')))
            self.label_26.setText(str(data.get('parameter5', '')))
            self.label_30.setText(str(data.get('parameter6', '')))
            self.label_34.setText(str(data.get('parameter7', '')))
            self.label_38.setText(str(data.get('parameter8', '')))
            self.label_42.setText(str(data.get('parameter9', '')))
            self.label_46.setText(str(data.get('parameter10', '')))
            self.label_50.setText(str(data.get('parameter11', '')))
            self.label_123.setText(str(data.get('parameter3', '')))
            self.label_127.setText(str(data.get('parameter4', '')))
            self.label_125.setText(str(data.get('parameter5', '')))
            self.label_126.setText(str(data.get('parameter6', '')))
            self.label_128.setText(str(data.get('parameter9', '')))
            self.label_124.setText(str(data.get('parameter10', '')))  # 使用get方法提供默认值
        # 放卷机实时数据表处理分支
        elif table_name == "factory1_4_realtime_data_fjj":
            # 更新参数12显示（label_53标签）
            self.label_53.setText(str(data.get('parameter12', '')))
            self.label_57.setText(str(data.get('parameter13', '')))
            self.label_61.setText(str(data.get('parameter14', '')))
            self.label_65.setText(str(data.get('parameter15', '')))  # 使用get方法提供默认值
        # 自动机历史数据表处理分支
        elif table_name == "factory1_4_realtime_data_zdj":
            self.label_73.setText(str(data.get('parameter16', '')))
            self.label_77.setText(str(data.get('parameter17', '')))
            self.label_81.setText(str(data.get('parameter18', '')))
            self.label_85.setText(str(data.get('parameter19', '')))
            self.label_89.setText(str(data.get('parameter20', '')))
            self.label_93.setText(str(data.get('parameter21', '')))  # 使用get方法提供默认值
        elif table_name == "factory1_4_set_data_jcj":
            self.label_104.setText(str(data.get('parameter1', '')))
            self.label_105.setText(str(data.get('parameter2', '')))
            self.label_106.setText(str(data.get('parameter3', '')))
            self.label_107.setText(str(data.get('parameter4', '')))
            self.label_108.setText(str(data.get('parameter5', '')))
            self.label_115.setText(str(data.get('parameter6', '')))  # 使用get方法提供默认值
        elif table_name == "factory1_4_set_data_fjj":
            self.label_109.setText(str(data.get('parameter1', '')))
            self.label_110.setText(str(data.get('parameter2', '')))
            self.label_111.setText(str(data.get('parameter3', '')))  # 使用get方法提供默认值
        elif table_name == "factory1_4_set_data_zdj":
            self.label_112.setText(str(data.get('parameter1', '')))
            self.label_113.setText(str(data.get('parameter2', '')))
            self.label_114.setText(str(data.get('parameter3', '')))
            self.label_116.setText(str(data.get('parameter4', '')))  # 使用get方法提供默认值
        elif table_name == "factory1_4_set_data_curve":
            self.label_117.setText(str(data.get('parameter1', '')))
            self.label_118.setText(str(data.get('parameter2', '')))
            self.label_114.setText(str(data.get('parameter3', '')))
            self.label_115.setText(str(data.get('parameter4', '')))
            self.label_121.setText(str(data.get('parameter5', '')))
            self.label_122.setText(str(data.get('parameter6', '')))  # 使用get方法提供默认值
    def show_dialog_pop_parameter(self):
        """隐藏当前历史数据窗口，显示实时参数弹窗的方法"""
        self.hide()  # 隐藏当前窗口
        # 检查实时参数弹窗是否已存在
        if self.dialog_realtime:
            # 如果弹窗已最小化或隐藏，则恢复显示
            if self.dialog_realtime.isMinimized():
                self.dialog_realtime.showNormal()  # 从最小化状态恢复
            elif not self.dialog_realtime.isVisible():
                self.dialog_realtime.show()  # 如果不可见则显示
            # 如果已经可见，则将其置于前台
            self.dialog_realtime.activateWindow()  # 激活窗口（置于前台）
            self.dialog_realtime.raise_()  # 提升窗口层级

    def center_dialog(self):
        """将弹窗居中显示的方法"""
        # 获取主屏幕尺寸
        screen = QApplication.primaryScreen().geometry()
        # 计算居中坐标（屏幕宽度-窗口宽度）/2
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        # 移动窗口到计算位置
        self.move(x, y)

    def dialog_mouse_press(self, event):
        """处理鼠标按下事件（用于窗口拖动）"""
        # 判断点击位置是否在标题栏区域内
        point_in_title = self.widget_historical_title.rect().contains(event.pos())
        # 当左键点击且位置在标题栏时
        if event.button() == Qt.LeftButton and point_in_title:
            # 记录全局鼠标位置（屏幕坐标系）
            self.drag_start_pos = event.globalPos()
            # 保存窗口当前位置
            self.dialog_original_pos = self.pos()
            # 接受事件，阻止事件传递
            event.accept()
        else:
            # 忽略非标题栏区域的点击
            event.ignore()

    def dialog_mouse_move(self, event):
        """处理鼠标移动事件（实现窗口拖动）"""
        # 当满足三个条件时处理拖动：
        # 1. 左键保持按下状态
        # 2. 存在初始拖动位置记录
        # 3. 鼠标在标题栏区域
        if (event.buttons() & Qt.LeftButton and
                hasattr(self, 'drag_start_pos') and
                self.widget_historical_title.rect().contains(event.pos())):

            # 计算位置偏移量（当前鼠标位置 - 起始位置）
            delta = event.globalPos() - self.drag_start_pos
            # 移动窗口到新位置（原始位置 + 偏移量）
            self.move(self.dialog_original_pos + delta)
            # 接受事件，确保操作流畅
            event.accept()
        else:
            # 忽略无效拖动操作
            event.ignore()

    # 历史参数弹窗类新增关闭事件处理
    # 重写窗口关闭事件处理方法（当窗口被关闭时自动触发）
    def closeEvent(self, event):
        """处理关闭事件：关闭关联的实时参数弹窗"""
        # 检查是否存在实时参数弹窗实例
        if self.dialog_realtime:  # 判断dialog_realtime是否已初始化
            self.dialog_realtime.close()  # 调用实时弹窗的关闭方法
        super().closeEvent(event)  # 调用父类QDialog的关闭事件处理，确保正常关闭流程

class HistoricalParameterDialogFactory2Device1(QDialog, Ui_Dialog_Pop_Historical_Parameter_Factory2Device1):
    def __init__(self):
        # 调用父类构造方法
        super().__init__()
        # 初始化UI界面
        self.threads = {}
        self.setWindowFlags(Qt.FramelessWindowHint)  # 设置无边框窗口样式（隐藏标题栏和边框）
        self.setAttribute(Qt.WA_TranslucentBackground)  # 启用透明背景属性（实现半透明/异形窗口效果）
        self.setupUi(self)

        self.dialog_realtime = None  # 定义创建用于存储历史数据曲线弹窗的实例
        self.pushButton_realtime.clicked.connect(self.show_dialog_pop_parameter)  # 连接按钮点击信号

        # 初始化位置记录变量
        self.dialog_original_pos = None  # 窗口原始位置
        self.drag_start_pos = None  # 鼠标拖动起始位置
        # 绑定鼠标事件到自身方法
        self.mousePressEvent = self.dialog_mouse_press  # 按下事件处理
        self.mouseMoveEvent = self.dialog_mouse_move  # 移动事件处理
        # 设置窗口居中属性
        self.center_dialog()  # 初始居中显示
        self.dateTimeEdit.setDateTime(datetime.now())
        # 连接查询按钮
        self.pushButton_historical_query.clicked.connect(self.handle_historical_query)
        # 初始化历史曲线
        self._init_historical_curves()

    def _init_historical_curves(self):
        """初始化历史曲线组件"""
        # 管径历史曲线 (创建历史曲线绘制组件)
        self.hist_curve1 = HistoricalCurvePlotter(
            self.widget_pop_historical_parameter_curve1,  # 指定父容器控件
            "factory2_1_set_data_curve",  # 对应的数据库表名
            {'curve1': {'field': 'parameter1', 'color': '#FF0000'},
                        'curve2': {'field': 'parameter2', 'color': '#FFFF00'},
                        'curve3': {'field': 'parameter3', 'color': '#00FFFF'},
                        'curve4': {'field': 'parameter4', 'color': '#00FF00'},
                        'curve5': {'field': 'parameter5', 'color': '#FFFF00'},
                        'curve6': {'field': 'parameter6', 'color': '#FF0000'}
             },  # 曲线参数映射配置
            (-1, 1)  # Y轴显示范围
        )

        # 挤出机历史曲线 (第二组历史曲线)
        self.hist_curve2 = HistoricalCurvePlotter(
            self.widget_pop_historical_parameter_curve2,  # 第二个曲线容器的父控件
            "factory2_1_realtime_data_jcj",  # 挤出机实时数据表
            {'curve1': {'field': 'parameter3', 'color': '#FF0000'},
             'curve2': {'field': 'parameter4', 'color': '#FFFF00'},
             'curve3': {'field': 'parameter5', 'color': '#00FFFF'},
             'curve4': {'field': 'parameter6', 'color': '#00FF00'},
             'curve5': {'field': 'parameter9', 'color': '#FFAA00'},
             'curve6': {'field': 'parameter10', 'color': '#FF55FF'}
             },  # 参数映射关系
            (0, 200)  # Y轴最大范围200
        )

    def handle_historical_query(self):
        """处理历史查询按钮点击事件的核心方法"""
        # 获取界面选择的时间（转换为Python datetime对象）
        query_time = self.dateTimeEdit.dateTime().toPyDateTime()
        # 计算结束时间（格式化成SQL可识别的字符串）
        end_time = query_time.strftime("%Y-%m-%d %H:%M:%S")
        # 计算起始时间（当前查询时间前推10分钟）
        start_time = (query_time - timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")

        # 更新两条历史曲线（触发重绘）
        self.hist_curve1.update_plot(start_time, end_time)  # 更新管径曲线
        self.hist_curve2.update_plot(start_time, end_time)  # 更新挤出机曲线

        # 更新参数显示（精确到秒的查询）
        self._update_parameters(
        query_time.strftime("%Y-%m-%d %H:%M:%S"),
        start_time,
        end_time)

    def _update_parameters(self, exact_time, start_time, end_time):
        """更新指定时间点的参数显示
        Args:
            exact_time: 精确时间字符串（格式：YYYY-MM-DD HH:MM:SS）
        """
        # 定义需要查询的数据表列表
        tables = ["factory2_1_realtime_data_jcj", "factory2_1_realtime_data_fjj", "factory2_1_realtime_data_zdj" , "factory2_1_set_data_curve",
                  "factory2_1_set_data_jcj", "factory2_1_set_data_fjj", "factory2_1_set_data_zdj"]

        # 创建线程对象
        thread = QThread()
        # 创建工作线程实例
        worker = HistoricalDataQueryWorker(tables, exact_time, start_time, end_time)

        # 将工作对象移动到新线程
        worker.moveToThread(thread)

        # 信号连接
        thread.started.connect(worker.run)  # type: ignore[attr-defined]
        worker.finished.connect(thread.quit)  # type: ignore[attr-defined]
        worker.finished.connect(worker.deleteLater)  # type: ignore[attr-defined]
        thread.finished.connect(thread.deleteLater)  # type: ignore[attr-defined]

        # 连接数据更新信号到处理方法
        worker.data_ready.connect(self._handle_historical_data)  # type: ignore[attr-defined]

        # 存储线程引用
        self.threads['historical_query'] = (thread, worker)

        # 启动线程
        thread.start()

    def _handle_historical_data(self, result_data):
        """处理从子线程接收到的历史数据
        Args:
            result_data: 包含表名和数据的字典 {table_name: data}
        """
        # 遍历所有返回的数据
        for table_name, data in result_data.items():
            # 如果有返回数据（即使只有一条）
            if data:
                # 更新界面标签（取第一条/唯一一条数据）
                self._update_ui_labels(table_name, data)

    def _update_ui_labels(self, table_name, data):
        """根据数据表名更新对应的UI标签
        Args:
            table_name: 数据表名称（用于分支判断）
            data: 单条历史数据记录（字典格式）
        """
        # 挤出机实时数据表处理分支
        if table_name == "factory2_1_realtime_data_jcj":
            # 更新参数1显示（label_10标签）
            self.label_10.setText(str(data.get('parameter1', '')))  # 使用空字符串作为默认值
            # 更新参数2显示（label_14标签）
            self.label_14.setText(str(data.get('parameter2', '')))
            self.label_18.setText(str(data.get('parameter3', '')))
            self.label_22.setText(str(data.get('parameter4', '')))
            self.label_26.setText(str(data.get('parameter5', '')))
            self.label_30.setText(str(data.get('parameter6', '')))
            self.label_34.setText(str(data.get('parameter7', '')))
            self.label_38.setText(str(data.get('parameter8', '')))
            self.label_42.setText(str(data.get('parameter9', '')))
            self.label_46.setText(str(data.get('parameter10', '')))
            self.label_50.setText(str(data.get('parameter11', '')))
            self.label_123.setText(str(data.get('parameter3', '')))
            self.label_127.setText(str(data.get('parameter4', '')))
            self.label_125.setText(str(data.get('parameter5', '')))
            self.label_126.setText(str(data.get('parameter6', '')))
            self.label_128.setText(str(data.get('parameter9', '')))
            self.label_124.setText(str(data.get('parameter10', '')))  # 使用get方法提供默认值
        # 放卷机实时数据表处理分支
        elif table_name == "factory2_1_realtime_data_fjj":
            # 更新参数12显示（label_53标签）
            self.label_53.setText(str(data.get('parameter12', '')))
            self.label_57.setText(str(data.get('parameter13', '')))
            self.label_61.setText(str(data.get('parameter14', '')))
            self.label_65.setText(str(data.get('parameter15', '')))  # 使用get方法提供默认值
        # 自动机历史数据表处理分支
        elif table_name == "factory2_1_realtime_data_zdj":
            self.label_73.setText(str(data.get('parameter16', '')))
            self.label_77.setText(str(data.get('parameter17', '')))
            self.label_81.setText(str(data.get('parameter18', '')))
            self.label_85.setText(str(data.get('parameter19', '')))
            self.label_89.setText(str(data.get('parameter20', '')))
            self.label_93.setText(str(data.get('parameter21', '')))  # 使用get方法提供默认值
        elif table_name == "factory2_1_set_data_jcj":
            self.label_104.setText(str(data.get('parameter1', '')))
            self.label_105.setText(str(data.get('parameter2', '')))
            self.label_106.setText(str(data.get('parameter3', '')))
            self.label_107.setText(str(data.get('parameter4', '')))
            self.label_108.setText(str(data.get('parameter5', '')))
            self.label_115.setText(str(data.get('parameter6', '')))  # 使用get方法提供默认值
        elif table_name == "factory2_1_set_data_fjj":
            self.label_109.setText(str(data.get('parameter1', '')))
            self.label_110.setText(str(data.get('parameter2', '')))
            self.label_111.setText(str(data.get('parameter3', '')))  # 使用get方法提供默认值
        elif table_name == "factory2_1_set_data_zdj":
            self.label_112.setText(str(data.get('parameter1', '')))
            self.label_113.setText(str(data.get('parameter2', '')))
            self.label_114.setText(str(data.get('parameter3', '')))
            self.label_116.setText(str(data.get('parameter4', '')))  # 使用get方法提供默认值
        elif table_name == "factory2_1_set_data_curve":
            self.label_117.setText(str(data.get('parameter1', '')))
            self.label_118.setText(str(data.get('parameter2', '')))
            self.label_114.setText(str(data.get('parameter3', '')))
            self.label_115.setText(str(data.get('parameter4', '')))
            self.label_121.setText(str(data.get('parameter5', '')))
            self.label_122.setText(str(data.get('parameter6', '')))  # 使用get方法提供默认值
    def show_dialog_pop_parameter(self):
        """隐藏当前历史数据窗口，显示实时参数弹窗的方法"""
        self.hide()  # 隐藏当前窗口
        # 检查实时参数弹窗是否已存在
        if self.dialog_realtime:
            # 如果弹窗已最小化或隐藏，则恢复显示
            if self.dialog_realtime.isMinimized():
                self.dialog_realtime.showNormal()  # 从最小化状态恢复
            elif not self.dialog_realtime.isVisible():
                self.dialog_realtime.show()  # 如果不可见则显示
            # 如果已经可见，则将其置于前台
            self.dialog_realtime.activateWindow()  # 激活窗口（置于前台）
            self.dialog_realtime.raise_()  # 提升窗口层级

    def center_dialog(self):
        """将弹窗居中显示的方法"""
        # 获取主屏幕尺寸
        screen = QApplication.primaryScreen().geometry()
        # 计算居中坐标（屏幕宽度-窗口宽度）/2
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        # 移动窗口到计算位置
        self.move(x, y)

    def dialog_mouse_press(self, event):
        """处理鼠标按下事件（用于窗口拖动）"""
        # 判断点击位置是否在标题栏区域内
        point_in_title = self.widget_historical_title.rect().contains(event.pos())
        # 当左键点击且位置在标题栏时
        if event.button() == Qt.LeftButton and point_in_title:
            # 记录全局鼠标位置（屏幕坐标系）
            self.drag_start_pos = event.globalPos()
            # 保存窗口当前位置
            self.dialog_original_pos = self.pos()
            # 接受事件，阻止事件传递
            event.accept()
        else:
            # 忽略非标题栏区域的点击
            event.ignore()

    def dialog_mouse_move(self, event):
        """处理鼠标移动事件（实现窗口拖动）"""
        # 当满足三个条件时处理拖动：
        # 1. 左键保持按下状态
        # 2. 存在初始拖动位置记录
        # 3. 鼠标在标题栏区域
        if (event.buttons() & Qt.LeftButton and
                hasattr(self, 'drag_start_pos') and
                self.widget_historical_title.rect().contains(event.pos())):

            # 计算位置偏移量（当前鼠标位置 - 起始位置）
            delta = event.globalPos() - self.drag_start_pos
            # 移动窗口到新位置（原始位置 + 偏移量）
            self.move(self.dialog_original_pos + delta)
            # 接受事件，确保操作流畅
            event.accept()
        else:
            # 忽略无效拖动操作
            event.ignore()

    # 历史参数弹窗类新增关闭事件处理
    # 重写窗口关闭事件处理方法（当窗口被关闭时自动触发）
    def closeEvent(self, event):
        """处理关闭事件：关闭关联的实时参数弹窗"""
        # 检查是否存在实时参数弹窗实例
        if self.dialog_realtime:  # 判断dialog_realtime是否已初始化
            self.dialog_realtime.close()  # 调用实时弹窗的关闭方法
        super().closeEvent(event)  # 调用父类QDialog的关闭事件处理，确保正常关闭流程

class HistoricalParameterDialogFactory2Device2(QDialog, Ui_Dialog_Pop_Historical_Parameter_Factory2Device2):
    def __init__(self):
        # 调用父类构造方法
        super().__init__()
        # 初始化UI界面
        self.threads = {}
        self.setWindowFlags(Qt.FramelessWindowHint)  # 设置无边框窗口样式（隐藏标题栏和边框）
        self.setAttribute(Qt.WA_TranslucentBackground)  # 启用透明背景属性（实现半透明/异形窗口效果）
        self.setupUi(self)

        self.dialog_realtime = None  # 定义创建用于存储历史数据曲线弹窗的实例
        self.pushButton_realtime.clicked.connect(self.show_dialog_pop_parameter)  # 连接按钮点击信号

        # 初始化位置记录变量
        self.dialog_original_pos = None  # 窗口原始位置
        self.drag_start_pos = None  # 鼠标拖动起始位置
        # 绑定鼠标事件到自身方法
        self.mousePressEvent = self.dialog_mouse_press  # 按下事件处理
        self.mouseMoveEvent = self.dialog_mouse_move  # 移动事件处理
        # 设置窗口居中属性
        self.center_dialog()  # 初始居中显示
        self.dateTimeEdit.setDateTime(datetime.now())
        # 连接查询按钮
        self.pushButton_historical_query.clicked.connect(self.handle_historical_query)
        # 初始化历史曲线
        self._init_historical_curves()

    def _init_historical_curves(self):
        """初始化历史曲线组件"""
        # 管径历史曲线 (创建历史曲线绘制组件)
        self.hist_curve1 = HistoricalCurvePlotter(
            self.widget_pop_historical_parameter_curve1,  # 指定父容器控件
            "factory2_2_set_data_curve",  # 对应的数据库表名
            {'curve1': {'field': 'parameter1', 'color': '#FF0000'},
                        'curve2': {'field': 'parameter2', 'color': '#FFFF00'},
                        'curve3': {'field': 'parameter3', 'color': '#00FFFF'},
                        'curve4': {'field': 'parameter4', 'color': '#00FF00'},
                        'curve5': {'field': 'parameter5', 'color': '#FFFF00'},
                        'curve6': {'field': 'parameter6', 'color': '#FF0000'}
             },  # 曲线参数映射配置
            (-1, 1)  # Y轴显示范围
        )

        # 挤出机历史曲线 (第二组历史曲线)
        self.hist_curve2 = HistoricalCurvePlotter(
            self.widget_pop_historical_parameter_curve2,  # 第二个曲线容器的父控件
            "factory2_2_realtime_data_jcj",  # 挤出机实时数据表
            {'curve1': {'field': 'parameter3', 'color': '#FF0000'},
             'curve2': {'field': 'parameter4', 'color': '#FFFF00'},
             'curve3': {'field': 'parameter5', 'color': '#00FFFF'},
             'curve4': {'field': 'parameter6', 'color': '#00FF00'},
             'curve5': {'field': 'parameter9', 'color': '#FFAA00'},
             'curve6': {'field': 'parameter10', 'color': '#FF55FF'}
             },  # 参数映射关系
            (0, 200)  # Y轴最大范围200
        )

    def handle_historical_query(self):
        """处理历史查询按钮点击事件的核心方法"""
        # 获取界面选择的时间（转换为Python datetime对象）
        query_time = self.dateTimeEdit.dateTime().toPyDateTime()
        # 计算结束时间（格式化成SQL可识别的字符串）
        end_time = query_time.strftime("%Y-%m-%d %H:%M:%S")
        # 计算起始时间（当前查询时间前推10分钟）
        start_time = (query_time - timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")
        # 更新两条历史曲线（触发重绘）
        self.hist_curve1.update_plot(start_time, end_time)  # 更新管径曲线
        self.hist_curve2.update_plot(start_time, end_time)  # 更新挤出机曲线

        # 更新参数显示（精确到秒的查询）
        self._update_parameters(
        query_time.strftime("%Y-%m-%d %H:%M:%S"),
        start_time,
        end_time)

    def _update_parameters(self, exact_time, start_time, end_time):
        """更新指定时间点的参数显示
        Args:
            exact_time: 精确时间字符串（格式：YYYY-MM-DD HH:MM:SS）
        """
        # 定义需要查询的数据表列表
        tables = ["factory2_2_realtime_data_jcj", "factory2_2_realtime_data_fjj", "factory2_2_realtime_data_zdj" , "factory2_2_set_data_curve",
                  "factory2_2_set_data_jcj", "factory2_2_set_data_fjj", "factory2_2_set_data_zdj"]

        # 创建线程对象
        thread = QThread()
        # 创建工作线程实例
        worker = HistoricalDataQueryWorker(tables, exact_time, start_time, end_time)

        # 将工作对象移动到新线程
        worker.moveToThread(thread)

        # 信号连接
        thread.started.connect(worker.run)  # type: ignore[attr-defined]
        worker.finished.connect(thread.quit)  # type: ignore[attr-defined]
        worker.finished.connect(worker.deleteLater)  # type: ignore[attr-defined]
        thread.finished.connect(thread.deleteLater)  # type: ignore[attr-defined]

        # 连接数据更新信号到处理方法
        worker.data_ready.connect(self._handle_historical_data)  # type: ignore[attr-defined]

        # 存储线程引用
        self.threads['historical_query'] = (thread, worker)

        # 启动线程
        thread.start()

    def _handle_historical_data(self, result_data):
        """处理从子线程接收到的历史数据
        Args:
            result_data: 包含表名和数据的字典 {table_name: data}
        """
        # 遍历所有返回的数据
        for table_name, data in result_data.items():
            # 如果有返回数据（即使只有一条）
            if data:
                # 更新界面标签（取第一条/唯一一条数据）
                self._update_ui_labels(table_name, data)

    def _update_ui_labels(self, table_name, data):
        """根据数据表名更新对应的UI标签
        Args:
            table_name: 数据表名称（用于分支判断）
            data: 单条历史数据记录（字典格式）
        """
        # 挤出机实时数据表处理分支
        if table_name == "factory2_2_realtime_data_jcj":
            # 更新参数1显示（label_10标签）
            self.label_10.setText(str(data.get('parameter1', '')))  # 使用空字符串作为默认值
            # 更新参数2显示（label_14标签）
            self.label_14.setText(str(data.get('parameter2', '')))
            self.label_18.setText(str(data.get('parameter3', '')))
            self.label_22.setText(str(data.get('parameter4', '')))
            self.label_26.setText(str(data.get('parameter5', '')))
            self.label_30.setText(str(data.get('parameter6', '')))
            self.label_34.setText(str(data.get('parameter7', '')))
            self.label_38.setText(str(data.get('parameter8', '')))
            self.label_42.setText(str(data.get('parameter9', '')))
            self.label_46.setText(str(data.get('parameter10', '')))
            self.label_50.setText(str(data.get('parameter11', '')))
            self.label_123.setText(str(data.get('parameter3', '')))
            self.label_127.setText(str(data.get('parameter4', '')))
            self.label_125.setText(str(data.get('parameter5', '')))
            self.label_126.setText(str(data.get('parameter6', '')))
            self.label_128.setText(str(data.get('parameter9', '')))
            self.label_124.setText(str(data.get('parameter10', '')))  # 使用get方法提供默认值
        # 放卷机实时数据表处理分支
        elif table_name == "factory2_2_realtime_data_fjj":
            # 更新参数12显示（label_53标签）
            self.label_53.setText(str(data.get('parameter12', '')))
            self.label_57.setText(str(data.get('parameter13', '')))
            self.label_61.setText(str(data.get('parameter14', '')))
            self.label_65.setText(str(data.get('parameter15', '')))  # 使用get方法提供默认值
        # 自动机历史数据表处理分支
        elif table_name == "factory2_2_realtime_data_zdj":
            self.label_73.setText(str(data.get('parameter16', '')))
            self.label_77.setText(str(data.get('parameter17', '')))
            self.label_81.setText(str(data.get('parameter18', '')))
            self.label_85.setText(str(data.get('parameter19', '')))
            self.label_89.setText(str(data.get('parameter20', '')))
            self.label_93.setText(str(data.get('parameter21', '')))  # 使用get方法提供默认值
        elif table_name == "factory2_2_set_data_jcj":
            self.label_104.setText(str(data.get('parameter1', '')))
            self.label_105.setText(str(data.get('parameter2', '')))
            self.label_106.setText(str(data.get('parameter3', '')))
            self.label_107.setText(str(data.get('parameter4', '')))
            self.label_108.setText(str(data.get('parameter5', '')))
            self.label_115.setText(str(data.get('parameter6', '')))  # 使用get方法提供默认值
        elif table_name == "factory2_2_set_data_fjj":
            self.label_109.setText(str(data.get('parameter1', '')))
            self.label_110.setText(str(data.get('parameter2', '')))
            self.label_111.setText(str(data.get('parameter3', '')))  # 使用get方法提供默认值
        elif table_name == "factory2_2_set_data_zdj":
            self.label_112.setText(str(data.get('parameter1', '')))
            self.label_113.setText(str(data.get('parameter2', '')))
            self.label_114.setText(str(data.get('parameter3', '')))
            self.label_116.setText(str(data.get('parameter4', '')))  # 使用get方法提供默认值
        elif table_name == "factory2_2_set_data_curve":
            self.label_117.setText(str(data.get('parameter1', '')))
            self.label_118.setText(str(data.get('parameter2', '')))
            self.label_114.setText(str(data.get('parameter3', '')))
            self.label_115.setText(str(data.get('parameter4', '')))
            self.label_121.setText(str(data.get('parameter5', '')))
            self.label_122.setText(str(data.get('parameter6', '')))  # 使用get方法提供默认值
    def show_dialog_pop_parameter(self):
        """隐藏当前历史数据窗口，显示实时参数弹窗的方法"""
        self.hide()  # 隐藏当前窗口
        # 检查实时参数弹窗是否已存在
        if self.dialog_realtime:
            # 如果弹窗已最小化或隐藏，则恢复显示
            if self.dialog_realtime.isMinimized():
                self.dialog_realtime.showNormal()  # 从最小化状态恢复
            elif not self.dialog_realtime.isVisible():
                self.dialog_realtime.show()  # 如果不可见则显示
            # 如果已经可见，则将其置于前台
            self.dialog_realtime.activateWindow()  # 激活窗口（置于前台）
            self.dialog_realtime.raise_()  # 提升窗口层级

    def center_dialog(self):
        """将弹窗居中显示的方法"""
        # 获取主屏幕尺寸
        screen = QApplication.primaryScreen().geometry()
        # 计算居中坐标（屏幕宽度-窗口宽度）/2
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        # 移动窗口到计算位置
        self.move(x, y)

    def dialog_mouse_press(self, event):
        """处理鼠标按下事件（用于窗口拖动）"""
        # 判断点击位置是否在标题栏区域内
        point_in_title = self.widget_historical_title.rect().contains(event.pos())
        # 当左键点击且位置在标题栏时
        if event.button() == Qt.LeftButton and point_in_title:
            # 记录全局鼠标位置（屏幕坐标系）
            self.drag_start_pos = event.globalPos()
            # 保存窗口当前位置
            self.dialog_original_pos = self.pos()
            # 接受事件，阻止事件传递
            event.accept()
        else:
            # 忽略非标题栏区域的点击
            event.ignore()

    def dialog_mouse_move(self, event):
        """处理鼠标移动事件（实现窗口拖动）"""
        # 当满足三个条件时处理拖动：
        # 1. 左键保持按下状态
        # 2. 存在初始拖动位置记录
        # 3. 鼠标在标题栏区域
        if (event.buttons() & Qt.LeftButton and
                hasattr(self, 'drag_start_pos') and
                self.widget_historical_title.rect().contains(event.pos())):

            # 计算位置偏移量（当前鼠标位置 - 起始位置）
            delta = event.globalPos() - self.drag_start_pos
            # 移动窗口到新位置（原始位置 + 偏移量）
            self.move(self.dialog_original_pos + delta)
            # 接受事件，确保操作流畅
            event.accept()
        else:
            # 忽略无效拖动操作
            event.ignore()

    # 历史参数弹窗类新增关闭事件处理
    # 重写窗口关闭事件处理方法（当窗口被关闭时自动触发）
    def closeEvent(self, event):
        """处理关闭事件：关闭关联的实时参数弹窗"""
        # 检查是否存在实时参数弹窗实例
        if self.dialog_realtime:  # 判断dialog_realtime是否已初始化
            self.dialog_realtime.close()  # 调用实时弹窗的关闭方法
        super().closeEvent(event)  # 调用父类QDialog的关闭事件处理，确保正常关闭流程

class HistoricalParameterDialogFactory2Device3(QDialog, Ui_Dialog_Pop_Historical_Parameter_Factory2Device3):
    def __init__(self):
        # 调用父类构造方法
        super().__init__()
        # 初始化UI界面
        self.threads = {}
        self.setWindowFlags(Qt.FramelessWindowHint)  # 设置无边框窗口样式（隐藏标题栏和边框）
        self.setAttribute(Qt.WA_TranslucentBackground)  # 启用透明背景属性（实现半透明/异形窗口效果）
        self.setupUi(self)

        self.dialog_realtime = None  # 定义创建用于存储历史数据曲线弹窗的实例
        self.pushButton_realtime.clicked.connect(self.show_dialog_pop_parameter)  # 连接按钮点击信号

        # 初始化位置记录变量
        self.dialog_original_pos = None  # 窗口原始位置
        self.drag_start_pos = None  # 鼠标拖动起始位置
        # 绑定鼠标事件到自身方法
        self.mousePressEvent = self.dialog_mouse_press  # 按下事件处理
        self.mouseMoveEvent = self.dialog_mouse_move  # 移动事件处理
        # 设置窗口居中属性
        self.center_dialog()  # 初始居中显示
        self.dateTimeEdit.setDateTime(datetime.now())
        # 连接查询按钮
        self.pushButton_historical_query.clicked.connect(self.handle_historical_query)
        # 初始化历史曲线
        self._init_historical_curves()

    def _init_historical_curves(self):
        """初始化历史曲线组件"""
        # 管径历史曲线 (创建历史曲线绘制组件)
        self.hist_curve1 = HistoricalCurvePlotter(
            self.widget_pop_historical_parameter_curve1,  # 指定父容器控件
            "factory2_3_set_data_curve",  # 对应的数据库表名
            {'curve1': {'field': 'parameter1', 'color': '#FF0000'},
                        'curve2': {'field': 'parameter2', 'color': '#FFFF00'},
                        'curve3': {'field': 'parameter3', 'color': '#00FFFF'},
                        'curve4': {'field': 'parameter4', 'color': '#00FF00'},
                        'curve5': {'field': 'parameter5', 'color': '#FFFF00'},
                        'curve6': {'field': 'parameter6', 'color': '#FF0000'}
             },  # 曲线参数映射配置
            (-1, 1)  # Y轴显示范围
        )

        # 挤出机历史曲线 (第二组历史曲线)
        self.hist_curve2 = HistoricalCurvePlotter(
            self.widget_pop_historical_parameter_curve2,  # 第二个曲线容器的父控件
            "factory2_3_realtime_data_jcj",  # 挤出机实时数据表
            {'curve1': {'field': 'parameter3', 'color': '#FF0000'},
             'curve2': {'field': 'parameter4', 'color': '#FFFF00'},
             'curve3': {'field': 'parameter5', 'color': '#00FFFF'},
             'curve4': {'field': 'parameter6', 'color': '#00FF00'},
             'curve5': {'field': 'parameter9', 'color': '#FFAA00'},
             'curve6': {'field': 'parameter10', 'color': '#FF55FF'}
             },  # 参数映射关系
            (0, 200)  # Y轴最大范围200
        )

    def handle_historical_query(self):
        """处理历史查询按钮点击事件的核心方法"""
        # 获取界面选择的时间（转换为Python datetime对象）
        query_time = self.dateTimeEdit.dateTime().toPyDateTime()
        # 计算结束时间（格式化成SQL可识别的字符串）
        end_time = query_time.strftime("%Y-%m-%d %H:%M:%S")
        # 计算起始时间（当前查询时间前推10分钟）
        start_time = (query_time - timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")
        # 更新两条历史曲线（触发重绘）
        self.hist_curve1.update_plot(start_time, end_time)  # 更新管径曲线
        self.hist_curve2.update_plot(start_time, end_time)  # 更新挤出机曲线

        # 更新参数显示（精确到秒的查询）
        self._update_parameters(
        query_time.strftime("%Y-%m-%d %H:%M:%S"),
        start_time,
        end_time)

    def _update_parameters(self, exact_time, start_time, end_time):
        """更新指定时间点的参数显示
        Args:
            exact_time: 精确时间字符串（格式：YYYY-MM-DD HH:MM:SS）
        """
        # 定义需要查询的数据表列表
        tables = ["factory2_3_realtime_data_jcj", "factory2_3_realtime_data_fjj", "factory2_3_realtime_data_zdj" , "factory2_3_set_data_curve",
                  "factory2_3_set_data_jcj", "factory2_3_set_data_fjj", "factory2_3_set_data_zdj"]

        # 创建线程对象
        thread = QThread()
        # 创建工作线程实例
        worker = HistoricalDataQueryWorker(tables, exact_time, start_time, end_time)

        # 将工作对象移动到新线程
        worker.moveToThread(thread)

        # 信号连接
        thread.started.connect(worker.run)  # type: ignore[attr-defined]
        worker.finished.connect(thread.quit)  # type: ignore[attr-defined]
        worker.finished.connect(worker.deleteLater)  # type: ignore[attr-defined]
        thread.finished.connect(thread.deleteLater)  # type: ignore[attr-defined]

        # 连接数据更新信号到处理方法
        worker.data_ready.connect(self._handle_historical_data)  # type: ignore[attr-defined]

        # 存储线程引用
        self.threads['historical_query'] = (thread, worker)

        # 启动线程
        thread.start()

    def _handle_historical_data(self, result_data):
        """处理从子线程接收到的历史数据
        Args:
            result_data: 包含表名和数据的字典 {table_name: data}
        """
        # 遍历所有返回的数据
        for table_name, data in result_data.items():
            # 如果有返回数据（即使只有一条）
            if data:
                # 更新界面标签（取第一条/唯一一条数据）
                self._update_ui_labels(table_name, data)

    def _update_ui_labels(self, table_name, data):
        """根据数据表名更新对应的UI标签
        Args:
            table_name: 数据表名称（用于分支判断）
            data: 单条历史数据记录（字典格式）
        """
        # 挤出机实时数据表处理分支
        if table_name == "factory2_3_realtime_data_jcj":
            # 更新参数1显示（label_10标签）
            self.label_10.setText(str(data.get('parameter1', '')))  # 使用空字符串作为默认值
            # 更新参数2显示（label_14标签）
            self.label_14.setText(str(data.get('parameter2', '')))
            self.label_18.setText(str(data.get('parameter3', '')))
            self.label_22.setText(str(data.get('parameter4', '')))
            self.label_26.setText(str(data.get('parameter5', '')))
            self.label_30.setText(str(data.get('parameter6', '')))
            self.label_34.setText(str(data.get('parameter7', '')))
            self.label_38.setText(str(data.get('parameter8', '')))
            self.label_42.setText(str(data.get('parameter9', '')))
            self.label_46.setText(str(data.get('parameter10', '')))
            self.label_50.setText(str(data.get('parameter11', '')))
            self.label_123.setText(str(data.get('parameter3', '')))
            self.label_127.setText(str(data.get('parameter4', '')))
            self.label_125.setText(str(data.get('parameter5', '')))
            self.label_126.setText(str(data.get('parameter6', '')))
            self.label_128.setText(str(data.get('parameter9', '')))
            self.label_124.setText(str(data.get('parameter10', '')))  # 使用get方法提供默认值
        # 放卷机实时数据表处理分支
        elif table_name == "factory2_3_realtime_data_fjj":
            # 更新参数12显示（label_53标签）
            self.label_53.setText(str(data.get('parameter12', '')))
            self.label_57.setText(str(data.get('parameter13', '')))
            self.label_61.setText(str(data.get('parameter14', '')))
            self.label_65.setText(str(data.get('parameter15', '')))  # 使用get方法提供默认值
        # 自动机历史数据表处理分支
        elif table_name == "factory2_3_realtime_data_zdj":
            self.label_73.setText(str(data.get('parameter16', '')))
            self.label_77.setText(str(data.get('parameter17', '')))
            self.label_81.setText(str(data.get('parameter18', '')))
            self.label_85.setText(str(data.get('parameter19', '')))
            self.label_89.setText(str(data.get('parameter20', '')))
            self.label_93.setText(str(data.get('parameter21', '')))  # 使用get方法提供默认值
        elif table_name == "factory2_3_set_data_jcj":
            self.label_104.setText(str(data.get('parameter1', '')))
            self.label_105.setText(str(data.get('parameter2', '')))
            self.label_106.setText(str(data.get('parameter3', '')))
            self.label_107.setText(str(data.get('parameter4', '')))
            self.label_108.setText(str(data.get('parameter5', '')))
            self.label_115.setText(str(data.get('parameter6', '')))  # 使用get方法提供默认值
        elif table_name == "factory2_3_set_data_fjj":
            self.label_109.setText(str(data.get('parameter1', '')))
            self.label_110.setText(str(data.get('parameter2', '')))
            self.label_111.setText(str(data.get('parameter3', '')))  # 使用get方法提供默认值
        elif table_name == "factory2_3_set_data_zdj":
            self.label_112.setText(str(data.get('parameter1', '')))
            self.label_113.setText(str(data.get('parameter2', '')))
            self.label_114.setText(str(data.get('parameter3', '')))
            self.label_116.setText(str(data.get('parameter4', '')))  # 使用get方法提供默认值
        elif table_name == "factory2_3_set_data_curve":
            self.label_117.setText(str(data.get('parameter1', '')))
            self.label_118.setText(str(data.get('parameter2', '')))
            self.label_114.setText(str(data.get('parameter3', '')))
            self.label_115.setText(str(data.get('parameter4', '')))
            self.label_121.setText(str(data.get('parameter5', '')))
            self.label_122.setText(str(data.get('parameter6', '')))  # 使用get方法提供默认值
    def show_dialog_pop_parameter(self):
        """隐藏当前历史数据窗口，显示实时参数弹窗的方法"""
        self.hide()  # 隐藏当前窗口
        # 检查实时参数弹窗是否已存在
        if self.dialog_realtime:
            # 如果弹窗已最小化或隐藏，则恢复显示
            if self.dialog_realtime.isMinimized():
                self.dialog_realtime.showNormal()  # 从最小化状态恢复
            elif not self.dialog_realtime.isVisible():
                self.dialog_realtime.show()  # 如果不可见则显示
            # 如果已经可见，则将其置于前台
            self.dialog_realtime.activateWindow()  # 激活窗口（置于前台）
            self.dialog_realtime.raise_()  # 提升窗口层级

    def center_dialog(self):
        """将弹窗居中显示的方法"""
        # 获取主屏幕尺寸
        screen = QApplication.primaryScreen().geometry()
        # 计算居中坐标（屏幕宽度-窗口宽度）/2
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        # 移动窗口到计算位置
        self.move(x, y)

    def dialog_mouse_press(self, event):
        """处理鼠标按下事件（用于窗口拖动）"""
        # 判断点击位置是否在标题栏区域内
        point_in_title = self.widget_historical_title.rect().contains(event.pos())
        # 当左键点击且位置在标题栏时
        if event.button() == Qt.LeftButton and point_in_title:
            # 记录全局鼠标位置（屏幕坐标系）
            self.drag_start_pos = event.globalPos()
            # 保存窗口当前位置
            self.dialog_original_pos = self.pos()
            # 接受事件，阻止事件传递
            event.accept()
        else:
            # 忽略非标题栏区域的点击
            event.ignore()

    def dialog_mouse_move(self, event):
        """处理鼠标移动事件（实现窗口拖动）"""
        # 当满足三个条件时处理拖动：
        # 1. 左键保持按下状态
        # 2. 存在初始拖动位置记录
        # 3. 鼠标在标题栏区域
        if (event.buttons() & Qt.LeftButton and
                hasattr(self, 'drag_start_pos') and
                self.widget_historical_title.rect().contains(event.pos())):

            # 计算位置偏移量（当前鼠标位置 - 起始位置）
            delta = event.globalPos() - self.drag_start_pos
            # 移动窗口到新位置（原始位置 + 偏移量）
            self.move(self.dialog_original_pos + delta)
            # 接受事件，确保操作流畅
            event.accept()
        else:
            # 忽略无效拖动操作
            event.ignore()

    # 历史参数弹窗类新增关闭事件处理
    # 重写窗口关闭事件处理方法（当窗口被关闭时自动触发）
    def closeEvent(self, event):
        """处理关闭事件：关闭关联的实时参数弹窗"""
        # 检查是否存在实时参数弹窗实例
        if self.dialog_realtime:  # 判断dialog_realtime是否已初始化
            self.dialog_realtime.close()  # 调用实时弹窗的关闭方法
        super().closeEvent(event)  # 调用父类QDialog的关闭事件处理，确保正常关闭流程


# ---------------------------------历史参数弹窗类（继承QDialog和UI类）---------------------------------
class AlarmDialog(QDialog, Ui_Dialog_alarm):
    def __init__(self):
        # 调用父类构造方法
        super().__init__()
        # 初始化UI界面
        self.setWindowFlags(Qt.FramelessWindowHint)  # 设置无边框窗口样式（隐藏标题栏和边框）
        self.setAttribute(Qt.WA_TranslucentBackground)  # 启用透明背景属性（实现半透明/异形窗口效果）
        self.setupUi(self)
        # 创建线程管理器字典
        self.threads = {}
        # 设置窗口属性
        self.right_down_dialog()  # 初始右下角显示
        # 初始化报警表名列表
        self.alarm_tables = [
            'factory1_1_alarm_data',
            'factory1_2_alarm_data',
            'factory1_3_alarm_data',
            'factory1_4_alarm_data',
            'factory2_1_alarm_data',
            'factory2_2_alarm_data',
            'factory2_3_alarm_data'
        ]

        # 存储每个表最后一次的报警值，用于比较变化
        self.last_alarm_values = {}

        # 前端根据报警表名自动生成包含所有表名的本地缓存版本字典
        self.data_versions = {table: 0 for table in self.alarm_tables}
        # 确保初始化为9行
        self.tableWidget_realtime_alarm.setRowCount(9)

        # 设置日期时间选择器的初始值
        current_time = datetime.now()
        start_time = current_time - timedelta(hours=24)  # 默认查询最近24小时
        self.dateTimeEdit_start.setDateTime(start_time)
        self.dateTimeEdit_stop.setDateTime(current_time)

        # 连接查询按钮的点击信号到查询方法
        self.pushButton_query.clicked.connect(self.query_historical_alarms)
        # 启动报警数据更新线程 - 使用DataUpdateWorker
        self._start_data_update_thread(self.alarm_tables)

    # 添加新方法：启动所有数据采集线程
    # 添加新方法：启动数据更新线程 - 复用DataUpdateWorker
    def _start_data_update_thread(self, tables_to_monitor):
        """启动数据更新线程
        参数:
            tables_to_monitor: 需要监控的表名列表
        """
        # 创建线程对象
        thread = QThread()
        # 创建工作线程实例
        worker = DataUpdateWorker(tables_to_monitor)

        # 将工作对象移动到新线程
        worker.moveToThread(thread)

        # 信号连接
        thread.started.connect(worker.run)  #type: ignore[arg-type]# 线程启动时执行run方法
        worker.finished.connect(thread.quit)  #type: ignore[arg-type]# 工作完成时退出线程
        worker.finished.connect(worker.deleteLater)  #type: ignore[arg-type]# 工作完成后销毁worker对象
        thread.finished.connect(thread.deleteLater)  #type: ignore[arg-type]# 线程退出后销毁线程对象

        # 连接数据更新信号到处理方法
        worker.data_updated.connect(self._handle_alarm_update)#type: ignore[arg-type]

        # 存储线程引用
        self.threads['data_update_alarm'] = (thread, worker)

        # 启动线程
        thread.start()
    # 添加新方法：处理报警数据更新
    def _handle_alarm_update(self, table_name, data):
        """处理从子线程接收到的报警数据更新
        参数:
            table_name: 表名
            data: 数据字典
        """
        # 数据有效性检查
        if not data or 'parameter1' not in data:
            print("Invalid data or missing 'parameter1' field.")
            return

        # 获取报警值
        alarm_value = data.get('parameter1','')
        print(alarm_value)

        # 检查报警值是否有变化
        if table_name in self.last_alarm_values and self.last_alarm_values[table_name] == alarm_value:
            # 报警值没有变化，不需要更新界面
            return

        # 更新最后一次的报警值
        self.last_alarm_values[table_name] = alarm_value

        # 如果报警值为0或空，则不处理
        if not alarm_value:
            print("No alarm value or empty value（报警值为0或空）.")
            return

        # 从数据库获取时间戳，而不是使用当前时间
        record_time = data.get('timestamp')
        # 如果timestamp是datetime对象，则格式化为字符串
        if isinstance(record_time, datetime):
            record_time = record_time.strftime("%Y-%m-%d %H:%M:%S")
        # 如果timestamp是字符串，可能包含"T"字符，需要替换
        elif isinstance(record_time, str):
            # 替换ISO格式中的"T"为空格
            record_time = record_time.replace("T", " ")
        # 如果没有timestamp或格式不正确，则使用当前时间作为备选
        else:
            record_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print("警告: 数据库中缺少timestamp字段或格式不正确，使用当前时间作为替代")

        # 解析表名获取工厂和设备信息
        parts = table_name.split('_')
        factory = parts[0]
        device = parts[1] if len(parts) > 1 else "未知设备"

        # 根据报警值获取报警内容
        alarm_content = self._get_alarm_content(alarm_value)

        # 构建报警显示文本
        alarm_text = f"[{record_time}] {factory}-{device}: {alarm_content}"

        # 获取当前所有行数据
        rows = []
        for row in range(self.tableWidget_realtime_alarm.rowCount()):
            if item := self.tableWidget_realtime_alarm.item(row, 0):
                rows.append(item.text())

        # 如果已有9条报警，移除最早的一条
        if len(rows) >= 9:
            rows.pop(0) #type: ignore[arg-type]

        # 添加新报警到列表末尾
        rows.append(alarm_text)

        # 清空表格
        self.tableWidget_realtime_alarm.clearContents()

        # 重新填充表格
        for row, text in enumerate(rows):
            self.tableWidget_realtime_alarm.setItem(row, 0, QTableWidgetItem(text))
            self.tableWidget_realtime_alarm.item(row, 0).setBackground(Qt.red)

        # 滚动到最后一行
        self.tableWidget_realtime_alarm.scrollToBottom()

        print(f"新报警: {factory} {device} - {alarm_content}")
    def right_down_dialog(self):
        """将弹窗居中显示的方法"""
        # 获取主屏幕尺寸
        screen = QApplication.primaryScreen().geometry()
        # 计算居中坐标（屏幕宽度-窗口宽度）/2
        x = (screen.width() - self.width())
        y = (screen.height() - self.height())
        # 移动窗口到计算位置
        self.move(x, y)
    @staticmethod
    def _get_alarm_content(alarm_code):
        """根据报警代码获取报警内容描述"""
        # 报警代码与内容的映射字典
        alarm_dict = {
            1: "上电加热...",
            2: "挤出启动...",
            4: "运转作业...",
            8: "常规预警！",
            16: "异常报警！",
            32: "请求支援！"
        }

        # 返回对应的报警内容，如果没有对应的内容则返回默认文本
        return alarm_dict.get(alarm_code, f"未知报警(代码:{alarm_code})")

    def query_historical_alarms(self):
        """查询历史报警记录的方法"""
        # 获取用户选择的起始和结束时间
        start_time = self.dateTimeEdit_start.dateTime().toPyDateTime()
        end_time = self.dateTimeEdit_stop.dateTime().toPyDateTime()

        # 检查时间范围是否有效
        if start_time > end_time:
            print("错误：起始时间不能晚于结束时间")
            # 可以在界面上显示错误提示
            return

        # 格式化时间为数据库查询格式
        start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
        end_time_str = end_time.strftime("%Y-%m-%d %H:%M:%S")

        print(f"查询历史报警: {start_time_str} 至 {end_time_str}")

        # 创建线程对象
        thread = QThread()
        # 创建工作线程实例
        worker = AlarmHistoryQueryWorker(self.alarm_tables, start_time_str, end_time_str)

        # 将工作对象移动到新线程
        worker.moveToThread(thread)

        # 信号连接
        thread.started.connect(worker.run)  # type: ignore[attr-defined]
        worker.finished.connect(thread.quit)    # type: ignore[attr-defined]
        worker.finished.connect(worker.deleteLater) # type: ignore[attr-defined]
        thread.finished.connect(thread.deleteLater) # type: ignore[attr-defined]

        # 连接数据更新信号到处理方法
        worker.data_ready.connect(self._handle_alarm_history)   # type: ignore[attr-defined]

        # 存储线程引用
        self.threads['alarm_history_query'] = (thread, worker)

        # 启动线程
        thread.start()
    def _handle_alarm_history(self, all_alarms):
        """处理从子线程接收到的历史报警数据
        Args:
            all_alarms: 报警记录列表 [(时间, 报警文本), ...]
        """
        # 清空历史报警表格
        self.tableWidget_historical_alarm.clearContents()

        # 设置表格行数（最多显示50行，或者实际记录数）
        row_count = min(len(all_alarms), 50)
        self.tableWidget_historical_alarm.setRowCount(row_count)

        # 填充表格
        for row, (_, alarm_text) in enumerate(all_alarms[:50]):  # 最多显示50条
            self.tableWidget_historical_alarm.setItem(row, 0, QTableWidgetItem(alarm_text))
            # 设置背景色为黄色（区别于实时报警的红色）
            self.tableWidget_historical_alarm.item(row, 0).setBackground(Qt.yellow)

        # 如果没有查询到报警记录
        if not all_alarms:
            # 设置一行显示无数据
            self.tableWidget_historical_alarm.setRowCount(1)
            self.tableWidget_historical_alarm.setItem(0, 0, QTableWidgetItem("查询时间段内无报警记录"))

        # 滚动到第一行
        self.tableWidget_historical_alarm.scrollToTop()

        print(f"共查询到 {len(all_alarms)} 条历史报警记录")
    # def closeEvent(self, event):
    #     # 停止所有报警相关线程
    #     if hasattr(self, 'threads'):
    #         for key, (thread, worker) in self.threads.items():
    #             if hasattr(worker, 'stop'):
    #                 worker.stop()
    #     super().closeEvent(event)

# ---------------------------------主窗口类（继承QMainWindow和UI类）---------------------------------
class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        # 调用父类构造方法
        super().__init__()
        # 初始化UI界面
        self.setupUi(self)
        # 设置窗口全屏显示
        self.setWindowState(Qt.WindowFullScreen)

        # 初始化参数弹窗（使用自定义弹窗类）
        self.pop_dialog = ParameterDialog()
        self.pop_dialog_factory1_2 = ParameterDialogFactory1Device2()
        self.pop_dialog_factory1_3 = ParameterDialogFactory1Device3()
        self.pop_dialog_factory1_4 = ParameterDialogFactory1Device4()
        self.pop_dialog_factory2_1 = ParameterDialogFactory2Device1()
        self.pop_dialog_factory2_2 = ParameterDialogFactory2Device2()
        self.pop_dialog_factory2_3 = ParameterDialogFactory2Device3()


        # 初始化历史弹窗（使用自定义弹窗类）
        self.dialog_historical = HistoricalParameterDialog()
        self.dialog_historical_factory1_2 = HistoricalParameterDialogFactory1Device2()
        self.dialog_historical_factory1_3 = HistoricalParameterDialogFactory1Device3()
        self.dialog_historical_factory1_4 = HistoricalParameterDialogFactory1Device4()
        self.dialog_historical_factory2_1 = HistoricalParameterDialogFactory2Device1()
        self.dialog_historical_factory2_2 = HistoricalParameterDialogFactory2Device2()
        self.dialog_historical_factory2_3 = HistoricalParameterDialogFactory2Device3()

        # 建立实例关联
        self.pop_dialog.dialog_historical = self.dialog_historical
        self.dialog_historical.dialog_realtime = self.pop_dialog

        self.pop_dialog_factory1_2.dialog_historical = self.dialog_historical_factory1_2
        self.dialog_historical_factory1_2.dialog_realtime = self.pop_dialog_factory1_2
        self.pop_dialog_factory1_3.dialog_historical = self.dialog_historical_factory1_3
        self.dialog_historical_factory1_3.dialog_realtime = self.pop_dialog_factory1_3
        self.pop_dialog_factory1_4.dialog_historical = self.dialog_historical_factory1_4
        self.dialog_historical_factory1_4.dialog_realtime = self.pop_dialog_factory1_4
        self.pop_dialog_factory2_1.dialog_historical = self.dialog_historical_factory2_1
        self.dialog_historical_factory2_1.dialog_realtime = self.pop_dialog_factory2_1
        self.pop_dialog_factory2_2.dialog_historical = self.dialog_historical_factory2_2
        self.dialog_historical_factory2_2.dialog_realtime = self.pop_dialog_factory2_2
        self.pop_dialog_factory2_3.dialog_historical = self.dialog_historical_factory2_3
        self.dialog_historical_factory2_3.dialog_realtime = self.pop_dialog_factory2_3
        # 初始化报警弹窗（使用自定义弹窗类）
        self.pop_alarm_dialog = AlarmDialog()

        # 绑定曲线控件的鼠标点击事件
        self.curve1.mousePressEvent = self.show_pop_parameter
        self.curve2.mousePressEvent = self.show_pop_parameter_factory1_2
        self.curve3.mousePressEvent = self.show_pop_parameter_factory1_3
        self.curve4.mousePressEvent = self.show_pop_parameter_factory1_4
        self.curve5.mousePressEvent = self.show_pop_parameter_factory2_1
        self.curve6.mousePressEvent = self.show_pop_parameter_factory2_2
        self.curve7.mousePressEvent = self.show_pop_parameter_factory2_3
        # 绑定曲线控件的鼠标点击事件
        self.pushButton_alarm.mousePressEvent = self.show_pop_alarm
        # 绑定关闭按钮：点击时关闭所有窗口
        self.Button_close.clicked.connect(self.close_all_windows)
        # 绑定最小化按钮：点击时最小化所有窗口
        self.Button_minimize.clicked.connect(self.minimize_all_windows)
        # 初始化时间功能
        self.timer = QTimer(self)  # 创建定时器对象
        self.timer.timeout.connect(self.update_time)  # type: ignore[attr-defined] # 连接定时信号
        self.timer.start(1000)  # 启动定时器（1秒间隔）
        self.update_time()  # 立即更新时间显示

        # 创建线程管理器字典
        self.threads = {}
        # 需要监控的表名列表
        self.tables_to_monitor = [
            "factory1_1_set_data_curve",
            "factory1_2_set_data_curve",
            "factory1_2_set_data_curve",
            "factory1_4_set_data_curve",
            "factory2_1_set_data_curve",
            "factory2_2_set_data_curve",
            "factory2_3_set_data_curve",
            "factory1_1_realtime_data_jcj",
            "factory1_2_realtime_data_jcj",
            "factory1_3_realtime_data_jcj",
            "factory1_4_realtime_data_jcj",
            "factory2_1_realtime_data_jcj",
            "factory2_2_realtime_data_jcj",
            "factory2_3_realtime_data_jcj"
        ]

        # 启动数据更新线程
        self._start_data_update_thread(self.tables_to_monitor)
        # 添加首页面采集子线程
        self._start_insert_threads()
        # 添加管径实时曲线
        self.curve_plotter1 = RealTimeMainWindowCurve1(
            parent_widget=self.curve1,  # 对应UI中的曲线容器
            table_name="factory1_1_set_data_curve",
            params_config={
                'curve3': 'parameter3',
                'curve1': 'parameter1',
                'curve6': 'parameter6',
                'curve4': 'parameter4',
                'curve2': 'parameter2',
                'curve5': 'parameter5'
            },
            y_limits=(-1, 1)
        )
        self.curve_plotter2 = RealTimeMainWindowCurve1(
            parent_widget=self.curve2,  # 对应UI中的曲线容器
            table_name="factory1_2_set_data_curve",
            params_config={
                'curve3': 'parameter3',
                'curve1': 'parameter1',
                'curve6': 'parameter6',
                'curve4': 'parameter4',
                'curve2': 'parameter2',
                'curve5': 'parameter5'
            },
            y_limits=(-1, 1)
        )
        self.curve_plotter3 = RealTimeMainWindowCurve1(
            parent_widget=self.curve3,  # 对应UI中的曲线容器
            table_name="factory1_3_set_data_curve",
            params_config={
                'curve3': 'parameter3',
                'curve1': 'parameter1',
                'curve6': 'parameter6',
                'curve4': 'parameter4',
                'curve2': 'parameter2',
                'curve5': 'parameter5'
            },
            y_limits=(-1, 1)
        )
        self.curve_plotter4 = RealTimeMainWindowCurve1(
            parent_widget=self.curve4,  # 对应UI中的曲线容器
            table_name="factory1_4_set_data_curve",
            params_config={
                'curve3': 'parameter3',
                'curve1': 'parameter1',
                'curve6': 'parameter6',
                'curve4': 'parameter4',
                'curve2': 'parameter2',
                'curve5': 'parameter5'
            },
            y_limits=(-1, 1)
        )
        self.curve_plotter5 = RealTimeMainWindowCurve1(
            parent_widget=self.curve5,  # 对应UI中的曲线容器
            table_name="factory2_1_set_data_curve",
            params_config={
                'curve3': 'parameter3',
                'curve1': 'parameter1',
                'curve6': 'parameter6',
                'curve4': 'parameter4',
                'curve2': 'parameter2',
                'curve5': 'parameter5'
            },
            y_limits=(-1, 1)
        )
        self.curve_plotter6 = RealTimeMainWindowCurve1(
            parent_widget=self.curve6,  # 对应UI中的曲线容器
            table_name="factory2_2_set_data_curve",
            params_config={
                'curve3': 'parameter3',
                'curve1': 'parameter1',
                'curve6': 'parameter6',
                'curve4': 'parameter4',
                'curve2': 'parameter2',
                'curve5': 'parameter5'
            },
            y_limits=(-1, 1)
        )
        self.curve_plotter7 = RealTimeMainWindowCurve1(
            parent_widget=self.curve7,  # 对应UI中的曲线容器
            table_name="factory2_3_set_data_curve",
            params_config={
                'curve3': 'parameter3',
                'curve1': 'parameter1',
                'curve6': 'parameter6',
                'curve4': 'parameter4',
                'curve2': 'parameter2',
                'curve5': 'parameter5'
            },
            y_limits=(-1, 1)
        )
        # 添加管径实时曲线（示例配置）
        self.curve_plotter_realtime1 = RealTimeCurvePlotter(
            parent_widget=self.pop_dialog.widget_pop_parameter_curve1,  # 对应UI中的曲线容器
            table_name="factory1_1_set_data_curve",
            params_config={
                'curve3': 'parameter3',
                'curve1': 'parameter1',
                'curve6': 'parameter6',
                'curve4': 'parameter4',
                'curve2': 'parameter2',
                'curve5': 'parameter5'
            },
            y_limits=(-1, 1)
        )
        self.curve_jcj_realtime1 = RealTimeJcjCurvePlotter(
            parent_widget=self.pop_dialog.widget_pop_parameter_curve2,  # 对应UI中的曲线容器
            table_name="factory1_1_realtime_data_jcj",
            params_config={
                'curve1': 'parameter3',
                'curve2': 'parameter4',
                'curve3': 'parameter5',
                'curve4': 'parameter6',
                'curve5': 'parameter9',
                'curve6': 'parameter10'
            },
            y_limits=(0, 200)
        )
        # 添加管径实时曲线（示例配置）
        self.curve_plotter_realtime2 = RealTimeCurvePlotter(
            parent_widget=self.pop_dialog_factory1_2.widget_pop_parameter_curve1,  # 对应UI中的曲线容器
            table_name="factory1_2_set_data_curve",
            params_config={
                'curve3': 'parameter3',
                'curve1': 'parameter1',
                'curve6': 'parameter6',
                'curve4': 'parameter4',
                'curve2': 'parameter2',
                'curve5': 'parameter5'
            },
            y_limits=(-1, 1)
        )
        self.curve_jcj_realtime2 = RealTimeJcjCurvePlotter(
            parent_widget=self.pop_dialog_factory1_2.widget_pop_parameter_curve2,  # 对应UI中的曲线容器
            table_name="factory1_2_realtime_data_jcj",
            params_config={
                'curve1': 'parameter3',
                'curve2': 'parameter4',
                'curve3': 'parameter5',
                'curve4': 'parameter6',
                'curve5': 'parameter9',
                'curve6': 'parameter10'
            },
            y_limits=(0, 200)
        )
        # 添加管径实时曲线（示例配置）
        self.curve_plotter_realtime3 = RealTimeCurvePlotter(
            parent_widget=self.pop_dialog_factory1_3.widget_pop_parameter_curve1,  # 对应UI中的曲线容器
            table_name="factory1_3_set_data_curve",
            params_config={
                'curve3': 'parameter3',
                'curve1': 'parameter1',
                'curve6': 'parameter6',
                'curve4': 'parameter4',
                'curve2': 'parameter2',
                'curve5': 'parameter5'
            },
            y_limits=(-1, 1)
        )
        self.curve_jcj_realtime3 = RealTimeJcjCurvePlotter(
            parent_widget=self.pop_dialog_factory1_3.widget_pop_parameter_curve2,  # 对应UI中的曲线容器
            table_name="factory1_3_realtime_data_jcj",
            params_config={
                'curve1': 'parameter3',
                'curve2': 'parameter4',
                'curve3': 'parameter5',
                'curve4': 'parameter6',
                'curve5': 'parameter9',
                'curve6': 'parameter10'
            },
            y_limits=(0, 200)
        )
        # 添加管径实时曲线（示例配置）
        self.curve_plotter_realtime4 = RealTimeCurvePlotter(
            parent_widget=self.pop_dialog_factory1_4.widget_pop_parameter_curve1,  # 对应UI中的曲线容器
            table_name="factory1_4_set_data_curve",
            params_config={
                'curve3': 'parameter3',
                'curve1': 'parameter1',
                'curve6': 'parameter6',
                'curve4': 'parameter4',
                'curve2': 'parameter2',
                'curve5': 'parameter5'
            },
            y_limits=(-1, 1)
        )
        self.curve_jcj_realtime4 = RealTimeJcjCurvePlotter(
            parent_widget=self.pop_dialog_factory1_4.widget_pop_parameter_curve2,  # 对应UI中的曲线容器
            table_name="factory1_4_realtime_data_jcj",
            params_config={
                'curve1': 'parameter3',
                'curve2': 'parameter4',
                'curve3': 'parameter5',
                'curve4': 'parameter6',
                'curve5': 'parameter9',
                'curve6': 'parameter10'
            },
            y_limits=(0, 200)
        )
        # 添加管径实时曲线（示例配置）
        self.curve_plotter_realtime5 = RealTimeCurvePlotter(
            parent_widget=self.pop_dialog_factory2_1.widget_pop_parameter_curve1,  # 对应UI中的曲线容器
            table_name="factory2_1_set_data_curve",
            params_config={
                'curve3': 'parameter3',
                'curve1': 'parameter1',
                'curve6': 'parameter6',
                'curve4': 'parameter4',
                'curve2': 'parameter2',
                'curve5': 'parameter5'
            },
            y_limits=(-1, 1)
        )
        self.curve_jcj_realtime5 = RealTimeJcjCurvePlotter(
            parent_widget=self.pop_dialog_factory2_1.widget_pop_parameter_curve2,  # 对应UI中的曲线容器
            table_name="factory2_1_realtime_data_jcj",
            params_config={
                'curve1': 'parameter3',
                'curve2': 'parameter4',
                'curve3': 'parameter5',
                'curve4': 'parameter6',
                'curve5': 'parameter9',
                'curve6': 'parameter10'
            },
            y_limits=(0, 200)
        )
        # 添加管径实时曲线（示例配置）
        self.curve_plotter_realtime6 = RealTimeCurvePlotter(
            parent_widget=self.pop_dialog_factory2_2.widget_pop_parameter_curve1,  # 对应UI中的曲线容器
            table_name="factory2__set_data_curve",
            params_config={
                'curve3': 'parameter3',
                'curve1': 'parameter1',
                'curve6': 'parameter6',
                'curve4': 'parameter4',
                'curve2': 'parameter2',
                'curve5': 'parameter5'
            },
            y_limits=(-1, 1)
        )
        self.curve_jcj_realtime6 = RealTimeJcjCurvePlotter(
            parent_widget=self.pop_dialog_factory2_2.widget_pop_parameter_curve2,  # 对应UI中的曲线容器
            table_name="factory2_2_realtime_data_jcj",
            params_config={
                'curve1': 'parameter3',
                'curve2': 'parameter4',
                'curve3': 'parameter5',
                'curve4': 'parameter6',
                'curve5': 'parameter9',
                'curve6': 'parameter10'
            },
            y_limits=(0, 200)
        )
        # 添加管径实时曲线（示例配置）
        self.curve_plotter_realtime7 = RealTimeCurvePlotter(
            parent_widget=self.pop_dialog_factory2_3.widget_pop_parameter_curve1,  # 对应UI中的曲线容器
            table_name="factory2_3_set_data_curve",
            params_config={
                'curve3': 'parameter3',
                'curve1': 'parameter1',
                'curve6': 'parameter6',
                'curve4': 'parameter4',
                'curve2': 'parameter2',
                'curve5': 'parameter5'
            },
            y_limits=(-1, 1)
        )
        self.curve_jcj_realtime7 = RealTimeJcjCurvePlotter(
            parent_widget=self.pop_dialog_factory2_3.widget_pop_parameter_curve2,  # 对应UI中的曲线容器
            table_name="factory2_3_realtime_data_jcj",
            params_config={
                'curve1': 'parameter3',
                'curve2': 'parameter4',
                'curve3': 'parameter5',
                'curve4': 'parameter6',
                'curve5': 'parameter9',
                'curve6': 'parameter10'
            },
            y_limits=(0, 200)
        )

        # 在初始化曲线后添加事件穿透设置
        self.curve_plotter1.canvas.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.curve_plotter2.canvas.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.curve_plotter3.canvas.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.curve_plotter4.canvas.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.curve_plotter5.canvas.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.curve_plotter6.canvas.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.curve_plotter7.canvas.setAttribute(Qt.WA_TransparentForMouseEvents, True)
    def _start_insert_threads(self):
        """启动所有数据采集线程"""
        # 工厂1设备1产量数据采集
        self._start_insert_thread(
            groups=[
                ("factory1_1_realtime_data_jcj", [
                    (11, 4, ["parameter1", "parameter2"]),
                    (21, 12, ["parameter3", "parameter4", "parameter5", "parameter6","parameter7","parameter8"]),
                    (1, 2, ["parameter9"]),
                    (5, 2, ["parameter10"]),
                    (7, 2, ["parameter11"])
                ]),
                ("factory1_1_realtime_data_fjj", [
                    (103, 2, ["parameter12"]),
                    (107, 4, ["parameter13", "parameter15"]),
                    (113, 2, ["parameter14"])
                ]),
                ("factory1_1_realtime_data_zdj", [
                    (201, 2, ["parameter16"]),
                    (221, 2, ["parameter17"]),
                    (203, 2, ["parameter18"]),
                    (231, 2, ["parameter19"]),
                    (235, 2, ["parameter20"]),
                    (239, 2, ["parameter21"])
                ]),
                ("factory1_1_set_data_curve", [
                    (203, 6, ["parameter3", "parameter1", "parameter2"]),
                    (103, 2, ["parameter4"]),
                    (209, 6, ["parameter7", "parameter5", "parameter6"])
                ]),
                ("factory1_1_set_data_jcj", [
                    (41, 10, ["parameter1", "parameter2", "parameter3", "parameter4", "parameter5"]),
                    (3, 2, ["parameter6"])
                ]),
                ("factory1_1_set_data_fjj", [
                    (101, 2, ["parameter1"]),
                    (105, 2, ["parameter2"]),
                    (123, 2, ["parameter3"])
                ]),
                ("factory1_1_set_data_zdj", [
                    (201, 2, ["parameter1"]),
                    (217, 2, ["parameter2"]),
                    (209, 2, ["parameter3"]),
                    (233, 2, ["parameter4"])
                ]),
                ("factory1_1_production_data", [
                    (231, 4, ["parameter1", "parameter2"]),
                    (237, 4, ["parameter3", "parameter4"]),
                    (1, 2, ["parameter5"])
                ]),
                ("factory1_1_alarm_data", [
                    (16, 1, ["parameter1"])
                ])
            ],
            ip="192.168.155.10"
        )
        # 工厂1设备2产量数据采集
        self._start_insert_thread(
            groups=[
                ("factory1_2_realtime_data_jcj", [
                    (11, 4, ["parameter1", "parameter2"]),
                    (21, 12, ["parameter3", "parameter4", "parameter5", "parameter6","parameter7","parameter8"]),
                    (1, 2, ["parameter9"]),
                    (5, 2, ["parameter10"]),
                    (7, 2, ["parameter11"])
                ]),
                ("factory1_2_realtime_data_fjj", [
                    (103, 2, ["parameter12"]),
                    (107, 4, ["parameter13", "parameter15"]),
                    (113, 2, ["parameter14"])
                ]),
                ("factory1_2_realtime_data_zdj", [
                    (201, 2, ["parameter16"]),
                    (221, 2, ["parameter17"]),
                    (203, 2, ["parameter18"]),
                    (231, 2, ["parameter19"]),
                    (235, 2, ["parameter20"]),
                    (239, 2, ["parameter21"])
                ]),
                ("factory1_2_set_data_curve", [
                    (203, 6, ["parameter3", "parameter1", "parameter2"]),
                    (103, 2, ["parameter4"]),
                    (209, 6, ["parameter7", "parameter5", "parameter6"])
                ]),
                ("factory1_2_set_data_jcj", [
                    (41, 10, ["parameter1", "parameter2", "parameter3", "parameter4", "parameter5"]),
                    (3, 2, ["parameter6"])
                ]),
                ("factory1_2_set_data_fjj", [
                    (101, 2, ["parameter1"]),
                    (105, 2, ["parameter2"]),
                    (123, 2, ["parameter3"])
                ]),
                ("factory1_2_set_data_zdj", [
                    (201, 2, ["parameter1"]),
                    (217, 2, ["parameter2"]),
                    (209, 2, ["parameter3"]),
                    (233, 2, ["parameter4"])
                ]),
                ("factory1_2_production_data", [
                    (231, 4, ["parameter1", "parameter2"]),
                    (237, 4, ["parameter3", "parameter4"]),
                    (1, 2, ["parameter5"])
                ]),
                ("factory1_2_alarm_data", [
                    (16, 1, ["parameter1"])
                ])
            ],
            ip="192.168.155.14"
        )
        # 工厂1设备3产量数据采集
        self._start_insert_thread(
            groups=[
                ("factory1_3_realtime_data_jcj", [
                    (11, 4, ["parameter1", "parameter2"]),
                    (21, 12, ["parameter3", "parameter4", "parameter5", "parameter6","parameter7","parameter8"]),
                    (1, 2, ["parameter9"]),
                    (5, 2, ["parameter10"]),
                    (7, 2, ["parameter11"])
                ]),
                ("factory1_3_realtime_data_fjj", [
                    (103, 2, ["parameter12"]),
                    (107, 4, ["parameter13", "parameter15"]),
                    (113, 2, ["parameter14"])
                ]),
                ("factory1_3_realtime_data_zdj", [
                    (201, 2, ["parameter16"]),
                    (221, 2, ["parameter17"]),
                    (203, 2, ["parameter18"]),
                    (231, 2, ["parameter19"]),
                    (235, 2, ["parameter20"]),
                    (239, 2, ["parameter21"])
                ]),
                ("factory1_3_set_data_curve", [
                    (203, 6, ["parameter3", "parameter1", "parameter2"]),
                    (103, 2, ["parameter4"]),
                    (209, 6, ["parameter7", "parameter5", "parameter6"])
                ]),
                ("factory1_3_set_data_jcj", [
                    (41, 10, ["parameter1", "parameter2", "parameter3", "parameter4", "parameter5"]),
                    (3, 2, ["parameter6"])
                ]),
                ("factory1_3_set_data_fjj", [
                    (101, 2, ["parameter1"]),
                    (105, 2, ["parameter2"]),
                    (123, 2, ["parameter3"])
                ]),
                ("factory1_3_set_data_zdj", [
                    (201, 2, ["parameter1"]),
                    (217, 2, ["parameter2"]),
                    (209, 2, ["parameter3"]),
                    (233, 2, ["parameter4"])
                ]),
                ("factory1_3_production_data", [
                    (231, 4, ["parameter1", "parameter2"]),
                    (237, 4, ["parameter3", "parameter4"]),
                    (1, 2, ["parameter5"])
                ]),
                ("factory1_3_alarm_data", [
                    (16, 1, ["parameter1"])
                ])
            ],
            ip="192.168.155.22"
        )
        # 工厂1设备4产量数据采集
        self._start_insert_thread(
            groups=[
                ("factory1_4_realtime_data_jcj", [
                    (11, 4, ["parameter1", "parameter2"]),
                    (21, 12, ["parameter3", "parameter4", "parameter5", "parameter6","parameter7","parameter8"]),
                    (1, 2, ["parameter9"]),
                    (5, 2, ["parameter10"]),
                    (7, 2, ["parameter11"])
                ]),
                ("factory1_4_realtime_data_fjj", [
                    (103, 2, ["parameter12"]),
                    (107, 4, ["parameter13", "parameter15"]),
                    (113, 2, ["parameter14"])
                ]),
                ("factory1_4_realtime_data_zdj", [
                    (201, 2, ["parameter16"]),
                    (221, 2, ["parameter17"]),
                    (203, 2, ["parameter18"]),
                    (231, 2, ["parameter19"]),
                    (235, 2, ["parameter20"]),
                    (239, 2, ["parameter21"])
                ]),
                ("factory1_4_set_data_curve", [
                    (203, 6, ["parameter3", "parameter1", "parameter2"]),
                    (103, 2, ["parameter4"]),
                    (209, 6, ["parameter7", "parameter5", "parameter6"])
                ]),
                ("factory1_4_set_data_jcj", [
                    (41, 10, ["parameter1", "parameter2", "parameter3", "parameter4", "parameter5"]),
                    (3, 2, ["parameter6"])
                ]),
                ("factory1_4_set_data_fjj", [
                    (101, 2, ["parameter1"]),
                    (105, 2, ["parameter2"]),
                    (123, 2, ["parameter3"])
                ]),
                ("factory1_4_set_data_zdj", [
                    (201, 2, ["parameter1"]),
                    (217, 2, ["parameter2"]),
                    (209, 2, ["parameter3"]),
                    (233, 2, ["parameter4"])
                ]),
                ("factory1_4_production_data", [
                    (231, 4, ["parameter1", "parameter2"]),
                    (237, 4, ["parameter3", "parameter4"]),
                    (1, 2, ["parameter5"])
                ]),
                ("factory1_4_alarm_data", [
                    (16, 1, ["parameter1"])
                ])
            ],
            ip="192.168.155.26"
        )
        # 工厂2设备1产量数据采集
        self._start_insert_thread(
            groups=[
                ("factory2_1_realtime_data_jcj", [
                    (11, 4, ["parameter1", "parameter2"]),
                    (21, 12, ["parameter3", "parameter4", "parameter5", "parameter6","parameter7","parameter8"]),
                    (1, 2, ["parameter9"]),
                    (5, 2, ["parameter10"]),
                    (7, 2, ["parameter11"])
                ]),
                ("factory2_1_realtime_data_fjj", [
                    (103, 2, ["parameter12"]),
                    (107, 4, ["parameter13", "parameter15"]),
                    (113, 2, ["parameter14"])
                ]),
                ("factory2_1_realtime_data_zdj", [
                    (201, 2, ["parameter16"]),
                    (221, 2, ["parameter17"]),
                    (203, 2, ["parameter18"]),
                    (231, 2, ["parameter19"]),
                    (235, 2, ["parameter20"]),
                    (239, 2, ["parameter21"])
                ]),
                ("factory2_1_set_data_curve", [
                    (203, 6, ["parameter3", "parameter1", "parameter2"]),
                    (103, 2, ["parameter4"]),
                    (209, 6, ["parameter7", "parameter5", "parameter6"])
                ]),
                ("factory2_1_set_data_jcj", [
                    (41, 10, ["parameter1", "parameter2", "parameter3", "parameter4", "parameter5"]),
                    (3, 2, ["parameter6"])
                ]),
                ("factory2_1_set_data_fjj", [
                    (101, 2, ["parameter1"]),
                    (105, 2, ["parameter2"]),
                    (123, 2, ["parameter3"])
                ]),
                ("factory2_1_set_data_zdj", [
                    (201, 2, ["parameter1"]),
                    (217, 2, ["parameter2"]),
                    (209, 2, ["parameter3"]),
                    (233, 2, ["parameter4"])
                ]),
                ("factory2_1_production_data", [
                    (231, 4, ["parameter1", "parameter2"]),
                    (237, 4, ["parameter3", "parameter4"]),
                    (1, 2, ["parameter5"])
                ]),
                ("factory2_1_alarm_data", [
                    (16, 1, ["parameter1"])
                ])
            ],
            ip="192.168.156.18"
        )
        # 工厂2设备2产量数据采集
        self._start_insert_thread(
            groups=[
                ("factory2_2_realtime_data_jcj", [
                    (11, 4, ["parameter1", "parameter2"]),
                    (21, 12, ["parameter3", "parameter4", "parameter5", "parameter6","parameter7","parameter8"]),
                    (1, 2, ["parameter9"]),
                    (5, 2, ["parameter10"]),
                    (7, 2, ["parameter11"])
                ]),
                ("factory2_2_realtime_data_fjj", [
                    (103, 2, ["parameter12"]),
                    (107, 4, ["parameter13", "parameter15"]),
                    (113, 2, ["parameter14"])
                ]),
                ("factory2_2_realtime_data_zdj", [
                    (201, 2, ["parameter16"]),
                    (221, 2, ["parameter17"]),
                    (203, 2, ["parameter18"]),
                    (231, 2, ["parameter19"]),
                    (235, 2, ["parameter20"]),
                    (239, 2, ["parameter21"])
                ]),
                ("factory2_2_set_data_curve", [
                    (203, 6, ["parameter3", "parameter1", "parameter2"]),
                    (103, 2, ["parameter4"]),
                    (209, 6, ["parameter7", "parameter5", "parameter6"])
                ]),
                ("factory2_2_set_data_jcj", [
                    (41, 10, ["parameter1", "parameter2", "parameter3", "parameter4", "parameter5"]),
                    (3, 2, ["parameter6"])
                ]),
                ("factory2_2_set_data_fjj", [
                    (101, 2, ["parameter1"]),
                    (105, 2, ["parameter2"]),
                    (123, 2, ["parameter3"])
                ]),
                ("factory2_2_set_data_zdj", [
                    (201, 2, ["parameter1"]),
                    (217, 2, ["parameter2"]),
                    (209, 2, ["parameter3"]),
                    (233, 2, ["parameter4"])
                ]),
                ("factory2_2_production_data", [
                    (231, 4, ["parameter1", "parameter2"]),
                    (237, 4, ["parameter3", "parameter4"]),
                    (1, 2, ["parameter5"])
                ]),
                ("factory2_2_alarm_data", [
                    (16, 1, ["parameter1"])
                ])
            ],
            ip="192.168.156.14"
        )
        # 工厂2设备3产量数据采集
        self._start_insert_thread(
            groups=[
                ("factory2_3_realtime_data_jcj", [
                    (11, 4, ["parameter1", "parameter2"]),
                    (21, 12, ["parameter3", "parameter4", "parameter5", "parameter6","parameter7","parameter8"]),
                    (1, 2, ["parameter9"]),
                    (5, 2, ["parameter10"]),
                    (7, 2, ["parameter11"])
                ]),
                ("factory2_3_realtime_data_fjj", [
                    (103, 2, ["parameter12"]),
                    (107, 4, ["parameter13", "parameter15"]),
                    (113, 2, ["parameter14"])
                ]),
                ("factory2_3_realtime_data_zdj", [
                    (201, 2, ["parameter16"]),
                    (221, 2, ["parameter17"]),
                    (203, 2, ["parameter18"]),
                    (231, 2, ["parameter19"]),
                    (235, 2, ["parameter20"]),
                    (239, 2, ["parameter21"])
                ]),
                ("factory2_3_set_data_curve", [
                    (203, 6, ["parameter3", "parameter1", "parameter2"]),
                    (103, 2, ["parameter4"]),
                    (209, 6, ["parameter7", "parameter5", "parameter6"])
                ]),
                ("factory2_3_set_data_jcj", [
                    (41, 10, ["parameter1", "parameter2", "parameter3", "parameter4", "parameter5"]),
                    (3, 2, ["parameter6"])
                ]),
                ("factory2_3_set_data_fjj", [
                    (101, 2, ["parameter1"]),
                    (105, 2, ["parameter2"]),
                    (123, 2, ["parameter3"])
                ]),
                ("factory2_3_set_data_zdj", [
                    (201, 2, ["parameter1"]),
                    (217, 2, ["parameter2"]),
                    (209, 2, ["parameter3"]),
                    (233, 2, ["parameter4"])
                ]),
                ("factory2_3_production_data", [
                    (231, 4, ["parameter1", "parameter2"]),
                    (237, 4, ["parameter3", "parameter4"]),
                    (1, 2, ["parameter5"])
                ]),
                ("factory2_3_alarm_data", [
                    (16, 1, ["parameter1"])
                ])
            ],
            ip="192.168.156.22"
        )
    # ------------------------- 线程启动方法 -------------------------
    def _start_insert_thread(self, groups, ip):
        """启动异步插入线程的方法（工厂方法）"""
        # 创建唯一标识符（示例使用第一个表名）
        table_names = [g[0] for g in groups]
        key = "_".join(table_names)

        # 检查是否已存在相同线程
        if key in self.threads:
            return
        # 创建线程对象（QThread实例）
        thread = QThread()
        # 创建工作线程实例，传递表名、组配置和IP地址
        worker = InsertWorker(groups, ip)

        # 将工作对象移动到新线程（关键步骤：让worker在子线程运行）
        worker.moveToThread(thread)

        # 信号连接（线程启动时触发工作对象的run方法）
        thread.started.connect(worker.run)  # type: ignore[attr-defined]
        # 工作完成时退出线程（finished信号来自worker）
        worker.finished.connect(thread.quit)  # type: ignore[attr-defined]
        # 工作完成后销毁worker对象
        worker.finished.connect(worker.deleteLater)  # type: ignore[attr-defined]
        # 线程退出后销毁线程对象
        thread.finished.connect(thread.deleteLater)  # type: ignore[attr-defined]

        # 存储线程引用（防止被Python垃圾回收）
        self.threads[key] = (thread, worker) # 使用字符串作为键
        # 启动线程（开始执行事件循环）
        thread.start()
    # 添加新方法：启动数据更新线程
    def _start_data_update_thread(self, tables_to_monitor):
        """启动数据更新线程
        参数:
            tables_to_monitor: 需要监控的表名列表
        """
        # 创建线程对象
        thread = QThread()
        # 创建工作线程实例
        worker = DataUpdateWorker(tables_to_monitor)

        # 将工作对象移动到新线程
        worker.moveToThread(thread)

        # 信号连接
        thread.started.connect(worker.run)  # type: ignore[attr-defined]# 线程启动时执行run方法
        worker.finished.connect(thread.quit)  # type: ignore[attr-defined]# 工作完成时退出线程
        worker.finished.connect(worker.deleteLater)  # type: ignore[attr-defined]# 工作完成后销毁worker对象
        thread.finished.connect(thread.deleteLater)  # type: ignore[attr-defined]# 线程退出后销毁线程对象

        # 连接数据更新信号到处理方法
        worker.data_updated.connect(self._handle_data_update)   # type: ignore[attr-defined]

        # 存储线程引用
        self.threads['data_update'] = (thread, worker)

        # 启动线程
        thread.start()

    # 添加新方法：处理数据更新
    def _handle_data_update(self, table_name, data):
        """处理从子线程接收到的数据更新
        参数:
            table_name: 表名
            data: 数据字典
        """
        # 创建策略映射字典（与原来相同）
        update_strategies = {
            "factory1_1_set_data_curve": [self._update_curve1_realtime, self.curve_plotter1.update_plot, self.curve_plotter_realtime1.update_plot],
            "factory1_2_set_data_curve": [self._update_curve2_realtime, self.curve_plotter2.update_plot, self.curve_plotter_realtime2.update_plot],
            "factory1_3_set_data_curve": [self._update_curve3_realtime, self.curve_plotter3.update_plot, self.curve_plotter_realtime3.update_plot],
            "factory1_4_set_data_curve": [self._update_curve4_realtime, self.curve_plotter4.update_plot, self.curve_plotter_realtime4.update_plot],
            "factory2_1_set_data_curve": [self._update_curve5_realtime, self.curve_plotter5.update_plot, self.curve_plotter_realtime5.update_plot],
            "factory2_2_set_data_curve": [self._update_curve6_realtime, self.curve_plotter6.update_plot, self.curve_plotter_realtime6.update_plot],
            "factory2_3_set_data_curve": [self._update_curve7_realtime, self.curve_plotter7.update_plot, self.curve_plotter_realtime7.update_plot],
            "factory1_1_realtime_data_jcj": self.curve_jcj_realtime1.update_jcj_plot,
            "factory1_2_realtime_data_jcj": self.curve_jcj_realtime2.update_jcj_plot,
            "factory1_3_realtime_data_jcj": self.curve_jcj_realtime3.update_jcj_plot,
            "factory1_4_realtime_data_jcj": self.curve_jcj_realtime4.update_jcj_plot,
            "factory2_1_realtime_data_jcj": self.curve_jcj_realtime5.update_jcj_plot,
            "factory2_2_realtime_data_jcj": self.curve_jcj_realtime6.update_jcj_plot,
            "factory2_3_realtime_data_jcj": self.curve_jcj_realtime7.update_jcj_plot
        }

        # 获取并执行对应的更新策略
        if strategy := update_strategies.get(table_name):
            if isinstance(strategy, list):  # 处理多个方法的情况
                for method in strategy:
                    method(data)    # type: ignore[attr-defined]
            else:
                strategy(data)  # type: ignore[attr-defined]
    # 分解原有的大更新方法为多个私有方法
    def _update_curve1_realtime(self, data):
        """更新挤出机实时数据"""
        self.curve1_lable2.setText(str(data.get('parameter1', '')))
        self.curve1_lable4.setText(str(data.get('parameter2', '')))
        self.curve1_lable6.setText(str(data.get('parameter3', '')))
        self.curve1_lable8.setText(str(data.get('parameter4', '')))
        self.curve1_lable10.setText(str(data.get('parameter5', '')))    # 使用get方法提供默认值
    def _update_curve2_realtime(self, data):
        """更新挤出机实时数据"""
        self.curve2_lable2.setText(str(data.get('parameter1', '')))
        self.curve2_lable4.setText(str(data.get('parameter2', '')))
        self.curve2_lable6.setText(str(data.get('parameter3', '')))
        self.curve2_lable8.setText(str(data.get('parameter4', '')))
        self.curve2_lable10.setText(str(data.get('parameter5', '')))    # 使用get方法提供默认值
    def _update_curve3_realtime(self, data):
        """更新挤出机实时数据"""
        self.curve3_lable2.setText(str(data.get('parameter1', '')))
        self.curve3_lable4.setText(str(data.get('parameter2', '')))
        self.curve3_lable6.setText(str(data.get('parameter3', '')))
        self.curve3_lable8.setText(str(data.get('parameter4', '')))
        self.curve3_lable10.setText(str(data.get('parameter5', '')))    # 使用get方法提供默认值
    def _update_curve4_realtime(self, data):
        """更新挤出机实时数据"""
        self.curve4_lable2.setText(str(data.get('parameter1', '')))
        self.curve4_lable4.setText(str(data.get('parameter2', '')))
        self.curve4_lable6.setText(str(data.get('parameter3', '')))
        self.curve4_lable8.setText(str(data.get('parameter4', '')))
        self.curve4_lable10.setText(str(data.get('parameter5', '')))    # 使用get方法提供默认值
    def _update_curve5_realtime(self, data):
        """更新挤出机实时数据"""
        self.curve5_lable2.setText(str(data.get('parameter1', '')))
        self.curve5_lable4.setText(str(data.get('parameter2', '')))
        self.curve5_lable6.setText(str(data.get('parameter3', '')))
        self.curve5_lable8.setText(str(data.get('parameter4', '')))
        self.curve5_lable10.setText(str(data.get('parameter5', '')))    # 使用get方法提供默认值
    def _update_curve6_realtime(self, data):
        """更新挤出机实时数据"""
        self.curve6_lable2.setText(str(data.get('parameter1', '')))
        self.curve6_lable4.setText(str(data.get('parameter2', '')))
        self.curve6_lable6.setText(str(data.get('parameter3', '')))
        self.curve6_lable8.setText(str(data.get('parameter4', '')))
        self.curve6_lable10.setText(str(data.get('parameter5', '')))    # 使用get方法提供默认值
    def _update_curve7_realtime(self, data):
        """更新挤出机实时数据"""
        self.curve7_lable2.setText(str(data.get('parameter1', '')))
        self.curve7_lable4.setText(str(data.get('parameter2', '')))
        self.curve7_lable6.setText(str(data.get('parameter3', '')))
        self.curve7_lable8.setText(str(data.get('parameter4', '')))
        self.curve7_lable10.setText(str(data.get('parameter5', '')))    # 使用get方法提供默认值

    def minimize_all_windows(self):
        """最小化所有窗口的方法"""
        # 隐藏所有弹出窗口
        # 使用正确的变量名引用弹窗实例
        if hasattr(self, 'pop_dialog') and self.pop_dialog.isVisible():
            self.pop_dialog.hide()
        if hasattr(self, 'pop_dialog_factory1_2') and self.pop_dialog_factory1_2.isVisible():
            self.pop_dialog_factory1_2.hide()
        if hasattr(self, 'pop_dialog_factory1_3') and self.pop_dialog_factory1_3.isVisible():
            self.pop_dialog_factory1_3.hide()
        if hasattr(self, 'pop_dialog_factory1_4') and self.pop_dialog_factory1_4.isVisible():
            self.pop_dialog_factory1_4.hide()
        if hasattr(self, 'pop_dialog_factory2_1') and self.pop_dialog_factory2_1.isVisible():
            self.pop_dialog_factory2_1.hide()
        if hasattr(self, 'pop_dialog_factory2_2') and self.pop_dialog_factory2_2.isVisible():
            self.pop_dialog_factory2_2.hide()
        if hasattr(self, 'pop_dialog_factory2_3') and self.pop_dialog_factory2_3.isVisible():
            self.pop_dialog_factory2_3.hide()

        # 隐藏历史参数弹窗
        if hasattr(self, 'dialog_historical') and self.dialog_historical.isVisible():
            self.dialog_historical.hide()
        if hasattr(self, 'dialog_historical_factory1_2') and self.dialog_historical_factory1_2.isVisible():
            self.dialog_historical_factory1_2.hide()
        if hasattr(self, 'dialog_historical_factory1_3') and self.dialog_historical_factory1_3.isVisible():
            self.dialog_historical_factory1_3.hide()
        if hasattr(self, 'dialog_historical_factory1_4') and self.dialog_historical_factory1_4.isVisible():
            self.dialog_historical_factory1_4.hide()
        if hasattr(self, 'dialog_historical_factory2_1') and self.dialog_historical_factory2_1.isVisible():
            self.dialog_historical_factory2_1.hide()
        if hasattr(self, 'dialog_historical_factory2_2') and self.dialog_historical_factory2_2.isVisible():
            self.dialog_historical_factory2_2.hide()
        if hasattr(self, 'dialog_historical_factory2_3') and self.dialog_historical_factory2_3.isVisible():
            self.dialog_historical_factory2_3.hide()

        # 隐藏报警弹窗
        if hasattr(self, 'pop_alarm_dialog') and self.pop_alarm_dialog.isVisible():
            self.pop_alarm_dialog.hide()

        # 最小化主窗口
        self.showMinimized()

    def close_all_windows(self):
        """关闭所有窗口的方法"""
        # 停止所有线程
        if hasattr(self, 'threads'):
            for key, (thread, worker) in self.threads.items():
                if hasattr(worker, 'stop'):
                    try:
                        worker.stop()  # 停止工作线程
                    except Exception as e:
                        print(f"停止线程时出错: {e}")
                thread.quit()  # 退出线程
                thread.wait(1000)  # 等待线程退出，最多等待1秒

        # 关闭所有参数弹窗
        if hasattr(self, 'pop_dialog'):
            self.pop_dialog.close()
        if hasattr(self, 'pop_dialog_factory1_2'):
            self.pop_dialog_factory1_2.close()
        if hasattr(self, 'pop_dialog_factory1_3'):
            self.pop_dialog_factory1_3.close()
        if hasattr(self, 'pop_dialog_factory1_4'):
            self.pop_dialog_factory1_4.close()
        if hasattr(self, 'pop_dialog_factory2_1'):
            self.pop_dialog_factory2_1.close()
        if hasattr(self, 'pop_dialog_factory2_2'):
            self.pop_dialog_factory2_2.close()
        if hasattr(self, 'pop_dialog_factory2_3'):
            self.pop_dialog_factory2_3.close()

        # 关闭所有历史参数弹窗
        if hasattr(self, 'dialog_historical'):
            self.dialog_historical.close()
        if hasattr(self, 'dialog_historical_factory1_2'):
            self.dialog_historical_factory1_2.close()
        if hasattr(self, 'dialog_historical_factory1_3'):
            self.dialog_historical_factory1_3.close()
        if hasattr(self, 'dialog_historical_factory1_4'):
            self.dialog_historical_factory1_4.close()
        if hasattr(self, 'dialog_historical_factory2_1'):
            self.dialog_historical_factory2_1.close()
        if hasattr(self, 'dialog_historical_factory2_2'):
            self.dialog_historical_factory2_2.close()
        if hasattr(self, 'dialog_historical_factory2_3'):
            self.dialog_historical_factory2_3.close()

        # 关闭报警弹窗
        if hasattr(self, 'pop_alarm_dialog'):
            self.pop_alarm_dialog.close()

        # 关闭主窗口
        self.close()

    @staticmethod  # 静态方法，不依赖实例对象
    def get_localtime():
        """获取本地时间的静态方法"""
        from datetime import datetime, timedelta
        now = datetime.now()  # 获取当前时间对象
        start_time = now - timedelta(minutes=10)  # 计算起始时间（当前时间向前10分钟）
        # 返回格式化后的日期和时间字符串
        return now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"),start_time.strftime("%H:%M:%S")

    def update_time(self):
        """更新时间显示的方法"""
        date_str, time_str , start_time= self.get_localtime()  # 解包日期时间
        self.title_DATA.setText(date_str)  # 更新日期标签
        self.title_time.setText(time_str)  # 更新时间标签
        self.curve1_lable9_14.setText(start_time)  # 更新1#曲线起始时间标签
        self.curve1_lable9_20.setText(start_time)  # 更新2#曲线起始时间标签
        self.curve1_lable9_24.setText(start_time)  # 更新3#曲线起始时间标签
        self.curve1_lable9_28.setText(start_time)  # 更新4#曲线起始时间标签
        self.curve1_lable9_32.setText(start_time)  # 更新5#曲线起始时间标签
        self.curve1_lable9_36.setText(start_time)  # 更新6#曲线起始时间标签
        self.curve1_lable9_39.setText(start_time)  # 更新7#曲线起始时间标签
        self.curve1_lable9_15.setText(time_str)  # 更新1#曲线截止时间标签
        self.curve1_lable9_21.setText(time_str)  # 更新2#曲线截止时间标签
        self.curve1_lable9_25.setText(time_str)  # 更新3#曲线截止时间标签
        self.curve1_lable9_29.setText(time_str)  # 更新4#曲线截止时间标签
        self.curve1_lable9_33.setText(time_str)  # 更新5#曲线截止时间标签
        self.curve1_lable9_37.setText(time_str)  # 更新6#曲线截止时间标签
        self.curve1_lable9_38.setText(time_str)  # 更新7#曲线截止时间标签

    def show_pop_parameter(self, event):
        """显示参数弹窗的槽函数"""
        # 检查弹窗是否已存在
        if self.pop_dialog:
            # 如果弹窗已最小化或隐藏，则恢复显示
            if self.pop_dialog.isMinimized():
                self.pop_dialog.showNormal()  # 从最小化状态恢复
            elif not self.pop_dialog.isVisible():
                self.pop_dialog.show()  # 如果不可见则显示
            # 如果已经可见，则将其置于前台
            self.pop_dialog.activateWindow()  # 激活窗口（置于前台）
            self.pop_dialog.raise_()  # 提升窗口层级
        event.accept()  # 接受事件，阻止进一步传播
    def show_pop_parameter_factory1_2(self, event):
        """显示参数弹窗的槽函数"""
        # 检查弹窗是否已存在
        if self.pop_dialog_factory1_2:
            # 如果弹窗已最小化或隐藏，则恢复显示
            if self.pop_dialog_factory1_2.isMinimized():
                self.pop_dialog_factory1_2.showNormal()  # 从最小化状态恢复
            elif not self.pop_dialog_factory1_2.isVisible():
                self.pop_dialog_factory1_2.show()  # 如果不可见则显示
            # 如果已经可见，则将其置于前台
            self.pop_dialog_factory1_2.activateWindow()  # 激活窗口（置于前台）
            self.pop_dialog_factory1_2.raise_()  # 提升窗口层级
        event.accept()  # 接受事件，阻止进一步传播
    def show_pop_parameter_factory1_3(self, event):
        """显示参数弹窗的槽函数"""
        # 检查弹窗是否已存在
        if self.pop_dialog_factory1_3:
            # 如果弹窗已最小化或隐藏，则恢复显示
            if self.pop_dialog_factory1_3.isMinimized():
                self.pop_dialog_factory1_3.showNormal()  # 从最小化状态恢复
            elif not self.pop_dialog_factory1_3.isVisible():
                self.pop_dialog_factory1_3.show()  # 如果不可见则显示
            # 如果已经可见，则将其置于前台
            self.pop_dialog_factory1_3.activateWindow()  # 激活窗口（置于前台）
            self.pop_dialog_factory1_3.raise_()  # 提升窗口层级
        event.accept()  # 接受事件，阻止进一步传播
    def show_pop_parameter_factory1_4(self, event):
        """显示参数弹窗的槽函数"""
        # 检查弹窗是否已存在
        if self.pop_dialog_factory1_4:
            # 如果弹窗已最小化或隐藏，则恢复显示
            if self.pop_dialog_factory1_4.isMinimized():
                self.pop_dialog_factory1_4.showNormal()  # 从最小化状态恢复
            elif not self.pop_dialog_factory1_4.isVisible():
                self.pop_dialog_factory1_4.show()  # 如果不可见则显示
            # 如果已经可见，则将其置于前台
            self.pop_dialog_factory1_4.activateWindow()  # 激活窗口（置于前台）
            self.pop_dialog_factory1_4.raise_()  # 提升窗口层级
        event.accept()  # 接受事件，阻止进一步传播
    def show_pop_parameter_factory2_1(self, event):
        """显示参数弹窗的槽函数"""
        # 检查弹窗是否已存在
        if self.pop_dialog_factory2_1:
            # 如果弹窗已最小化或隐藏，则恢复显示
            if self.pop_dialog_factory2_1.isMinimized():
                self.pop_dialog_factory2_1.showNormal()  # 从最小化状态恢复
            elif not self.pop_dialog_factory2_1.isVisible():
                self.pop_dialog_factory2_1.show()  # 如果不可见则显示
            # 如果已经可见，则将其置于前台
            self.pop_dialog_factory2_1.activateWindow()  # 激活窗口（置于前台）
            self.pop_dialog_factory2_1.raise_()  # 提升窗口层级
        event.accept()  # 接受事件，阻止进一步传播
    def show_pop_parameter_factory2_2(self, event):
        """显示参数弹窗的槽函数"""
        # 检查弹窗是否已存在
        if self.pop_dialog_factory2_2:
            # 如果弹窗已最小化或隐藏，则恢复显示
            if self.pop_dialog_factory2_2.isMinimized():
                self.pop_dialog_factory2_2.showNormal()  # 从最小化状态恢复
            elif not self.pop_dialog_factory2_2.isVisible():
                self.pop_dialog_factory2_2.show()  # 如果不可见则显示
            # 如果已经可见，则将其置于前台
            self.pop_dialog_factory2_2.activateWindow()  # 激活窗口（置于前台）
            self.pop_dialog_factory2_2.raise_()  # 提升窗口层级
        event.accept()  # 接受事件，阻止进一步传播
    def show_pop_parameter_factory2_3(self, event):
        """显示参数弹窗的槽函数"""
        # 检查弹窗是否已存在
        if self.pop_dialog_factory2_3:
            # 如果弹窗已最小化或隐藏，则恢复显示
            if self.pop_dialog_factory2_3.isMinimized():
                self.pop_dialog_factory2_3.showNormal()  # 从最小化状态恢复
            elif not self.pop_dialog_factory2_3.isVisible():
                self.pop_dialog_factory2_3.show()  # 如果不可见则显示
            # 如果已经可见，则将其置于前台
            self.pop_dialog_factory2_3.activateWindow()  # 激活窗口（置于前台）
            self.pop_dialog_factory2_3.raise_()  # 提升窗口层级
        event.accept()  # 接受事件，阻止进一步传播
    def show_pop_alarm(self, event):
        """显示报警弹窗的槽函数"""
        # 检查弹窗是否已存在
        if self.pop_alarm_dialog:
            # 如果弹窗已最小化或隐藏，则恢复显示
            if self.pop_alarm_dialog.isMinimized():
                self.pop_alarm_dialog.showNormal()  # 从最小化状态恢复
            elif not self.pop_alarm_dialog.isVisible():
                self.pop_alarm_dialog.show()  # 如果不可见则显示
            # 如果已经可见，则将其置于前台
            self.pop_alarm_dialog.activateWindow()  # 激活窗口（置于前台）
            self.pop_alarm_dialog.raise_()  # 提升窗口层级
        event.accept()  # 接受事件，阻止进一步传播

    # 重写关闭事件，确保线程正确停止
    # 添加closeEvent方法，确保通过系统关闭按钮关闭时也能级联关闭所有窗口
    def closeEvent(self, event):
        """处理关闭事件：关闭所有已打开的窗口"""
        # 停止所有线程
        if hasattr(self, 'threads'):
            for key, (thread, worker) in self.threads.items():
                if hasattr(worker, 'stop'):
                    try:
                        worker.stop()  # 停止工作线程
                    except Exception as e:
                        print(f"停止线程时出错: {e}")
                thread.quit()  # 退出线程
                thread.wait(1000)  # 等待线程退出，最多等待1秒

        # 关闭所有参数弹窗
        if hasattr(self, 'pop_dialog'):
            self.pop_dialog.close()
        if hasattr(self, 'pop_dialog_factory1_2'):
            self.pop_dialog_factory1_2.close()
        if hasattr(self, 'pop_dialog_factory1_3'):
            self.pop_dialog_factory1_3.close()
        if hasattr(self, 'pop_dialog_factory1_4'):
            self.pop_dialog_factory1_4.close()
        if hasattr(self, 'pop_dialog_factory2_1'):
            self.pop_dialog_factory2_1.close()
        if hasattr(self, 'pop_dialog_factory2_2'):
            self.pop_dialog_factory2_2.close()
        if hasattr(self, 'pop_dialog_factory2_3'):
            self.pop_dialog_factory2_3.close()

        # 关闭所有历史参数弹窗
        if hasattr(self, 'dialog_historical'):
            self.dialog_historical.close()
        if hasattr(self, 'dialog_historical_factory1_2'):
            self.dialog_historical_factory1_2.close()
        if hasattr(self, 'dialog_historical_factory1_3'):
            self.dialog_historical_factory1_3.close()
        if hasattr(self, 'dialog_historical_factory1_4'):
            self.dialog_historical_factory1_4.close()
        if hasattr(self, 'dialog_historical_factory2_1'):
            self.dialog_historical_factory2_1.close()
        if hasattr(self, 'dialog_historical_factory2_2'):
            self.dialog_historical_factory2_2.close()
        if hasattr(self, 'dialog_historical_factory2_3'):
            self.dialog_historical_factory2_3.close()

        # 关闭报警弹窗
        if hasattr(self, 'pop_alarm_dialog'):
            self.pop_alarm_dialog.close()

        # 调用父类的关闭事件处理
        super().closeEvent(event)

# ---------------------------------数据更新工作线程类---------------------------------
class DataUpdateWorker(QObject):
    """数据更新工作线程类，负责从数据库获取数据并发送信号"""
    # 定义信号，用于将获取的数据传递给主线程
    data_updated = pyqtSignal(str, dict)  # 参数：表名和数据字典
    finished = pyqtSignal()  # 完成信号

    def __init__(self, tables_to_monitor):
        """初始化数据更新工作线程
        参数:
            data_manager: 数据管理器实例
            tables_to_monitor: 需要监控的表名列表
        """
        super().__init__()
        self.data_manager = data_manager
        self.tables_to_monitor = tables_to_monitor
        self.running = True
        # 存储本地缓存的版本号
        self.data_versions = {table: 0 for table in self.tables_to_monitor}

    def run(self):
        """线程运行方法，定期检查数据库更新"""
        while self.running:
            # 获取所有表的当前版本号
            current_versions = self.data_manager.get_data_versions()

            # 检查每个监控的表是否有更新
            for table_name in self.tables_to_monitor:
                if table_name in current_versions and current_versions[table_name] > self.data_versions[table_name]:
                    # 获取表的最新数据
                    data = self.data_manager.get_realtime_data(table_name)
                    if data:  # 确保数据有效
                        # 发送信号，将表名和数据传递给主线程
                        self.data_updated.emit(table_name, data)    # type: ignore[attr-defined]
                    # 更新本地版本号
                    self.data_versions[table_name] = current_versions[table_name]

            # 短暂休眠，避免过度占用CPU
            QThread.msleep(100)  # 休眠100毫秒

    def stop(self):
        """停止线程运行"""
        self.running = False
        self.finished.emit()    # type: ignore[attr-defined]
# ---------------------------------数据库异步，工作线程类---------------------------------
class InsertWorker(QObject):
    """执行实际插入操作的工作类（必须在主线程外运行）"""
    # 定义完成信号（无参数）
    finished = pyqtSignal()

    def __init__(self, groups, ip, port=502):
        """构造函数（参数来自_start_insert_thread）"""
        super().__init__()  # 必须调用父类构造函数
        # self.table_name = table_name  # 要操作的数据表名
        self.groups = groups  # 组配置参数
        self.ip = ip  # 网络设备IP地址
        self.port = port
        self.sock = None  # 持久化socket连接
        self.keep_running = True
        self.inserter = inserter
        self.int_inserter = inserter


    # 新增连接初始化方法
    def init_connection(self):
        if not self.sock:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                self.sock.settimeout(5)
                self.sock.connect((self.ip, self.port))
                print(f"成功建立到 {self.ip}:{self.port} 的持久连接\n")
                return True
            except Exception as e:
                print(f"连接建立失败: {str(e)}")
                self.sock = None
                return False
        return True
    def run(self):# 定义线程运行方法(处理整数数据)
        # 导入sleep函数用于线程休眠
        from time import sleep
        # 开始异常捕获(最外层)
        try:
            while self.keep_running:    # 主循环，当keep_running为True时持续运行
                try:    # 中层异常捕获(连接和数据采集)
                    if not self.init_connection():  # 尝试初始化连接
                        sleep(1)  # 连接失败则休眠1秒
                        continue  # 跳过本次循环，重新尝试

                    # 新调用方式（一次处理所有表）
                    success = self.inserter.insert_multiple_tables_data(
                        table_groups=self.groups,   # 寄存器组配置
                        sock=self.sock  # 已建立的socket连接
                    )
                    sleep(0.5)

                    if not success:  # 如果插入失败
                        self.reconnect()  # 执行重连
                        sleep(0.5)

                except (socket.timeout, ConnectionResetError) as e:
                    print(f"连接异常: {str(e)}")
                    self.reconnect()
                    sleep(1)
                    # break  # 跳出当前组循环，重新开始
                except Exception as e:
                    print(f"运行时异常: {str(e)}")
                    sleep(1)

        finally:    # 无论是否发生异常都会执行的代码块
            self.cleanup()  # 清理socket连接等资源
            self.finished.emit()    # type: ignore[attr-defined]# 发射完成信号通知主线程
    # def run_int(self):  # 定义线程运行方法(处理整数数据)
    #     from time import sleep  # 导入sleep函数用于线程休眠
    #
    #     try:  # 开始异常捕获(最外层)
    #         while self.keep_running:  # 主循环，当keep_running为True时持续运行
    #             try:  # 中层异常捕获(连接和数据采集)
    #                 if not self.init_connection():  # 尝试初始化连接
    #                     sleep(1)  # 连接失败则休眠1秒
    #                     continue  # 跳过本次循环，重新尝试
    #
    #                 # 遍历所有组配置(每个设备可能有多个寄存器组)
    #                 for group_config in self.groups:
    #                     # 解包组配置(表名和寄存器组)
    #                     table_name, groups = group_config
    #
    #                     try:  # 最内层异常捕获(单个寄存器组操作)
    #                         # 调用数据插入器插入整数数据
    #                         success = self.int_inserter.insert_combined_mcgs_int_data(
    #                             table_name=table_name,  # 目标表名
    #                             groups=groups,  # 寄存器组配置
    #                             ip=self.ip,  # 设备IP地址
    #                             port=self.port,  # 设备端口
    #                             sock=self.sock  # 已建立的socket连接
    #                         )
    #
    #                         if not success:  # 如果插入失败
    #                             self.reconnect()  # 执行重连
    #
    #                     # 捕获网络相关异常(超时/连接重置)
    #                     except (socket.timeout, ConnectionResetError) as e:
    #                         print(f"连接异常: {str(e)}，尝试重连...")
    #                         self.reconnect()  # 执行重连
    #                         sleep(1)  # 重连后等待1秒
    #                         break  # 跳出当前组循环，重新开始
    #
    #                     # 捕获其他运行时异常
    #                     except Exception as e:
    #                         print(f"运行时异常: {str(e)}")
    #                         sleep(1)  # 异常后等待1秒
    #
    #             # 捕获主循环中的其他异常
    #             except Exception as e:
    #                 print(f"主循环异常: {str(e)}")
    #                 sleep(1)  # 异常后等待1秒
    #
    #     finally:  # 无论是否发生异常都会执行的代码块
    #         self.cleanup()  # 清理socket连接等资源
    #         self.finished.emit()  # type: ignore[attr-defined]# 发射完成信号通知主线程
    def reconnect(self):
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
            self.sock = None
        print("尝试重新连接...")
        self.init_connection()

    def cleanup(self):
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
            self.sock = None

    def stop(self):
        self.keep_running = False
        self.cleanup()

# ---------------------------------参数弹窗历史数据查询工作线程类---------------------------------
class HistoricalDataQueryWorker(QObject):
    """执行历史数据查询的工作线程类"""
    # 定义信号，用于将查询结果传递给主线程
    data_ready = pyqtSignal(dict)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, tables, exact_time, start_time, end_time):
        """初始化历史数据查询工作线程
        Args:
            tables: 要查询的表名列表
            exact_time: 精确时间点
            start_time: 查询开始时间
            end_time: 查询结束时间
        """
        super().__init__()
        self.tables = tables
        self.exact_time = exact_time
        self.start_time = start_time
        self.end_time = end_time
        # 创建历史数据管理器实例
        self.hist_data_manager = historical_data_manager

    def run(self):
        """执行历史数据查询任务"""
        try:
            # 存储所有查询结果的字典
            result_data = {}

            # 遍历所有目标数据表
            for table in self.tables:
                # 执行精确时间点查询
                data = self.hist_data_manager.get_nearest_data(
                    table,
                    self.exact_time,
                    self.start_time,
                    self.end_time
                )
                # 存储查询结果
                result_data[table] = data

            # 发送查询结果信号
            self.data_ready.emit(result_data) # type: ignore[attr-defined]
        except Exception as e:
            print(f"历史数据查询异常: {str(e)}")
            self.error.emit(f"查询失败: {str(e)}")  # type: ignore[attr-defined]
        finally:
            # 发送完成信号
            self.finished.emit()    # type: ignore[attr-defined]

# ---------------------------------报警历史查询工作线程类---------------------------------
class AlarmHistoryQueryWorker(QObject):
    """执行报警历史数据查询的工作线程类"""
    # 定义信号，用于将查询结果传递给主线程
    data_ready = pyqtSignal(list)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, alarm_tables, start_time_str, end_time_str):
        """初始化报警历史数据查询工作线程
        Args:
            alarm_tables: 要查询的报警表名列表
            start_time_str: 查询开始时间字符串
            end_time_str: 查询结束时间字符串
        """
        super().__init__()
        self.alarm_tables = alarm_tables
        self.start_time_str = start_time_str
        self.end_time_str = end_time_str
        # 创建历史数据管理器实例
        self.hist_data_manager = historical_data_manager

    def run(self):
        """执行报警历史数据查询任务"""
        try:
            # 存储所有查询到的报警记录
            all_alarms = []

            # 遍历所有报警表
            for table_name in self.alarm_tables:
                # 查询指定时间段内的报警数据
                alarm_data = self.hist_data_manager.get_historical_data(
                    table_name,
                    self.start_time_str,
                    self.end_time_str
                )

                # 如果查询到数据
                if alarm_data:
                    for record in alarm_data:
                        # 获取报警值
                        alarm_value = record.get('parameter1')

                        # 如果报警值为0或空，则跳过
                        if not alarm_value:
                            continue

                        # 获取记录时间
                        record_time = record.get('timestamp', self.start_time_str)
                        if isinstance(record_time, datetime):
                            record_time = record_time.strftime("%Y-%m-%d %H:%M:%S")

                        # 解析表名获取工厂和设备信息
                        parts = table_name.split('_')
                        factory = parts[0]
                        device = parts[1] if len(parts) > 1 else "未知设备"

                        # 根据报警值获取报警内容
                        alarm_content = self._get_alarm_content(alarm_value)

                        # 构建报警显示文本
                        alarm_text = f"[{record_time}] {factory}-{device}: {alarm_content}"

                        # 添加到报警列表
                        all_alarms.append((record_time, alarm_text))

            # 按时间排序报警记录（从新到旧）
            all_alarms.sort(key=lambda x: x[0], reverse=True)

            # 发送查询结果信号
            self.data_ready.emit(all_alarms)    # type: ignore[attr-defined]
        except Exception as e:
            print(f"报警历史数据查询异常: {str(e)}")
            self.error.emit(f"查询失败: {str(e)}")  # type: ignore[attr-defined]
        finally:
            # 发送完成信号
            self.finished.emit()    # type: ignore[attr-defined]

    @staticmethod
    def _get_alarm_content(alarm_code):
        """根据报警代码获取报警内容描述"""
        # 报警代码与内容的映射字典
        alarm_dict = {
            1: "上电加热...",
            2: "挤出启动...",
            4: "运转作业...",
            8: "常规预警！",
            16: "异常报警！",
            32: "请求支援！"
        }

        # 返回对应的报警内容，如果没有对应的内容则返回默认文本
        return alarm_dict.get(alarm_code, f"未知报警(代码:{alarm_code})")
# ---------------------------------程序入口---------------------------------
if __name__ == '__main__':
    app = QApplication(sys.argv)  # 创建应用实例
    mainWindow = MainWindow()  # 创建主窗口对象
    mainWindow.show()  # 显示主窗口
    sys.exit(app.exec_())  # 进入主事件循环
