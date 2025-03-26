# 导入系统模块
import sys
from datetime import datetime, timedelta
import socket

# 从PyQt5导入需要的组件
from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog
from PyQt5.QtCore import Qt, QTimer, QObject, pyqtSignal, QThread
# 导入自动生成的UI界面类
from Ui_MainWindow import Ui_MainWindow
from Ui_pop_parameter import Ui_Dialog_Pop_Parameter
from Ui_pop_historical_parameter import Ui_Dialog_Pop_Historical_Parameter
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

        # 创建数据管理器实例（使用默认连接参数）
        self.data_manager = data_manager
        # 创建数据更新定时器（继承自QObject）
        self.data_timer = QTimer(self)
        # 连接定时器信号到更新方法（每秒触发一次）
        self.data_timer.timeout.connect(self.update_realtime_data)  # type: ignore[attr-defined]
        # 启动定时器（间隔1000毫秒=1秒）
        self.data_timer.start(1000)

        # 初始化时间功能
        self.timer = QTimer(self)  # 创建定时器对象
        self.timer.timeout.connect(self.update_time)  # type: ignore[attr-defined] # 连接定时信号
        self.timer.start(1000)  # 启动定时器（1秒间隔）
        self.update_time()  # 立即更新时间显示

        # 创建线程管理器字典
        self.threads = {}

        # 前端根据全局变量CLASS_TABLES自动生成包含所有表名的本地缓存版本字典存入data_versions，
        self.data_versions = {table: 0 for table in data_manager.CLASS_TABLES}
        # 立即触发首次数据加载
        QTimer.singleShot(0, self.update_realtime_data)

        # 合并所有采集任务到单个线程
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
                ])
            ],
            ip="192.168.156.14"
        )
        # 添加管径实时曲线（示例配置）
        self.curve_plotter = RealTimeCurvePlotter(
            parent_widget=self.widget_pop_parameter_curve1,  # 对应UI中的曲线容器
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

        # 添加挤出机参数实时曲线（示例配置）
        self.curve_jcj = RealTimeJcjCurvePlotter(
            parent_widget=self.widget_pop_parameter_curve2,  # 对应UI中的曲线容器
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

    def update_realtime_data(self):
        """智能更新实时数据的方法（主入口）
        功能说明：通过版本号对比机制，只更新发生变化的数据库表
        实现原理：比较数据库当前版本号与本地缓存版本号，触发差异更新"""

        # 从数据库获取所有表的当前版本号（字典结构：{表名: 最新版本号}）
        current_versions = self.data_manager.get_data_versions()

        # 遍历所有表名（current_versions字典的键）
        for table_name in current_versions:
            # 版本号对比：数据库版本 > 本地缓存版本（说明有新数据）
            if current_versions[table_name] > self.data_versions[table_name]:
                # 调用私有方法更新具体表数据
                self._update_table_data(table_name)
                # 更新本地版本号为最新值（保持版本同步）
                self.data_versions[table_name] = current_versions[table_name]

    def _update_table_data(self, table_name):
        """私有方法：更新指定表的数据
        参数说明：
        - table_name: 字符串类型，需要更新的数据库表名称
        执行流程：
        1. 从数据库获取最新数据
        2. 有效性验证
        3. 根据表名选择更新策略
        4. 执行具体更新操作"""

        # 从数据管理器获取指定表的实时数据（返回字典或None）
        data = self.data_manager.get_realtime_data(table_name)

        # 数据有效性检查：如果data为空（None）、空字典或假值
        if not data:
            return  # 提前退出，不执行后续操作

        # 创建策略映射字典（表名与更新方法的对应关系）
        update_strategies = {
            # 键：表名字符串 -> 值：对应的更新方法（函数对象）
            "factory1_1_realtime_data_jcj": self._update_jcj_realtime,  # 挤出机实时数据
            "factory1_1_realtime_data_fjj": self._update_fjj_realtime,  # 放卷机实时数据
            "factory1_1_realtime_data_zdj": self._update_zdj_realtime,  # 自动机实时数据
            "factory1_1_set_data_jcj": self._update_jcj_set,  # 挤出机设定数据
            "factory1_1_set_data_fjj": self._update_fjj_set,  # 放卷机设定数据
            "factory1_1_set_data_zdj": self._update_zdj_set,  # 自动机设定数据
            "factory1_1_set_data_curve": self._update_curve_set  # 曲线设定数据
        }

        # 使用海象运算符 := 在条件判断中同时完成赋值操作
        # 1. 从字典中获取对应表名的更新策略（函数对象）
        # 2. 如果找到对应策略（非None），执行该策略
        if strategy := update_strategies.get(table_name):
            # 调用对应的更新方法，并传入获取到的数据，这里update_strategies.get(table_name)的表名对应的函数对象
            strategy(data)  # type: ignore[attr-defined] # 表名对应的函数对象，括号内参数为data字典，字典内为例如parameter1~parameter11等参数

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
        self.label_105.setText(str(data.get('parameter10', '')))
        print('挤出机实时数据：',
              data.get('parameter1', 'N/A'),
              data.get('parameter2', 'N/A'),
              data.get('parameter3', 'N/A'),
              data.get('parameter4', 'N/A'),
              data.get('parameter5', 'N/A'),
              data.get('parameter6', 'N/A'),
              data.get('parameter7', 'N/A'),
              data.get('parameter8', 'N/A'),
              data.get('parameter9', 'N/A'),
              data.get('parameter10', 'N/A'),
              data.get('parameter11', 'N/A'))  # 使用get方法提供默认值

    def _update_fjj_realtime(self, data):
        """更新挤出机实时数据"""
        self.label_53.setText(str(data.get('parameter12', '')))
        self.label_57.setText(str(data.get('parameter13', '')))
        self.label_61.setText(str(data.get('parameter14', '')))
        self.label_65.setText(str(data.get('parameter15', '')))
        print('放卷机实时数据：',
              data.get('parameter12', 'N/A'),
              data.get('parameter13', 'N/A'),
              data.get('parameter14', 'N/A'),
              data.get('parameter15', 'N/A'))  # 使用get方法提供默认值

    def _update_zdj_realtime(self, data):
        """更新挤出机实时数据"""
        self.label_73.setText(str(data.get('parameter16', '')))
        self.label_77.setText(str(data.get('parameter17', '')))
        self.label_81.setText(str(data.get('parameter18', '')))
        self.label_85.setText(str(data.get('parameter19', '')))
        self.label_89.setText(str(data.get('parameter20', '')))
        self.label_93.setText(str(data.get('parameter21', '')))
        print('自动机实时数据：',
              data.get('parameter16', 'N/A'),
              data.get('parameter17', 'N/A'),
              data.get('parameter18', 'N/A'),
              data.get('parameter19', 'N/A'),
              data.get('parameter20', 'N/A'),
              data.get('parameter21', 'N/A'))  # 使用get方法提供默认值

    def _update_jcj_set(self, data):
        """更新挤出机实时数据"""
        self.lineEdit_4.setText(str(data.get('parameter1', '')))
        self.lineEdit_5.setText(str(data.get('parameter2', '')))
        self.lineEdit_6.setText(str(data.get('parameter3', '')))
        self.lineEdit_7.setText(str(data.get('parameter4', '')))
        self.lineEdit_8.setText(str(data.get('parameter5', '')))
        self.lineEdit_10.setText(str(data.get('parameter6', '')))
        print('挤出机设定数据：',
              data.get('parameter1', 'N/A'),
              data.get('parameter2', 'N/A'),
              data.get('parameter3', 'N/A'),
              data.get('parameter4', 'N/A'),
              data.get('parameter5', 'N/A'),
              data.get('parameter6', 'N/A'))  # 使用get方法提供默认值

    def _update_fjj_set(self, data):
        """更新挤出机实时数据"""
        self.lineEdit_13.setText(str(data.get('parameter1', '')))
        self.lineEdit_14.setText(str(data.get('parameter2', '')))
        self.lineEdit_16.setText(str(data.get('parameter3', '')))
        print('放卷机设定数据：',
              data.get('parameter1', 'N/A'),
              data.get('parameter2', 'N/A'),
              data.get('parameter3', 'N/A'))  # 使用get方法提供默认值

    def _update_zdj_set(self, data):
        """更新挤出机实时数据"""
        self.lineEdit_17.setText(str(data.get('parameter1', '')))
        self.lineEdit_18.setText(str(data.get('parameter2', '')))
        self.lineEdit_19.setText(str(data.get('parameter3', '')))
        self.lineEdit_20.setText(str(data.get('parameter4', '')))
        print('自动机设定数据：',
              data.get('parameter1', 'N/A'),
              data.get('parameter2', 'N/A'),
              data.get('parameter3', 'N/A'),
              data.get('parameter4', 'N/A'))  # 使用get方法提供默认值

    def _update_curve_set(self, data):
        """更新挤出机实时数据"""
        self.lineEdit_23.setText(str(data.get('parameter1', '')))
        self.lineEdit_48.setText(str(data.get('parameter2', '')))
        self.label_114.setText(str(data.get('parameter3', '')))
        self.label_115.setText(str(data.get('parameter4', '')))
        self.lineEdit_51.setText(str(data.get('parameter5', '')))
        self.lineEdit_52.setText(str(data.get('parameter6', '')))
        print('曲线设定实时数据：',
              data.get('parameter1', 'N/A'),
              data.get('parameter2', 'N/A'),
              data.get('parameter3', 'N/A'),
              data.get('parameter4', 'N/A'),
              data.get('parameter5', 'N/A'),
              data.get('parameter6', 'N/A'))  # 使用get方法提供默认值

    # 定义隐藏当前实时数据窗口，显示历史参数弹窗的方法
    def show_dialog_pop_historical_parameter(self):
        self.hide()  # 隐藏当前窗口
        # if not self.dialog_historical:  # 判断是否已存在实例
        #     self.dialog_historical = HistoricalParameterDialog()
        self.dialog_historical.show()

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
        """处理关闭事件：关闭关联的历史参数弹窗"""
        # 检查是否存在历史参数弹窗实例
        if self.dialog_historical:  # 判断dialog_historical是否已初始化
            self.dialog_historical.close()  # 调用历史弹窗的关闭方法
        super().closeEvent(event)  # 调用父类QDialog的关闭事件处理，确保正常关闭流程

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
        # 添加历史数据管理器
        self.hist_data_manager = historical_data_manager
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

        # # 计算结束时间（格式化成SQL可识别的字符串）
        # start_time = query_time.strftime("%Y-%m-%d %H:%M:%S")
        # # 计算起始时间（当前查询时间前推10分钟）
        # end_time = (query_time + timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")


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

        # 遍历所有目标数据表
        for table in tables:
            # 执行精确时间点查询（开始时间=结束时间=目标时间）
            data = self.hist_data_manager.get_nearest_data(
                table,
                exact_time,
                start_time,
                end_time
            )
            # 如果有返回数据（即使只有一条）
            if data:
                # 更新界面标签（取第一条/唯一一条数据）
                self._update_ui_labels(table, data)

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
            self.label_124.setText(str(data.get('parameter10', '')))
            print('挤出机历史数据：',
                  data.get('parameter1', 'N/A'),
                  data.get('parameter2', 'N/A'),
                  data.get('parameter3', 'N/A'),
                  data.get('parameter4', 'N/A'),
                  data.get('parameter5', 'N/A'),
                  data.get('parameter6', 'N/A'),
                  data.get('parameter7', 'N/A'),
                  data.get('parameter8', 'N/A'),
                  data.get('parameter9', 'N/A'),
                  data.get('parameter10', 'N/A'),
                  data.get('parameter11', 'N/A'))  # 使用get方法提供默认值
            # ... 其他参数更新逻辑（保持相同模式）

        # 放卷机实时数据表处理分支
        elif table_name == "factory1_1_realtime_data_fjj":
            # 更新参数12显示（label_53标签）
            self.label_53.setText(str(data.get('parameter12', '')))
            self.label_57.setText(str(data.get('parameter13', '')))
            self.label_61.setText(str(data.get('parameter14', '')))
            self.label_65.setText(str(data.get('parameter15', '')))
            print('放卷机实时数据：',
                  data.get('parameter12', 'N/A'),
                  data.get('parameter13', 'N/A'),
                  data.get('parameter14', 'N/A'),
                  data.get('parameter15', 'N/A'))  # 使用get方法提供默认值
            # ... 其他参数更新逻辑（保持相同模式）
        # 自动机历史数据表处理分支
        elif table_name == "factory1_1_realtime_data_zdj":
            self.label_73.setText(str(data.get('parameter16', '')))
            self.label_77.setText(str(data.get('parameter17', '')))
            self.label_81.setText(str(data.get('parameter18', '')))
            self.label_85.setText(str(data.get('parameter19', '')))
            self.label_89.setText(str(data.get('parameter20', '')))
            self.label_93.setText(str(data.get('parameter21', '')))
            print('自动机实时数据：',
                  data.get('parameter16', 'N/A'),
                  data.get('parameter17', 'N/A'),
                  data.get('parameter18', 'N/A'),
                  data.get('parameter19', 'N/A'),
                  data.get('parameter20', 'N/A'),
                  data.get('parameter21', 'N/A'))  # 使用get方法提供默认值
        elif table_name == "factory1_1_set_data_jcj":
            self.label_104.setText(str(data.get('parameter1', '')))
            self.label_105.setText(str(data.get('parameter2', '')))
            self.label_106.setText(str(data.get('parameter3', '')))
            self.label_107.setText(str(data.get('parameter4', '')))
            self.label_108.setText(str(data.get('parameter5', '')))
            self.label_115.setText(str(data.get('parameter6', '')))
            print('挤出机设定数据：',
                  data.get('parameter1', 'N/A'),
                  data.get('parameter2', 'N/A'),
                  data.get('parameter3', 'N/A'),
                  data.get('parameter4', 'N/A'),
                  data.get('parameter5', 'N/A'),
                  data.get('parameter6', 'N/A'))  # 使用get方法提供默认值
        elif table_name == "factory1_1_set_data_fjj":
            self.label_109.setText(str(data.get('parameter1', '')))
            self.label_110.setText(str(data.get('parameter2', '')))
            self.label_111.setText(str(data.get('parameter3', '')))
            print('放卷机设定数据：',
                  data.get('parameter1', 'N/A'),
                  data.get('parameter2', 'N/A'),
                  data.get('parameter3', 'N/A'))  # 使用get方法提供默认值
        elif table_name == "factory1_1_set_data_zdj":
            self.label_112.setText(str(data.get('parameter1', '')))
            self.label_113.setText(str(data.get('parameter2', '')))
            self.label_114.setText(str(data.get('parameter3', '')))
            self.label_116.setText(str(data.get('parameter4', '')))
            print('自动机设定数据：',
                  data.get('parameter1', 'N/A'),
                  data.get('parameter2', 'N/A'),
                  data.get('parameter3', 'N/A'),
                  data.get('parameter4', 'N/A'))  # 使用get方法提供默认值
        elif table_name == "factory1_1_set_data_curve":
            self.label_117.setText(str(data.get('parameter1', '')))
            self.label_118.setText(str(data.get('parameter2', '')))
            self.label_114.setText(str(data.get('parameter3', '')))
            self.label_115.setText(str(data.get('parameter4', '')))
            self.label_121.setText(str(data.get('parameter5', '')))
            self.label_122.setText(str(data.get('parameter6', '')))
            print('曲线设定实时数据：',
                  data.get('parameter1', 'N/A'),
                  data.get('parameter2', 'N/A'),
                  data.get('parameter3', 'N/A'),
                  data.get('parameter4', 'N/A'),
                  data.get('parameter5', 'N/A'),
                  data.get('parameter6', 'N/A'))  # 使用get方法提供默认值

    # 定义隐藏当前历史数据窗口，显示实时参数弹窗的方法
    def show_dialog_pop_parameter(self):
        self.hide()  # 隐藏当前窗口
        # if not self.dialog_realtime:  # 判断是否已存在实例
        #     self.dialog_realtime = ParameterDialog()
        self.dialog_realtime.show()


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
        self._start_insert_thread(
            groups=[
                ("factory1_1_alarm_data", [
                    (16, 1, ["parameter1"])
                ])
            ],
            ip="192.168.156.14"
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
        thread.started.connect(worker.run_int)  # type: ignore[attr-defined]
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

    def right_down_dialog(self):
        """将弹窗居中显示的方法"""
        # 获取主屏幕尺寸
        screen = QApplication.primaryScreen().geometry()
        # 计算居中坐标（屏幕宽度-窗口宽度）/2
        x = (screen.width() - self.width())
        y = (screen.height() - self.height())
        # 移动窗口到计算位置
        self.move(x, y)


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
        # 初始化历史弹窗（使用自定义弹窗类）
        self.dialog_historical = HistoricalParameterDialog()
        # 建立实例关联
        self.pop_dialog.dialog_historical = self.dialog_historical
        self.dialog_historical.dialog_realtime = self.pop_dialog
        # 初始化报警弹窗（使用自定义弹窗类）
        self.pop_alarm_dialog = AlarmDialog()

        # 绑定曲线控件的鼠标点击事件
        self.curve1.mousePressEvent = self.show_pop_parameter
        # 绑定曲线控件的鼠标点击事件
        self.pushButton_alarm.mousePressEvent = self.show_pop_alarm
        # 绑定关闭按钮：点击时关闭所有窗口
        self.Button_close.clicked.connect(self.close_all_windows)

        # 初始化时间功能
        self.timer = QTimer(self)  # 创建定时器对象
        self.timer.timeout.connect(self.update_time)  # type: ignore[attr-defined] # 连接定时信号
        self.timer.start(1000)  # 启动定时器（1秒间隔）
        self.update_time()  # 立即更新时间显示

        # 创建数据管理器实例（使用默认连接参数）
        self.data_manager = data_manager
        # 创建数据更新定时器（继承自QObject）
        self.data_timer = QTimer(self)
        # 连接定时器信号到更新方法（每秒触发一次）
        self.data_timer.timeout.connect(self.update_realtime_data)  # type: ignore[attr-defined]
        # 启动定时器（间隔1000毫秒=1秒）
        self.data_timer.start(1000)
        # 创建线程管理器字典
        self.threads = {}
        # 前端根据CLASS_TABLES自动生成包含所有表名的版本字典
        self.data_versions = {table: 0 for table in data_manager.CLASS_TABLES}
        # 立即触发首次数据加载
        QTimer.singleShot(0, self.update_realtime_data)
        # 添加管径实时曲线（示例配置）
        # 合并所有采集任务到单个线程
        self._start_insert_thread(
            groups=[
                ("factory1_1_production_data", [
                (231, 4, ["parameter1", "parameter2"]),
                (237, 4, ["parameter3", "parameter4"]),
                (1, 2, ["parameter5"])
            ])
            ],
            ip="192.168.156.14"
        )
        self.curve_plotter = RealTimeMainWindowCurve1(
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
        # 在初始化曲线后添加事件穿透设置
        self.curve_plotter.canvas.setAttribute(Qt.WA_TransparentForMouseEvents, True)

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

    def update_realtime_data(self):
        """智能更新实时数据的方法"""
        # 获取所有数据表的当前版本号
        current_versions = self.data_manager.get_data_versions()

        # 只更新有变化的表
        for table_name in current_versions:
            if current_versions[table_name] > self.data_versions[table_name]:
                self._update_table_data(table_name)
                self.data_versions[table_name] = current_versions[table_name]

    def _update_table_data(self, table_name):
        """私有方法：更新指定表的数据"""
        data = self.data_manager.get_realtime_data(table_name)
        if not data:
            return

        # 根据表名分发更新逻辑
        update_strategies = {
            "factory1_1_production_data": self._update_curve1_realtime
        }

        if strategy := update_strategies.get(table_name):
            strategy(data)  # type: ignore[attr-defined]

    # 分解原有的大更新方法为多个私有方法
    def _update_curve1_realtime(self, data):
        """更新挤出机实时数据"""
        self.curve1_lable2.setText(str(data.get('parameter1', '')))
        self.curve1_lable4.setText(str(data.get('parameter2', '')))
        self.curve1_lable6.setText(str(data.get('parameter3', '')))
        self.curve1_lable8.setText(str(data.get('parameter4', '')))
        self.curve1_lable10.setText(str(data.get('parameter5', '')))
        print('首页面曲线1实时数据：',
              data.get('parameter1', 'N/A'),
              data.get('parameter2', 'N/A'),
              data.get('parameter3', 'N/A'),
              data.get('parameter4', 'N/A'),
              data.get('parameter5', 'N/A'))  # 使用get方法提供默认值

    def close_all_windows(self):
        """关闭所有窗口的方法"""
        # 遍历所有线程并停止它们
        for thread, worker in self.threads.values():
            worker.stop()  # 停止工作线程
            thread.quit()  # 退出线程
            thread.wait()  # 等待线程退出

        self.pop_dialog.close()  # 关闭参数弹窗（会自动关闭其子弹窗）
        self.pop_alarm_dialog.close()  # 关闭报警弹窗
        self.close()  # 关闭主窗口

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
        self.curve1_lable9_14.setText(start_time)  # 更新日期标签
        self.curve1_lable9_15.setText(time_str)  # 更新时间标签


    def show_pop_parameter(self, event):
        """显示参数弹窗的槽函数"""
        self.pop_dialog.show()  # 显示弹窗
        event.accept()  # 接受事件，阻止进一步传播

    def show_pop_alarm(self, event):
        """显示报警弹窗的槽函数"""
        self.pop_alarm_dialog.show()  # 显示弹窗
        event.accept()  # 接受事件，阻止进一步传播


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

    def run(self):
        from time import sleep
        try:
            while self.keep_running:
                if self.init_connection():
                    try:
                        for group_config in self.groups:  # 每个group_config是(table_name, groups)
                            table_name, groups = group_config
                            success = inserter.insert_combined_mcgs_data(
                                table_name=table_name,
                                groups=groups,
                                ip=self.ip,
                                port=self.port,
                                sock=self.sock
                            )
                            if not success:
                                self.reconnect()
                    except (socket.timeout, ConnectionResetError) as e:
                        print(f"连接异常: {str(e)}，尝试重连...")
                        self.reconnect()
                    except Exception as e:
                        print(f"运行时异常: {str(e)}")
                sleep(1)
        finally:
            self.cleanup()
            self.finished.emit()  # type: ignore[attr-defined]

    def run_int(self):
        from time import sleep
        try:
            while self.keep_running:
                if self.init_connection():
                    try:
                        for group_config in self.groups:  # 每个group_config是(table_name, groups)
                            table_name, groups = group_config
                            success = inserter.insert_combined_mcgs_int_data(
                                table_name=table_name,
                                groups=groups,
                                ip=self.ip,
                                port=self.port,
                                sock=self.sock
                            )
                            if not success:
                                self.reconnect()
                    except (socket.timeout, ConnectionResetError) as e:
                        print(f"连接异常: {str(e)}，尝试重连...")
                        self.reconnect()
                    except Exception as e:
                        print(f"运行时异常: {str(e)}")
                sleep(1)
        finally:
            self.cleanup()
            self.finished.emit()  # type: ignore[attr-defined]

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



# ---------------------------------程序入口---------------------------------
if __name__ == '__main__':
    app = QApplication(sys.argv)  # 创建应用实例
    mainWindow = MainWindow()  # 创建主窗口对象
    mainWindow.show()  # 显示主窗口
    sys.exit(app.exec_())  # 进入主事件循环
