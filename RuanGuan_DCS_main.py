# 导入系统模块
import sys
from datetime import datetime, timedelta
import socket
import serial
import threading
# 从PyQt5导入需要的组件
from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog, QTableWidgetItem
from PyQt5.QtCore import Qt, QTimer, QObject, pyqtSignal, QThread
# 导入自动生成的UI界面类
from Ui_MainWindow import Ui_MainWindow
from Ui_pop_parameter import Ui_Dialog_Pop_Parameter
from Ui_pop_parameter_factory1_2 import Ui_Dialog_Pop_Parameter_Factory1Device2
from Ui_pop_parameter_factory1_3 import Ui_Dialog_Pop_Parameter_Factory1Device3
from Ui_pop_historical_parameter import Ui_Dialog_Pop_Historical_Parameter
from Ui_pop_historical_parameter_factory1_2 import Ui_Dialog_Pop_Historical_Parameter_Factory1Device2
from Ui_pop_historical_parameter_factory1_3 import Ui_Dialog_Pop_Historical_Parameter_Factory1Device3
from Ui_pop_alarm import Ui_Dialog_alarm
from Data_Manager import data_manager, historical_data_manager
from Ruanguan_Curve import RealTimeMainWindowCurve1
# from Ruanguan_Historical import HistoricalCurvePlotter
from RealtimeCurve import RealTimeCurvePlotter
from HistoricalCurve import HistoricalCurvePlotter

CLASS_COLORS1 = ['#FF0000', '#FFFF00', '#00FFFF', '#00FF00', '#FFFF00', '#FF0000', '#FFA500',
                 '#800080', '#008000', '#000080', '#808000', '#800000', '#008080', '#C0C0C0',
                 '#FFC0CB', '#87CEEB', '#98FB98', '#FFD700', '#FF6347', '#4682B4', '#2E8B57',
                 '#DAA520', '#9370DB', '#3CB371', '#7B68EE', '#00FA9A', '#F08080', '#4169E1',
                 '#FF69B4', '#8A2BE2'
                 ]
CLASS_COLORS2 = ['#FF0000', '#FFFF00', '#00FFFF', '#00FF00', '#FFAA00', '#FF55FF', '#FFA500',
                 '#800080', '#008000', '#000080', '#808000', '#800000', '#008080', '#C0C0C0',
                 '#FFC0CB', '#87CEEB', '#98FB98', '#FFD700', '#FF6347', '#4682B4', '#2E8B57',
                 '#DAA520', '#9370DB', '#3CB371', '#7B68EE', '#00FA9A', '#F08080', '#4169E1',
                 '#FF69B4', '#8A2BE2'
                 ]


class PublicDataUpdate:
    # 分解原有的大更新方法为多个私有方法
    def _update_jcj_realtime(self, data):
        """更新挤出机实时数据"""
        self.label_10.setText(str(data.get('preheating_stage', '')))
        self.label_14.setText(str(data.get('preheating_timer', '')))
        self.label_18.setText(str(data.get('temperature1', '')))
        self.label_22.setText(str(data.get('temperature2', '')))
        self.label_26.setText(str(data.get('temperature3', '')))
        self.label_30.setText(str(data.get('temperature4', '')))
        self.label_34.setText(str(data.get('exhaust_temperature', '')))
        self.label_38.setText(str(data.get('cabinet_temperature', '')))
        self.label_42.setText(str(data.get('extruder_rpm', '')))
        self.label_46.setText(str(data.get('inverter_current', '')))
        self.label_50.setText(str(data.get('inverter_error', '')))
        self.label_116.setText(str(data.get('temperature1', '')))
        self.label_117.setText(str(data.get('temperature2', '')))
        self.label_118.setText(str(data.get('temperature3', '')))
        self.label_119.setText(str(data.get('temperature4', '')))
        self.label_104.setText(str(data.get('extruder_rpm', '')))
        self.label_105.setText(str(data.get('inverter_current', '')))  # 使用get方法提供默认值

    def _update_fjj_realtime(self, data):
        """更新挤出机实时数据"""
        self.label_53.setText(str(data.get('wire_tension', '')))
        self.label_57.setText(str(data.get('unwinding_speed', '')))
        self.label_61.setText(str(data.get('linear_velocity', '')))
        self.label_65.setText(str(data.get('ribs_usage', '')))  # 使用get方法提供默认值

    def _update_zdj_realtime(self, data):
        """更新挤出机实时数据"""
        self.label_73.setText(str(data.get('rpm', '')))
        self.label_77.setText(str(data.get('traction_speed', '')))
        self.label_81.setText(str(data.get('pipe_diameter', '')))
        self.label_85.setText(str(data.get('current_production', '')))
        self.label_89.setText(str(data.get('equipment_production', '')))
        self.label_93.setText(str(data.get('pass_rate', '')))  # 使用get方法提供默认值

    def _update_jcj_set(self, data):
        """更新挤出机实时数据"""
        self.label_106.setText(str(data.get('temperature1_set', '')))
        self.label_107.setText(str(data.get('temperature2_set', '')))
        self.label_108.setText(str(data.get('temperature3_set', '')))
        self.label_109.setText(str(data.get('temperature4_set', '')))
        self.label_110.setText(str(data.get('exhaust_temperature_set', '')))
        self.label_111.setText(str(data.get('cabinet_temperature_set', '')))  # 使用get方法提供默认值

    def _update_fjj_set(self, data):
        """更新挤出机实时数据"""
        self.label_112.setText(str(data.get('wire_tension_set', '')))
        self.label_113.setText(str(data.get('linear_velocity_set', '')))
        self.label_124.setText(str(data.get('ribs_usage_set', '')))  # 使用get方法提供默认值

    def _update_zdj_set(self, data):
        """更新挤出机实时数据"""
        self.label_125.setText(str(data.get('rpm_set', '')))
        self.label_126.setText(str(data.get('traction_speed_set', '')))
        self.label_127.setText(str(data.get('pipe_diameter_set', '')))
        self.label_128.setText(str(data.get('planned_production', '')))  # 使用get方法提供默认值

    def _update_curve_set(self, data):
        """更新挤出机实时数据"""
        self.label_120.setText(str(data.get('upper_limit_alarm', '')))
        self.label_121.setText(str(data.get('upper_limit_warning', '')))
        self.label_114.setText(str(data.get('diameter_difference', '')))
        self.label_115.setText(str(data.get('tension_percentage', '')))
        self.label_122.setText(str(data.get('lower_limit_warning', '')))
        self.label_123.setText(str(data.get('lower_limit_alarm', '')))  # 使用get方法提供默认值

    def _update_history_jcj_realtime(self, data):
        """更新挤出机实时数据"""
        # 更新参数1显示（label_10标签）
        self.label_10.setText(str(data.get('preheating_stage', '')))  # 使用空字符串作为默认值
        # 更新参数2显示（label_14标签）
        self.label_14.setText(str(data.get('preheating_timer', '')))
        self.label_18.setText(str(data.get('temperature1', '')))
        self.label_22.setText(str(data.get('temperature2', '')))
        self.label_26.setText(str(data.get('temperature3', '')))
        self.label_30.setText(str(data.get('temperature4', '')))
        self.label_34.setText(str(data.get('exhaust_temperature', '')))
        self.label_38.setText(str(data.get('cabinet_temperature', '')))
        self.label_42.setText(str(data.get('extruder_rpm', '')))
        self.label_46.setText(str(data.get('inverter_current', '')))
        self.label_50.setText(str(data.get('inverter_error', '')))
        self.label_123.setText(str(data.get('temperature1', '')))
        self.label_127.setText(str(data.get('temperature2', '')))
        self.label_125.setText(str(data.get('temperature3', '')))
        self.label_126.setText(str(data.get('temperature4', '')))
        self.label_128.setText(str(data.get('extruder_rpm', '')))
        self.label_124.setText(str(data.get('inverter_current', '')))  # 使用get方法提供默认值

    def _update_history_fjj_realtime(self, data):
        """更新挤出机实时数据"""
        # 更新参数12显示（label_53标签）
        self.label_53.setText(str(data.get('wire_tension', '')))
        self.label_57.setText(str(data.get('unwinding_speed', '')))
        self.label_61.setText(str(data.get('linear_velocity', '')))
        self.label_65.setText(str(data.get('ribs_usage', '')))  # 使用get方法提供默认值

    def _update_history_zdj_realtime(self, data):
        """更新挤出机实时数据"""
        self.label_73.setText(str(data.get('rpm', '')))
        self.label_77.setText(str(data.get('traction_speed', '')))
        self.label_81.setText(str(data.get('pipe_diameter', '')))
        self.label_85.setText(str(data.get('current_production', '')))
        self.label_89.setText(str(data.get('equipment_production', '')))
        self.label_93.setText(str(data.get('pass_rate', '')))  # 使用get方法提供默认值

    def _update_history_jcj_set(self, data):
        """更新挤出机实时数据"""
        self.label_104.setText(str(data.get('temperature1_set', '')))
        self.label_105.setText(str(data.get('temperature2_set', '')))
        self.label_106.setText(str(data.get('temperature3_set', '')))
        self.label_107.setText(str(data.get('temperature4_set', '')))
        self.label_108.setText(str(data.get('exhaust_temperature_set', '')))
        self.label_115.setText(str(data.get('cabinet_temperature_set', '')))  # 使用get方法提供默认值

    def _update_history_fjj_set(self, data):
        """更新挤出机实时数据"""
        self.label_109.setText(str(data.get('wire_tension_set', '')))
        self.label_110.setText(str(data.get('linear_velocity_set', '')))
        self.label_111.setText(str(data.get('ribs_usage_set', '')))  # 使用get方法提供默认值

    def _update_history_zdj_set(self, data):
        """更新挤出机实时数据"""
        self.label_112.setText(str(data.get('rpm_set', '')))
        self.label_113.setText(str(data.get('traction_speed_set', '')))
        self.label_114.setText(str(data.get('pipe_diameter_set', '')))
        self.label_116.setText(str(data.get('planned_production', '')))  # 使用get方法提供默认值

    def _update_history_curve_set(self, data):
        """更新挤出机实时数据"""
        self.label_117.setText(str(data.get('upper_limit_alarm', '')))
        self.label_118.setText(str(data.get('upper_limit_warning', '')))
        self.label_114.setText(str(data.get('diameter_difference', '')))
        self.label_115.setText(str(data.get('tension_percentage', '')))
        self.label_121.setText(str(data.get('lower_limit_warning', '')))
        self.label_122.setText(str(data.get('lower_limit_alarm', '')))  # 使用get方法提供默认值

    @staticmethod
    def _get_alarm_content(alarm_code):
        """根据报警代码获取报警内容描述"""
        # 报警代码与内容的映射字典
        alarm_dict = {
            1: "急停按下或挤出变频报警！",
            2: "尺寸超上下限过久！",
            3: "尺寸下限报警",
            4: "尺寸上限报警",
            5: "尺寸下限预警",
            6: "尺寸上限预警",
            7: "温度未达标！",
            8: "螺旋伺服报警！",
            9: "牵引伺服报警！",
            10: "温区1传感器断线或损坏！",
            11: "温区2传感器断线或损坏！",
            12: "温区3传感器断线或损坏！",
            13: "温区4传感器断线或损坏！",
            14: "温区5传感器断线或损坏！",
            15: "AD偏移增益错误",
            16: "AD电源故障",
            17: "AD硬件错误",
            18: "变频器通讯中断！",
            19: "变频器报警！",
            20: "AD模块异常",
            21: "切刀护罩打开！",
            22: "切刀伺服异常报警或未上电！",
            23: "变频器通讯中断!",
            24: "分拣伺服异常！",
            25: "切刀异常！"
        }

        # 返回对应的报警内容，如果没有对应的内容则返回默认文本
        return alarm_dict.get(alarm_code, f"未知报警(代码:{alarm_code})")


# ---------------------------------参数弹窗类（继承QDialog和UI类）---------------------------------
class ParameterDialog(QDialog, Ui_Dialog_Pop_Parameter, PublicDataUpdate):
    def __init__(self):
        # 调用QDialog父类构造方法
        super().__init__()
        # 初始化UI界面
        self.setWindowFlags(Qt.FramelessWindowHint)  # 设置无边框窗口样式（隐藏标题栏和边框）
        self.setAttribute(Qt.WA_TranslucentBackground)  # 启用透明背景属性（实现半透明/异形窗口效果）
        self.setupUi(self)  # 调用 UI 设计的 setupUi 方法

        self.dialog_historical = None  # 定义创建用于存储历史数据曲线弹窗的实例
        self.pushButton_historical_curve.clicked.connect(self.show_dialog_pop_historical_parameter)  # 连接按钮点击信号
        # 连接时间设置输入框的信号
        self.lineEdit_SetTime.textChanged.connect(self.on_time_interval_changed)
        # 设置默认值
        self.lineEdit_SetTime.setText("10")

        # 初始化位置记录变量
        self.dialog_original_pos = None  # 窗口原始位置
        self.drag_start_pos = None  # 鼠标拖动起始位置
        # 绑定鼠标事件到自身方法
        self.mousePressEvent = self.dialog_mouse_press  # 按下事件处理
        self.mouseMoveEvent = self.dialog_mouse_move  # 移动事件处理
        # 设置窗口居中属性
        self.center_dialog()  # 初始居中显示

        self.data_manager = data_manager

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
        # 添加管径实时曲线（示例配置）
        self.curve_plotter = RealTimeCurvePlotter(
            parent_widget=self.widget_pop_parameter_curve1,  # 对应UI中的曲线容器
            params_config={
                'curve3': 'diameter_difference',
                'curve1': 'upper_limit_alarm',
                'curve6': 'lower_limit_alarm',
                'curve4': 'tension_percentage',
                'curve2': 'upper_limit_warning',
                'curve5': 'lower_limit_warning'
            },
            colors=CLASS_COLORS1,
            y_limits=(-1, 1)
        )

        # 添加挤出机参数实时曲线（示例配置）
        self.curve_jcj = RealTimeCurvePlotter(
            parent_widget=self.widget_pop_parameter_curve2,  # 对应UI中的曲线容器
            params_config={
                'curve1': 'temperature1',
                'curve2': 'temperature2',
                'curve3': 'temperature3',
                'curve4': 'temperature4',
                'curve5': 'extruder_rpm',
                'curve6': 'inverter_current'
            },
            colors=CLASS_COLORS2,
            y_limits=(0, 200)
        )

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
        thread.finished.connect(thread.deleteLater)  # type: ignore[attr-defined] # 线程退出后销毁线程对象

        # 连接数据更新信号到处理方法
        worker.data_updated.connect(self._handle_data_update)  # type: ignore[attr-defined]

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
            "factory1_1_realtime_data_jcj": [self._update_jcj_realtime, self.curve_jcj.update_plot],
            "factory1_1_realtime_data_fjj": self._update_fjj_realtime,
            "factory1_1_realtime_data_zdj": self._update_zdj_realtime,
            "factory1_1_set_data_jcj": self._update_jcj_set,
            "factory1_1_set_data_fjj": self._update_fjj_set,
            "factory1_1_set_data_zdj": self._update_zdj_set,
            "factory1_1_set_data_curve": [self._update_curve_set, self.curve_plotter.update_plot]
        }

        # 获取并执行对应的更新策略
        if strategy := update_strategies.get(table_name):
            if isinstance(strategy, list):  # 处理多个方法的情况
                for method in strategy:
                    method(data)  # type: ignore[attr-defined]
            else:
                strategy(data)  # type: ignore[attr-defined]

    def show_dialog_pop_historical_parameter(self):
        """显示历史参数弹窗的方法"""
        # self.hide()  # 隐藏当前窗口
        self.showMinimized()
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

    def on_time_interval_changed(self):
        """当时间间隔输入框内容改变时调用"""
        try:
            # 获取输入的时间间隔值
            time_interval = self.lineEdit_SetTime.text().strip()
            if time_interval:  # 如果输入不为空
                minutes = int(time_interval)
                if minutes > 0:  # 确保是正数
                    # 更新两个曲线绘制器的时间间隔
                    if hasattr(self, 'curve_plotter'):
                        self.curve_plotter.set_time_interval(minutes)
                    if hasattr(self, 'curve_jcj'):
                        self.curve_jcj.set_time_interval(minutes)
        except ValueError:
            # 如果输入无效，忽略错误
            pass

    # 重写 show 函数,讲数据更新线程启动放在show函数中
    def show(self):
        super().show()  # 调用父类 show 方法
        self._start_data_update_thread(self.tables_to_monitor)
        print("启动数据更新线程")

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


class ParameterDialogFactory1Device2(QDialog, Ui_Dialog_Pop_Parameter_Factory1Device2, PublicDataUpdate):
    def __init__(self):
        # 调用QDialog父类构造方法
        super().__init__()
        # 初始化UI界面
        self.setWindowFlags(Qt.FramelessWindowHint)  # 设置无边框窗口样式（隐藏标题栏和边框）
        self.setAttribute(Qt.WA_TranslucentBackground)  # 启用透明背景属性（实现半透明/异形窗口效果）
        self.setupUi(self)  # 调用 UI 设计的 setupUi 方法

        self.dialog_historical = None  # 定义创建用于存储历史数据曲线弹窗的实例
        self.pushButton_historical_curve.clicked.connect(self.show_dialog_pop_historical_parameter)  # 连接按钮点击信号
        # 连接时间设置输入框的信号
        self.lineEdit_SetTime.textChanged.connect(self.on_time_interval_changed)
        # 设置默认值
        self.lineEdit_SetTime.setText("10")

        # 初始化位置记录变量
        self.dialog_original_pos = None  # 窗口原始位置
        self.drag_start_pos = None  # 鼠标拖动起始位置
        # 绑定鼠标事件到自身方法
        self.mousePressEvent = self.dialog_mouse_press  # 按下事件处理
        self.mouseMoveEvent = self.dialog_mouse_move  # 移动事件处理
        # 设置窗口居中属性
        self.center_dialog()  # 初始居中显示

        self.data_manager = data_manager

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
        # 添加管径实时曲线（示例配置）
        self.curve_plotter = RealTimeCurvePlotter(
            parent_widget=self.widget_pop_parameter_curve1,  # 对应UI中的曲线容器
            params_config={
                'curve3': 'diameter_difference',
                'curve1': 'upper_limit_alarm',
                'curve6': 'lower_limit_alarm',
                'curve4': 'tension_percentage',
                'curve2': 'upper_limit_warning',
                'curve5': 'lower_limit_warning'
            },
            colors=CLASS_COLORS1,
            y_limits=(-1, 1)
        )

        # 添加挤出机参数实时曲线（示例配置）
        self.curve_jcj = RealTimeCurvePlotter(
            parent_widget=self.widget_pop_parameter_curve2,  # 对应UI中的曲线容器
            params_config={
                'curve1': 'temperature1',
                'curve2': 'temperature2',
                'curve3': 'temperature3',
                'curve4': 'temperature4',
                'curve5': 'extruder_rpm',
                'curve6': 'inverter_current'
            },
            colors=CLASS_COLORS2,
            y_limits=(0, 200)
        )

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
        worker.data_updated.connect(self._handle_data_update)  # type: ignore[attr-defined]

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
            "factory1_2_realtime_data_jcj": [self._update_jcj_realtime, self.curve_jcj.update_plot],
            "factory1_2_realtime_data_fjj": self._update_fjj_realtime,
            "factory1_2_realtime_data_zdj": self._update_zdj_realtime,
            "factory1_2_set_data_jcj": self._update_jcj_set,
            "factory1_2_set_data_fjj": self._update_fjj_set,
            "factory1_2_set_data_zdj": self._update_zdj_set,
            "factory1_2_set_data_curve": [self._update_curve_set, self.curve_plotter.update_plot]
        }

        # 获取并执行对应的更新策略
        if strategy := update_strategies.get(table_name):
            if isinstance(strategy, list):  # 处理多个方法的情况
                for method in strategy:
                    method(data)  # type: ignore[attr-defined]
            else:
                strategy(data)  # type: ignore[attr-defined]

    def show_dialog_pop_historical_parameter(self):
        """显示历史参数弹窗的方法"""
        # self.hide()  # 隐藏当前窗口
        self.showMinimized()
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

    def on_time_interval_changed(self):
        """当时间间隔输入框内容改变时调用"""
        try:
            # 获取输入的时间间隔值
            time_interval = self.lineEdit_SetTime.text().strip()
            if time_interval:  # 如果输入不为空
                minutes = int(time_interval)
                if minutes > 0:  # 确保是正数
                    # 更新两个曲线绘制器的时间间隔
                    if hasattr(self, 'curve_plotter'):
                        self.curve_plotter.set_time_interval(minutes)
                    if hasattr(self, 'curve_jcj'):
                        self.curve_jcj.set_time_interval(minutes)
        except ValueError:
            # 如果输入无效，忽略错误
            pass

    # 重写 show 函数,讲数据更新线程启动放在show函数中
    def show(self):
        super().show()  # 调用父类 show 方法
        self._start_data_update_thread(self.tables_to_monitor)
        print("启动数据更新线程")

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


class ParameterDialogFactory1Device3(QDialog, Ui_Dialog_Pop_Parameter_Factory1Device3, PublicDataUpdate):
    def __init__(self):
        # 调用QDialog父类构造方法
        super().__init__()
        # 初始化UI界面
        self.setWindowFlags(Qt.FramelessWindowHint)  # 设置无边框窗口样式（隐藏标题栏和边框）
        self.setAttribute(Qt.WA_TranslucentBackground)  # 启用透明背景属性（实现半透明/异形窗口效果）
        self.setupUi(self)  # 调用 UI 设计的 setupUi 方法

        self.dialog_historical = None  # 定义创建用于存储历史数据曲线弹窗的实例
        self.pushButton_historical_curve.clicked.connect(self.show_dialog_pop_historical_parameter)  # 连接按钮点击信号
        # 连接时间设置输入框的信号
        self.lineEdit_SetTime.textChanged.connect(self.on_time_interval_changed)
        # 设置默认值
        self.lineEdit_SetTime.setText("10")

        # 初始化位置记录变量
        self.dialog_original_pos = None  # 窗口原始位置
        self.drag_start_pos = None  # 鼠标拖动起始位置
        # 绑定鼠标事件到自身方法
        self.mousePressEvent = self.dialog_mouse_press  # 按下事件处理
        self.mouseMoveEvent = self.dialog_mouse_move  # 移动事件处理
        # 设置窗口居中属性
        self.center_dialog()  # 初始居中显示

        self.data_manager = data_manager

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
        # 添加管径实时曲线（示例配置）
        self.curve_plotter = RealTimeCurvePlotter(
            parent_widget=self.widget_pop_parameter_curve1,  # 对应UI中的曲线容器
            params_config={
                'curve3': 'diameter_difference',
                'curve1': 'upper_limit_alarm',
                'curve6': 'lower_limit_alarm',
                'curve4': 'tension_percentage',
                'curve2': 'upper_limit_warning',
                'curve5': 'lower_limit_warning'
            },
            colors=CLASS_COLORS1,
            y_limits=(-1, 1)
        )

        # 添加挤出机参数实时曲线（示例配置）
        self.curve_jcj = RealTimeCurvePlotter(
            parent_widget=self.widget_pop_parameter_curve2,  # 对应UI中的曲线容器
            params_config={
                'curve1': 'temperature1',
                'curve2': 'temperature2',
                'curve3': 'temperature3',
                'curve4': 'temperature4',
                'curve5': 'extruder_rpm',
                'curve6': 'inverter_current'
            },
            colors=CLASS_COLORS2,
            y_limits=(0, 200)
        )

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
        thread.started.connect(worker.run)  # type: ignore[attr-defined] # 线程启动时执行run方法
        worker.finished.connect(thread.quit)  # type: ignore[attr-defined]    # 工作完成时退出线程
        worker.finished.connect(worker.deleteLater)  # type: ignore[attr-defined]   # 工作完成后销毁worker对象
        thread.finished.connect(thread.deleteLater)  # type: ignore[attr-defined]    # 线程退出后销毁线程对象

        # 连接数据更新信号到处理方法
        worker.data_updated.connect(self._handle_data_update)  # type: ignore[attr-defined]

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
            "factory1_3_realtime_data_jcj": [self._update_jcj_realtime, self.curve_jcj.update_plot],
            "factory1_3_realtime_data_fjj": self._update_fjj_realtime,
            "factory1_3_realtime_data_zdj": self._update_zdj_realtime,
            "factory1_3_set_data_jcj": self._update_jcj_set,
            "factory1_3_set_data_fjj": self._update_fjj_set,
            "factory1_3_set_data_zdj": self._update_zdj_set,
            "factory1_3_set_data_curve": [self._update_curve_set, self.curve_plotter.update_plot]
        }

        # 获取并执行对应的更新策略
        if strategy := update_strategies.get(table_name):
            if isinstance(strategy, list):  # 处理多个方法的情况
                for method in strategy:
                    method(data)  # type: ignore[attr-defined]
            else:
                strategy(data)  # type: ignore[attr-defined]

    def show_dialog_pop_historical_parameter(self):
        """显示历史参数弹窗的方法"""
        # self.hide()  # 隐藏当前窗口
        self.showMinimized()
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

    def on_time_interval_changed(self):
        """当时间间隔输入框内容改变时调用"""
        try:
            # 获取输入的时间间隔值
            time_interval = self.lineEdit_SetTime.text().strip()
            if time_interval:  # 如果输入不为空
                minutes = int(time_interval)
                if minutes > 0:  # 确保是正数
                    # 更新两个曲线绘制器的时间间隔
                    if hasattr(self, 'curve_plotter'):
                        self.curve_plotter.set_time_interval(minutes)
                    if hasattr(self, 'curve_jcj'):
                        self.curve_jcj.set_time_interval(minutes)
        except ValueError:
            # 如果输入无效，忽略错误
            pass

    # 重写 show 函数,讲数据更新线程启动放在show函数中
    def show(self):
        super().show()  # 调用父类 show 方法
        self._start_data_update_thread(self.tables_to_monitor)
        print("启动数据更新线程")

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


# ---------------------------------历史参数弹窗类（继承QDialog和UI类）---------------------------------
class HistoricalParameterDialog(QDialog, Ui_Dialog_Pop_Historical_Parameter, PublicDataUpdate):
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
        # 连接时间设置输入框的信号
        self.lineEdit_SetTime.textChanged.connect(self.on_time_interval_changed)
        # 设置默认值
        self.lineEdit_SetTime.setText("10")
        # 添加时间间隔属性，默认为10分钟
        self.time_interval_minutes = 10
        # 初始化历史曲线
        self._init_historical_curves()

    def _init_historical_curves(self):
        """初始化历史曲线组件"""
        # 管径历史曲线 (创建历史曲线绘制组件)
        self.hist_curve1 = HistoricalCurvePlotter(
            parent_widget = self.widget_pop_historical_parameter_curve1,  # 指定父容器控件
            table_name = "factory1_1_set_data_curve",  # 对应的数据库表名
            params_config = {
                'curve1': 'upper_limit_alarm',
                'curve2': 'upper_limit_warning',
                'curve3': 'diameter_difference',
                'curve4': 'tension_percentage',
                'curve5': 'lower_limit_warning',
                'curve6': 'lower_limit_alarm'
            },
            colors = CLASS_COLORS1, #曲线颜色配置
            y_limits = (-1, 1)  # Y轴显示范围
        )

        # 挤出机历史曲线 (第二组历史曲线)
        self.hist_curve2 = HistoricalCurvePlotter(
            parent_widget = self.widget_pop_historical_parameter_curve2,  # 第二个曲线容器的父控件
            table_name = "factory1_1_realtime_data_jcj",  # 挤出机实时数据表
            params_config={
                'curve1': 'temperature1',
                'curve2': 'temperature2',
                'curve3': 'temperature3',
                'curve4': 'temperature4',
                'curve5': 'extruder_rpm',
                'curve6': 'inverter_current'
            },
            # 参数映射关系
            colors=CLASS_COLORS2, #曲线颜色配置
            y_limits = (0, 200)  # Y轴最大范围200
        )

    def set_time_interval(self, minutes):
        """设置曲线显示的时间间隔（分钟）"""
        try:
            self.time_interval_minutes = max(1, int(minutes))  # 确保至少1分钟
        except (ValueError, TypeError):
            self.time_interval_minutes = 10  # 如果转换失败，使用默认值

    def handle_historical_query(self):
        """处理历史查询按钮点击事件的核心方法"""
        # 获取界面选择的时间（转换为Python datetime对象）
        query_time = self.dateTimeEdit.dateTime().toPyDateTime()
        # 计算结束时间（格式化成SQL可识别的字符串）
        end_time = query_time.strftime("%Y-%m-%d %H:%M:%S")
        # 计算起始时间（当前查询时间前推10分钟）
        start_time = (query_time - timedelta(minutes=self.time_interval_minutes)).strftime("%Y-%m-%d %H:%M:%S")
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

    # 添加新方法：处理数据更新
    def _update_ui_labels(self, table_name, data):
        """处理从子线程接收到的数据更新
        参数:
            table_name: 表名
            data: 数据字典
        """
        # 创建策略映射字典（与原来相同）
        update_strategies = {
            "factory1_1_realtime_data_jcj": self._update_history_jcj_realtime,
            "factory1_1_realtime_data_fjj": self._update_history_fjj_realtime,
            "factory1_1_realtime_data_zdj": self._update_history_zdj_realtime,
            "factory1_1_set_data_jcj": self._update_history_jcj_set,
            "factory1_1_set_data_fjj": self._update_history_fjj_set,
            "factory1_1_set_data_zdj": self._update_history_zdj_set,
            "factory1_1_set_data_curve": self._update_history_curve_set
        }

        # 获取并执行对应的更新策略
        if strategy := update_strategies.get(table_name):
            if isinstance(strategy, list):  # 处理多个方法的情况
                for method in strategy:
                    method(data)  # type: ignore[attr-defined]
            else:
                strategy(data)  # type: ignore[attr-defined]

    def show_dialog_pop_parameter(self):
        """隐藏当前历史数据窗口，显示实时参数弹窗的方法"""
        # self.hide()  # 隐藏当前窗口
        self.showMinimized()
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

    def on_time_interval_changed(self):
        """当时间间隔输入框内容改变时调用"""
        try:
            # 获取输入的时间间隔值
            time_interval = self.lineEdit_SetTime.text().strip()
            if time_interval:  # 如果输入不为空
                minutes = int(time_interval)
                if minutes > 0:  # 确保是正数
                    # 更新两个曲线绘制器的时间间隔
                    if hasattr(self, 'hist_curve1'):
                        self.set_time_interval(minutes)
        except ValueError:
            # 如果输入无效，忽略错误
            pass

    # 历史参数弹窗类新增关闭事件处理
    # 重写窗口关闭事件处理方法（当窗口被关闭时自动触发）
    def closeEvent(self, event):
        """处理关闭事件：关闭关联的实时参数弹窗"""
        # 检查是否存在实时参数弹窗实例
        if self.dialog_realtime:  # 判断dialog_realtime是否已初始化
            self.dialog_realtime.close()  # 调用实时弹窗的关闭方法
        super().closeEvent(event)  # 调用父类QDialog的关闭事件处理，确保正常关闭流程


class HistoricalParameterDialogFactory1Device2(QDialog, Ui_Dialog_Pop_Historical_Parameter_Factory1Device2, PublicDataUpdate):
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
        # 连接时间设置输入框的信号
        self.lineEdit_SetTime.textChanged.connect(self.on_time_interval_changed)
        # 设置默认值
        self.lineEdit_SetTime.setText("10")
        # 添加时间间隔属性，默认为10分钟
        self.time_interval_minutes = 10
        # 初始化历史曲线
        self._init_historical_curves()

    def _init_historical_curves(self):
        """初始化历史曲线组件"""
        # 管径历史曲线 (创建历史曲线绘制组件)
        self.hist_curve1 = HistoricalCurvePlotter(
            parent_widget = self.widget_pop_historical_parameter_curve1,  # 指定父容器控件
            table_name = "factory1_2_set_data_curve",  # 对应的数据库表名
            params_config = {
                'curve1': 'upper_limit_alarm',
                'curve2': 'upper_limit_warning',
                'curve3': 'diameter_difference',
                'curve4': 'tension_percentage',
                'curve5': 'lower_limit_warning',
                'curve6': 'lower_limit_alarm'
            },
            colors = CLASS_COLORS1, #曲线颜色配置
            y_limits = (-1, 1)  # Y轴显示范围
        )

        # 挤出机历史曲线 (第二组历史曲线)
        self.hist_curve2 = HistoricalCurvePlotter(
            parent_widget = self.widget_pop_historical_parameter_curve2,  # 第二个曲线容器的父控件
            table_name = "factory1_2_realtime_data_jcj",  # 挤出机实时数据表
            params_config={
                'curve1': 'temperature1',
                'curve2': 'temperature2',
                'curve3': 'temperature3',
                'curve4': 'temperature4',
                'curve5': 'extruder_rpm',
                'curve6': 'inverter_current'
            },
            # 参数映射关系
            colors=CLASS_COLORS2, #曲线颜色配置
            y_limits = (0, 200)  # Y轴最大范围200
        )

    def set_time_interval(self, minutes):
        """设置曲线显示的时间间隔（分钟）"""
        try:
            self.time_interval_minutes = max(1, int(minutes))  # 确保至少1分钟
        except (ValueError, TypeError):
            self.time_interval_minutes = 10  # 如果转换失败，使用默认值

    def handle_historical_query(self):
        """处理历史查询按钮点击事件的核心方法"""
        # 获取界面选择的时间（转换为Python datetime对象）
        query_time = self.dateTimeEdit.dateTime().toPyDateTime()
        # 计算结束时间（格式化成SQL可识别的字符串）
        end_time = query_time.strftime("%Y-%m-%d %H:%M:%S")
        # 计算起始时间（当前查询时间前推10分钟）
        start_time = (query_time - timedelta(minutes=self.time_interval_minutes)).strftime("%Y-%m-%d %H:%M:%S")
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

    # 添加新方法：处理数据更新
    def _update_ui_labels(self, table_name, data):
        """处理从子线程接收到的数据更新
        参数:
            table_name: 表名
            data: 数据字典
        """
        # 创建策略映射字典（与原来相同）
        update_strategies = {
            "factory1_2_realtime_data_jcj": self._update_history_jcj_realtime,
            "factory1_2_realtime_data_fjj": self._update_history_fjj_realtime,
            "factory1_2_realtime_data_zdj": self._update_history_zdj_realtime,
            "factory1_2_set_data_jcj": self._update_history_jcj_set,
            "factory1_2_set_data_fjj": self._update_history_fjj_set,
            "factory1_2_set_data_zdj": self._update_history_zdj_set,
            "factory1_2_set_data_curve": self._update_history_curve_set
        }

        # 获取并执行对应的更新策略
        if strategy := update_strategies.get(table_name):
            if isinstance(strategy, list):  # 处理多个方法的情况
                for method in strategy:
                    method(data)  # type: ignore[attr-defined]
            else:
                strategy(data)  # type: ignore[attr-defined]

    def show_dialog_pop_parameter(self):
        """隐藏当前历史数据窗口，显示实时参数弹窗的方法"""
        # self.hide()  # 隐藏当前窗口
        self.showMinimized()
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

    def on_time_interval_changed(self):
        """当时间间隔输入框内容改变时调用"""
        try:
            # 获取输入的时间间隔值
            time_interval = self.lineEdit_SetTime.text().strip()
            if time_interval:  # 如果输入不为空
                minutes = int(time_interval)
                if minutes > 0:  # 确保是正数
                    # 更新两个曲线绘制器的时间间隔
                    if hasattr(self, 'hist_curve1'):
                        self.set_time_interval(minutes)
        except ValueError:
            # 如果输入无效，忽略错误
            pass

    # 历史参数弹窗类新增关闭事件处理
    # 重写窗口关闭事件处理方法（当窗口被关闭时自动触发）
    def closeEvent(self, event):
        """处理关闭事件：关闭关联的实时参数弹窗"""
        # 检查是否存在实时参数弹窗实例
        if self.dialog_realtime:  # 判断dialog_realtime是否已初始化
            self.dialog_realtime.close()  # 调用实时弹窗的关闭方法
        super().closeEvent(event)  # 调用父类QDialog的关闭事件处理，确保正常关闭流程


class HistoricalParameterDialogFactory1Device3(QDialog, Ui_Dialog_Pop_Historical_Parameter_Factory1Device3, PublicDataUpdate):
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
        # 连接时间设置输入框的信号
        self.lineEdit_SetTime.textChanged.connect(self.on_time_interval_changed)
        # 设置默认值
        self.lineEdit_SetTime.setText("10")
        # 添加时间间隔属性，默认为10分钟
        self.time_interval_minutes = 10
        # 初始化历史曲线
        self._init_historical_curves()

    def _init_historical_curves(self):
        """初始化历史曲线组件"""
        # 管径历史曲线 (创建历史曲线绘制组件)
        self.hist_curve1 = HistoricalCurvePlotter(
            parent_widget = self.widget_pop_historical_parameter_curve1,  # 指定父容器控件
            table_name = "factory1_3_set_data_curve",  # 对应的数据库表名
            params_config = {
                'curve1': 'upper_limit_alarm',
                'curve2': 'upper_limit_warning',
                'curve3': 'diameter_difference',
                'curve4': 'tension_percentage',
                'curve5': 'lower_limit_warning',
                'curve6': 'lower_limit_alarm'
            },
            colors = CLASS_COLORS1, #曲线颜色配置
            y_limits = (-1, 1)  # Y轴显示范围
        )

        # 挤出机历史曲线 (第二组历史曲线)
        self.hist_curve2 = HistoricalCurvePlotter(
            parent_widget = self.widget_pop_historical_parameter_curve2,  # 第二个曲线容器的父控件
            table_name = "factory1_3_realtime_data_jcj",  # 挤出机实时数据表
            params_config={
                'curve1': 'temperature1',
                'curve2': 'temperature2',
                'curve3': 'temperature3',
                'curve4': 'temperature4',
                'curve5': 'extruder_rpm',
                'curve6': 'inverter_current'
            },
            # 参数映射关系
            colors=CLASS_COLORS2, #曲线颜色配置
            y_limits = (0, 200)  # Y轴最大范围200
        )

    def set_time_interval(self, minutes):
        """设置曲线显示的时间间隔（分钟）"""
        try:
            self.time_interval_minutes = max(1, int(minutes))  # 确保至少1分钟
        except (ValueError, TypeError):
            self.time_interval_minutes = 10  # 如果转换失败，使用默认值

    def handle_historical_query(self):
        """处理历史查询按钮点击事件的核心方法"""
        # 获取界面选择的时间（转换为Python datetime对象）
        query_time = self.dateTimeEdit.dateTime().toPyDateTime()
        # 计算结束时间（格式化成SQL可识别的字符串）
        end_time = query_time.strftime("%Y-%m-%d %H:%M:%S")
        # 计算起始时间（当前查询时间前推10分钟）
        start_time = (query_time - timedelta(minutes=self.time_interval_minutes)).strftime("%Y-%m-%d %H:%M:%S")
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

    # 添加新方法：处理数据更新
    def _update_ui_labels(self, table_name, data):
        """处理从子线程接收到的数据更新
        参数:
            table_name: 表名
            data: 数据字典
        """
        # 创建策略映射字典（与原来相同）
        update_strategies = {
            "factory1_3_realtime_data_jcj": self._update_history_jcj_realtime,
            "factory1_3_realtime_data_fjj": self._update_history_fjj_realtime,
            "factory1_3_realtime_data_zdj": self._update_history_zdj_realtime,
            "factory1_3_set_data_jcj": self._update_history_jcj_set,
            "factory1_3_set_data_fjj": self._update_history_fjj_set,
            "factory1_3_set_data_zdj": self._update_history_zdj_set,
            "factory1_3_set_data_curve": self._update_history_curve_set
        }

        # 获取并执行对应的更新策略
        if strategy := update_strategies.get(table_name):
            if isinstance(strategy, list):  # 处理多个方法的情况
                for method in strategy:
                    method(data)  # type: ignore[attr-defined]
            else:
                strategy(data)  # type: ignore[attr-defined]

    def show_dialog_pop_parameter(self):
        """隐藏当前历史数据窗口，显示实时参数弹窗的方法"""
        # self.hide()  # 隐藏当前窗口
        self.showMinimized()
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

    def on_time_interval_changed(self):
        """当时间间隔输入框内容改变时调用"""
        try:
            # 获取输入的时间间隔值
            time_interval = self.lineEdit_SetTime.text().strip()
            if time_interval:  # 如果输入不为空
                minutes = int(time_interval)
                if minutes > 0:  # 确保是正数
                    # 更新两个曲线绘制器的时间间隔
                    if hasattr(self, 'hist_curve1'):
                        self.set_time_interval(minutes)
        except ValueError:
            # 如果输入无效，忽略错误
            pass

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
            'factory1_3_alarm_data'
        ]

        self.alarm_field_map = {
            'P0M43': '尺寸下限报警',
            'P0M45': '尺寸上限报警',
            'P0M46': '尺寸下限预警',
            'P0M48': '尺寸上限预警',
            'P0M41': '温度未达标！',
            'P0X21': '螺旋伺服报警！',
            'P0X20': '牵引伺服报警！',
            'P0M31': '切刀护罩打开！',
            'P0M6': '切刀伺服异常报警或未上电！',
            'P0M22': '切刀异常！',
            'P1FJSF_ALM': '分拣伺服异常！',
            'P2D8030': '温区1传感器断线或损坏！',
            'P2D8031': '温区2传感器断线或损坏！',
            'P2D8032': '温区3传感器断线或损坏！',
            'P2D8033': '温区4传感器断线或损坏！',
            'P2D8036': '温区5传感器断线或损坏！',
            'P2M98': '变频器通讯中断！',
            'P2X12': '变频器报警！',
            'P2M99': '变频器通讯中断!'
        }
        self.alarm_fields = list(self.alarm_field_map.keys())
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
        worker.data_updated.connect(self._handle_alarm_update)  #type: ignore[arg-type]

        # 存储线程引用
        self.threads['data_update_alarm'] = (thread, worker)

        # 启动线程
        thread.start()

    @staticmethod
    def _format_record_time(value):
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(value, str):
            return value.replace("T", " ")
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def _parse_device_id(table_name):
        parts = table_name.split('_')
        if len(parts) >= 2 and parts[1].isdigit():
            return parts[1]
        return "未知"

    def _append_realtime_alarm_row(self, alarm_text):
        rows = []
        for row in range(self.tableWidget_realtime_alarm.rowCount()):
            if item := self.tableWidget_realtime_alarm.item(row, 0):
                rows.append(item.text())

        if len(rows) >= 9:
            rows.pop(0)

        rows.append(alarm_text)

        self.tableWidget_realtime_alarm.clearContents()
        for row, text in enumerate(rows):
            self.tableWidget_realtime_alarm.setItem(row, 0, QTableWidgetItem(text))
            self.tableWidget_realtime_alarm.item(row, 0).setBackground(Qt.red)

        self.tableWidget_realtime_alarm.scrollToBottom()

    # 添加新方法：处理报警数据更新
    def _handle_alarm_update(self, table_name, data):
        """处理从子线程接收到的报警数据更新
        参数:
            table_name: 表名
            data: 数据字典
        """
        if not data:
            return

        present_fields = [k for k in self.alarm_fields if k in data]
        if not present_fields:
            return

        current_status = {}
        for field in present_fields:
            v = data.get(field)
            try:
                current_status[field] = int(v) if v is not None else 0
            except Exception:
                current_status[field] = 0

        prev_status = self.last_alarm_values.get(table_name)
        if prev_status is None:
            self.last_alarm_values[table_name] = current_status
            return

        device_id = self._parse_device_id(table_name)
        record_time = self._format_record_time(data.get('timestamp'))

        for field in present_fields:
            prev_v = int(prev_status.get(field, 0) or 0)
            cur_v = int(current_status.get(field, 0) or 0)
            if prev_v == 0 and cur_v == 1:
                alarm_content = self.alarm_field_map.get(field, field)
                alarm_text = f"[{record_time}] 设备{device_id}: {alarm_content}"
                self._append_realtime_alarm_row(alarm_text)

        self.last_alarm_values[table_name] = current_status

    def right_down_dialog(self):
        """将弹窗居中显示的方法"""
        # 获取主屏幕尺寸
        screen = QApplication.primaryScreen().geometry()
        # 计算居中坐标（屏幕宽度-窗口宽度）/2
        x = (screen.width() - self.width())
        y = (screen.height() - self.height())
        # 移动窗口到计算位置
        self.move(x, y)

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
        worker.finished.connect(thread.quit)  # type: ignore[attr-defined]
        worker.finished.connect(worker.deleteLater)  # type: ignore[attr-defined]
        thread.finished.connect(thread.deleteLater)  # type: ignore[attr-defined]

        # 连接数据更新信号到处理方法
        worker.data_ready.connect(self._handle_alarm_history)  # type: ignore[attr-defined]

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

    # 重写 show 函数,讲数据更新线程启动放在show函数中
    def show(self):
        super().show()  # 调用父类 show 方法
        self._start_data_update_thread(self.alarm_tables)
        print("启动数据更新线程")

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

        # 初始化历史弹窗（使用自定义弹窗类）
        self.dialog_historical = HistoricalParameterDialog()
        self.dialog_historical_factory1_2 = HistoricalParameterDialogFactory1Device2()
        self.dialog_historical_factory1_3 = HistoricalParameterDialogFactory1Device3()

        # 建立实例关联
        self.pop_dialog.dialog_historical = self.dialog_historical
        self.dialog_historical.dialog_realtime = self.pop_dialog

        self.pop_dialog_factory1_2.dialog_historical = self.dialog_historical_factory1_2
        self.dialog_historical_factory1_2.dialog_realtime = self.pop_dialog_factory1_2
        self.pop_dialog_factory1_3.dialog_historical = self.dialog_historical_factory1_3
        self.dialog_historical_factory1_3.dialog_realtime = self.pop_dialog_factory1_3
        # 初始化报警弹窗（使用自定义弹窗类）
        self.pop_alarm_dialog = AlarmDialog()

        # 绑定曲线控件的鼠标点击事件
        self.curve1.mousePressEvent = self.show_pop_parameter
        self.curve2.mousePressEvent = self.show_pop_parameter_factory1_2
        self.curve3.mousePressEvent = self.show_pop_parameter_factory1_3
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
            "factory1_3_set_data_curve",
            "factory1_1_production_data",
            "factory1_2_production_data",
            "factory1_3_production_data"
        ]
        # 添加管径实时曲线
        self.curve_plotter1 = RealTimeMainWindowCurve1(
            parent_widget=self.curve1,  # 对应UI中的曲线容器
            params_config={
                'curve3': 'diameter_difference',
                'curve1': 'upper_limit_alarm',
                'curve6': 'lower_limit_alarm',
                'curve4': 'tension_percentage',
                'curve2': 'upper_limit_warning',
                'curve5': 'lower_limit_warning'
            },
            y_limits=(-1, 1)
        )
        self.curve_plotter2 = RealTimeMainWindowCurve1(
            parent_widget=self.curve2,  # 对应UI中的曲线容器
            params_config={
                'curve3': 'diameter_difference',
                'curve1': 'upper_limit_alarm',
                'curve6': 'lower_limit_alarm',
                'curve4': 'tension_percentage',
                'curve2': 'upper_limit_warning',
                'curve5': 'lower_limit_warning'
            },
            y_limits=(-1, 1)
        )
        self.curve_plotter3 = RealTimeMainWindowCurve1(
            parent_widget=self.curve3,  # 对应UI中的曲线容器
            params_config={
                'curve3': 'diameter_difference',
                'curve1': 'upper_limit_alarm',
                'curve6': 'lower_limit_alarm',
                'curve4': 'tension_percentage',
                'curve2': 'upper_limit_warning',
                'curve5': 'lower_limit_warning'
            },
            y_limits=(-1, 1)
        )

        # 在初始化曲线后添加事件穿透设置
        self.curve_plotter1.canvas.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.curve_plotter2.canvas.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.curve_plotter3.canvas.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        self._start_data_update_thread(self.tables_to_monitor)

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
            "factory1_1_set_data_curve":  self.curve_plotter1.update_plot,
            "factory1_2_set_data_curve":  self.curve_plotter2.update_plot,
            "factory1_3_set_data_curve":  self.curve_plotter3.update_plot,
            "factory1_1_production_data": self._update_curve1_realtime,
            "factory1_2_production_data": self._update_curve2_realtime,
            "factory1_3_production_data": self._update_curve3_realtime
        }

        # 获取并执行对应的更新策略
        if strategy := update_strategies.get(table_name):
            if isinstance(strategy, list):  # 处理多个方法的情况。isinstance() 是 Python 的一个内置函数，用于检查一个对象是否属于指定的类型（或类型的元组）。在你的代码中，它被用来判断 strategy 是否是一个列表(list)。
                for method in strategy:
                    method(data)    # type: ignore[attr-defined]
            else:
                strategy(data)  # type: ignore[attr-defined]
    # 分解原有的大更新方法为多个私有方法

    # 分解原有的大更新方法为多个私有方法
    def _update_curve1_realtime(self, data):
        """更新挤出机实时数据"""
        self.curve1_lable2.setText(str(data.get('current_production', '')))
        self.curve1_lable4.setText(str(data.get('planned_production', '')))
        self.curve1_lable6.setText(str(data.get('qualified_products', '')))
        self.curve1_lable8.setText(str(data.get('pass_rate', '')))
        self.curve1_lable10.setText(str(data.get('extruder_rpm', '')))  # 使用get方法提供默认值

    def _update_curve2_realtime(self, data):
        """更新挤出机实时数据"""
        self.curve2_lable2.setText(str(data.get('current_production', '')))
        self.curve2_lable4.setText(str(data.get('planned_production', '')))
        self.curve2_lable6.setText(str(data.get('qualified_products', '')))
        self.curve2_lable8.setText(str(data.get('pass_rate', '')))
        self.curve2_lable10.setText(str(data.get('extruder_rpm', '')))  # 使用get方法提供默认值

    def _update_curve3_realtime(self, data):
        """更新挤出机实时数据"""
        self.curve3_lable2.setText(str(data.get('current_production', '')))
        self.curve3_lable4.setText(str(data.get('planned_production', '')))
        self.curve3_lable6.setText(str(data.get('qualified_products', '')))
        self.curve3_lable8.setText(str(data.get('pass_rate', '')))
        self.curve3_lable10.setText(str(data.get('extruder_rpm', '')))  # 使用get方法提供默认值

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

        # 隐藏历史参数弹窗
        if hasattr(self, 'dialog_historical') and self.dialog_historical.isVisible():
            self.dialog_historical.hide()
        if hasattr(self, 'dialog_historical_factory1_2') and self.dialog_historical_factory1_2.isVisible():
            self.dialog_historical_factory1_2.hide()
        if hasattr(self, 'dialog_historical_factory1_3') and self.dialog_historical_factory1_3.isVisible():
            self.dialog_historical_factory1_3.hide()

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

        # 关闭所有历史参数弹窗
        if hasattr(self, 'dialog_historical'):
            self.dialog_historical.close()
        if hasattr(self, 'dialog_historical_factory1_2'):
            self.dialog_historical_factory1_2.close()
        if hasattr(self, 'dialog_historical_factory1_3'):
            self.dialog_historical_factory1_3.close()

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
        return now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"), start_time.strftime("%H:%M:%S")

    def update_time(self):
        """更新时间显示的方法"""
        date_str, time_str, start_time = self.get_localtime()  # 解包日期时间
        self.title_DATA.setText(date_str)  # 更新日期标签
        self.title_time.setText(time_str)  # 更新时间标签
        self.curve1_lable9_14.setText(start_time)  # 更新1#曲线起始时间标签
        self.curve1_lable9_20.setText(start_time)  # 更新2#曲线起始时间标签
        self.curve1_lable9_24.setText(start_time)  # 更新3#曲线起始时间标签
        self.curve1_lable9_15.setText(time_str)  # 更新1#曲线截止时间标签
        self.curve1_lable9_21.setText(time_str)  # 更新2#曲线截止时间标签
        self.curve1_lable9_25.setText(time_str)  # 更新3#曲线截止时间标签

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

        # 关闭所有历史参数弹窗
        if hasattr(self, 'dialog_historical'):
            self.dialog_historical.close()
        if hasattr(self, 'dialog_historical_factory1_2'):
            self.dialog_historical_factory1_2.close()
        if hasattr(self, 'dialog_historical_factory1_3'):
            self.dialog_historical_factory1_3.close()

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

    def run(self):  # 定义线程运行方法(处理整数数据)
        # 导入sleep函数用于线程休眠
        from time import sleep
        # 开始异常捕获(最外层)
        try:
            while self.keep_running:  # 主循环，当keep_running为True时持续运行
                try:  # 中层异常捕获(连接和数据采集)
                    if not self.init_connection():  # 尝试初始化连接
                        sleep(1)  # 连接失败则休眠1秒
                        continue  # 跳过本次循环，重新尝试

                    # 新调用方式（一次处理所有表）
                    success = self.inserter.insert_multiple_tables_data(
                        table_groups=self.groups,  # 寄存器组配置
                        sock=self.sock  # 已建立的socket连接
                    )
                    # sleep(0.1)

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

        finally:  # 无论是否发生异常都会执行的代码块
            self.cleanup()  # 清理socket连接等资源
            self.finished.emit()  # type: ignore[attr-defined]# 发射完成信号通知主线程

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
class AlarmHistoryQueryWorker(QObject, PublicDataUpdate):
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
        self.alarm_field_map = {
            'P0M43': '尺寸下限报警',
            'P0M45': '尺寸上限报警',
            'P0M46': '尺寸下限预警',
            'P0M48': '尺寸上限预警',
            'P0M41': '温度未达标！',
            'P0X21': '螺旋伺服报警！',
            'P0X20': '牵引伺服报警！',
            'P0M31': '切刀护罩打开！',
            'P0M6': '切刀伺服异常报警或未上电！',
            'P0M22': '切刀异常！',
            'P1FJSF_ALM': '分拣伺服异常！',
            'P2D8030': '温区1传感器断线或损坏！',
            'P2D8031': '温区2传感器断线或损坏！',
            'P2D8032': '温区3传感器断线或损坏！',
            'P2D8033': '温区4传感器断线或损坏！',
            'P2D8036': '温区5传感器断线或损坏！',
            'P2M98': '变频器通讯中断！',
            'P2X12': '变频器报警！',
            'P2M99': '变频器通讯中断!'
        }
        self.alarm_fields = list(self.alarm_field_map.keys())

    @staticmethod
    def _format_record_time(value):
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(value, str):
            return value.replace("T", " ")
        return str(value) if value is not None else ""

    @staticmethod
    def _parse_device_id(table_name):
        parts = table_name.split('_')
        if len(parts) >= 2 and parts[1].isdigit():
            return parts[1]
        return "未知"

    def _get_prev_record_before_start(self, table_name):
        conn = self.hist_data_manager.connection_pool.get_connection()
        try:
            cursor = conn.cursor(dictionary=True)
            query = f"""SELECT * FROM {table_name} WHERE timestamp < %s ORDER BY timestamp DESC LIMIT 1"""
            cursor.execute(query, (self.start_time_str,))
            return cursor.fetchone()
        finally:
            try:
                if conn.is_connected():
                    conn.close()
            except Exception:
                pass

    def run(self):
        """执行报警历史数据查询任务"""
        try:
            all_alarms = []

            for table_name in self.alarm_tables:
                alarm_data = self.hist_data_manager.get_historical_data(
                    table_name,
                    self.start_time_str,
                    self.end_time_str
                )

                if not alarm_data:
                    continue

                prev = self._get_prev_record_before_start(table_name) or {}
                device_id = self._parse_device_id(table_name)

                for record in alarm_data:
                    record_time = self._format_record_time(record.get('timestamp', self.start_time_str))

                    for field in self.alarm_fields:
                        if field not in record and field not in prev:
                            continue

                        prev_raw = prev.get(field, 0)
                        cur_raw = record.get(field, 0)

                        try:
                            prev_v = int(prev_raw) if prev_raw is not None else 0
                        except Exception:
                            prev_v = 0

                        try:
                            cur_v = int(cur_raw) if cur_raw is not None else 0
                        except Exception:
                            cur_v = 0

                        if prev_v == 0 and cur_v == 1:
                            alarm_content = self.alarm_field_map.get(field, field)
                            alarm_text = f"[{record_time}] 设备{device_id}: {alarm_content}"
                            all_alarms.append((record_time, alarm_text))

                    prev = record

            all_alarms.sort(key=lambda x: x[0], reverse=True)
            self.data_ready.emit(all_alarms)  # type: ignore[attr-defined]
        except Exception as e:
            print(f"报警历史数据查询异常: {str(e)}")
            self.error.emit(f"查询失败: {str(e)}")  # type: ignore[attr-defined]
        finally:
            self.finished.emit()  # type: ignore[attr-defined]


# ---------------------------------程序入口---------------------------------
if __name__ == '__main__':
    app = QApplication(sys.argv)  # 创建应用实例
    mainWindow = MainWindow()  # 创建主窗口对象
    mainWindow.show()  # 显示主窗口
    sys.exit(app.exec_())  # 进入主事件循环
