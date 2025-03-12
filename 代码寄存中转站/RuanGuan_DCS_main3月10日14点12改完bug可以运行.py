# 导入系统模块
import sys
# 从PyQt5导入需要的组件
from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog
from PyQt5.QtCore import Qt, QTimer
# 导入自动生成的UI界面类
from Ui_MainWindow import Ui_MainWindow
from Ui_pop_parameter import Ui_Dialog_Pop_Parameter
from Ui_pop_historical_parameter import Ui_Dialog_Pop_Historical_Parameter
from Ui_pop_alarm import Ui_Dialog_alarm
from Data_Manager import DataManager, inserter


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
        # 设置窗口属性
        self.setWindowFlags(Qt.FramelessWindowHint)  # 无边框
        self.center_dialog()  # 初始居中显示

        # 创建数据管理器实例（使用默认连接参数）
        self.data_manager = DataManager()
        # 创建数据更新定时器（继承自QObject）
        self.data_timer = QTimer(self)
        # 连接定时器信号到更新方法（每秒触发一次）
        self.data_timer.timeout.connect(self.update_realtime_data)
        # 启动定时器（间隔1000毫秒=1秒）
        self.data_timer.start(1000)

        # 定义七个不连续的寄存器组（地址11读4寄存器，地址21读8寄存器，地址15读2寄存器···）
        groups_config = [
            (11, 4, ["parameter1", "parameter2"]),
            (21, 8, ["parameter3", "parameter4", "parameter5", "parameter6"]),
            (15, 2, ["parameter7"]),
            (31, 2, ["parameter8"]),
            (1, 2, ["parameter9"]),
            (5, 2, ["parameter10"]),
            (7, 2, ["parameter11"])
        ]

        # 执行组合采集（所有参数一次性写入factory1_1_realtime_data_jcj表）
        inserter.insert_combined_mcgs_data(
            table_name="factory1_1_realtime_data_jcj",
            groups=groups_config,
            ip="192.168.10.30"
        )

        # 定义三个不连续的寄存器组（地址103读2寄存器，地址107读4寄存器，地址113读2寄存器）
        groups_config = [
            (103, 2, ["parameter1"]),
            (107, 4, ["parameter2", "parameter4"]),
            (113, 2, ["parameter3"])
        ]

        # 执行组合采集（所有参数一次性写入factory1_1_realtime_data_fjj表）
        inserter.insert_combined_mcgs_data(
            table_name="factory1_1_realtime_data_fjj",
            groups=groups_config,
            ip="192.168.10.30"
        )

        # 定义三个不连续的寄存器组（地址221读2寄存器，地址217读2寄存器，地址203读2寄存器）
        groups_config = [
            (221, 2, ["parameter1"]),
            (217, 2, ["parameter2"]),
            (203, 2, ["parameter3"]),
            (231, 2, ["parameter4"]),
            (235, 2, ["parameter5"]),
            (239, 2, ["parameter6"])
        ]

        # 执行组合采集（所有参数一次性写入factory1_1_realtime_data_zdj表）
        inserter.insert_combined_mcgs_data(
            table_name="factory1_1_realtime_data_zdj",
            groups=groups_config,
            ip="192.168.10.30"
        )

    def update_realtime_data(self):
        """定时更新实时数据的方法"""
        # 调用数据管理器获取factory1_1_realtime_data_jcj的数据
        data = self.data_manager.get_realtime_data("factory1_1_realtime_data_jcj")
        if data:  # 如果成功获取数据
            # 更新界面显示（示例代码，需根据实际UI控件调整）：
            self.label_10.setText(str(data['parameter1']))  # 更新数值1标签
            self.label_14.setText(str(data['parameter2']))  # 更新数值2标签
            self.label_18.setText(str(data['parameter3']))  # 更新数值3标签
            self.label_22.setText(str(data['parameter4']))  # 更新数值4标签
            self.label_26.setText(str(data['parameter5']))  # 更新数值5标签
            self.label_30.setText(str(data['parameter6']))  # 更新数值6标签
            self.label_34.setText(str(data['parameter7']))  # 更新数值7标签
            self.label_38.setText(str(data['parameter8']))  # 更新数值8标签
            self.label_42.setText(str(data['parameter9']))  # 更新数值9标签
            self.label_46.setText(str(data['parameter10']))  # 更新数值10标签
            self.label_50.setText(str(data['parameter11']))  # 更新数值11标签
            print('挤出机实时数据：', data['parameter1'], data['parameter2'], data['parameter3'], data['parameter4'], data['parameter5'], data['parameter6'], data['parameter7'], data['parameter8'],
                  data['parameter9'], data['parameter10'], data['parameter11'])  # 测试用，打印数据

        # 调用数据管理器获取factory1_1_realtime_data_fjj的数据
        data = self.data_manager.get_realtime_data("factory1_1_realtime_data_fjj")
        if data:  # 如果成功获取数据
            # 更新界面显示（示例代码，需根据实际UI控件调整）：
            self.label_53.setText(str(data['parameter1']))  # 更新数值1标签
            self.label_57.setText(str(data['parameter2']))  # 更新数值2标签
            self.label_61.setText(str(data['parameter3']))  # 更新数值3标签
            self.label_65.setText(str(data['parameter4']))  # 更新数值4标签
            print('放卷机实时数据：', data['parameter1'], data['parameter2'], data['parameter3'], data['parameter4'])  # 测试用，打印数据

        # 调用数据管理器获取factory1_1_realtime_data_jcj的数据
        data = self.data_manager.get_realtime_data("factory1_1_realtime_data_zdj")
        if data:  # 如果成功获取数据
            # 更新界面显示（示例代码，需根据实际UI控件调整）：
            self.label_73.setText(str(data['parameter1']))  # 更新数值1标签
            self.label_77.setText(str(data['parameter2']))  # 更新数值2标签
            self.label_81.setText(str(data['parameter3']))  # 更新数值3标签
            self.label_85.setText(str(data['parameter4']))  # 更新数值4标签
            self.label_89.setText(str(data['parameter5']))  # 更新数值5标签
            self.label_93.setText(str(data['parameter6']))  # 更新数值6标签
            print('自动机实时数据：', data['parameter1'], data['parameter2'], data['parameter3'], data['parameter4'], data['parameter5'], data['parameter6'])  # 测试用，打印数据

        # 调用数据管理器获取factory1_1_set_data_jcj的数据
        data = self.data_manager.get_realtime_data("factory1_1_set_data_jcj")
        if data:  # 如果成功获取数据
            # 更新界面显示（示例代码，需根据实际UI控件调整）：
            self.lineEdit_4.setText(str(data['parameter1']))  # 更新数值1标签
            self.lineEdit_5.setText(str(data['parameter2']))  # 更新数值2标签
            self.lineEdit_6.setText(str(data['parameter3']))  # 更新数值3标签
            self.lineEdit_7.setText(str(data['parameter4']))  # 更新数值4标签
            self.lineEdit_8.setText(str(data['parameter5']))  # 更新数值5标签
            self.lineEdit_10.setText(str(data['parameter6']))  # 更新数值6标签
            print('挤出机设定数据：', data['parameter1'], data['parameter2'], data['parameter3'], data['parameter4'], data['parameter5'], data['parameter6'])  # 测试用，打印数据

        # 调用数据管理器获取factory1_1_set_data_fjj的数据
        data = self.data_manager.get_realtime_data("factory1_1_set_data_fjj")
        if data:  # 如果成功获取数据
            # 更新界面显示（示例代码，需根据实际UI控件调整）：
            self.lineEdit_13.setText(str(data['parameter1']))  # 更新数值1标签
            self.lineEdit_14.setText(str(data['parameter2']))  # 更新数值2标签
            self.lineEdit_16.setText(str(data['parameter3']))  # 更新数值3标签
            print('放卷机设定数据：', data['parameter1'], data['parameter2'], data['parameter3'])  # 测试用，打印数据

        # 调用数据管理器获取factory1_1_set_data_zdj的数据
        data = self.data_manager.get_realtime_data("factory1_1_set_data_zdj")
        if data:  # 如果成功获取数据
            # 更新界面显示（示例代码，需根据实际UI控件调整）：
            self.lineEdit_17.setText(str(data['parameter1']))  # 更新数值1标签
            self.lineEdit_18.setText(str(data['parameter2']))  # 更新数值2标签
            self.lineEdit_19.setText(str(data['parameter3']))  # 更新数值3标签
            self.lineEdit_20.setText(str(data['parameter4']))  # 更新数值4标签
            print('自动机设定数据：', data['parameter1'], data['parameter2'], data['parameter3'], data['parameter4'])  # 测试用，打印数据

        # 调用数据管理器获取factory1_1_set_data_curve的数据
        data = self.data_manager.get_realtime_data("factory1_1_set_data_curve")
        if data:  # 如果成功获取数据
            # 更新界面显示（示例代码，需根据实际UI控件调整）：
            self.lineEdit_23.setText(str(data['parameter1']))  # 更新数值1标签
            self.lineEdit_48.setText(str(data['parameter2']))  # 更新数值2标签
            self.lineEdit_49.setText(str(data['parameter3']))  # 更新数值3标签
            self.lineEdit_50.setText(str(data['parameter4']))  # 更新数值4标签
            self.lineEdit_51.setText(str(data['parameter5']))  # 更新数值5标签
            self.lineEdit_52.setText(str(data['parameter6']))  # 更新数值6标签
            print('上曲线设定数据：', data['parameter1'], data['parameter2'], data['parameter3'], data['parameter4'], data['parameter5'], data['parameter6'])  # 测试用，打印数据

        # 调用数据管理器获取factory1_1_realtime_data_jcj的数据，更改温区曲线下数据框数据
        data = self.data_manager.get_realtime_data("factory1_1_realtime_data_jcj")
        if data:  # 如果成功获取数据
            # 更新界面显示（示例代码，需根据实际UI控件调整）：
            self.lineEdit_24.setText(str(data['parameter3']))  # 更新数值3标签
            self.lineEdit_54.setText(str(data['parameter4']))  # 更新数值4标签
            self.lineEdit_57.setText(str(data['parameter5']))  # 更新数值5标签
            self.lineEdit_56.setText(str(data['parameter6']))  # 更新数值6标签
            self.label_104.setText(str(data['parameter9']))  # 更新数值9标签
            self.label_105.setText(str(data['parameter10']))  # 更新数值10标签
            print('下曲线设定数据：', data['parameter3'], data['parameter4'], data['parameter5'], data['parameter6'], data['parameter9'], data['parameter10'])  # 测试用，打印数据

    # 定义隐藏当前实时数据窗口，显示历史参数弹窗的方法
    def show_dialog_pop_historical_parameter(self):
        self.hide()  # 隐藏当前窗口
        self.dialog_historical = HistoricalParameterDialog()  # 创建历史数据曲线对话框并传递父对象
        self.dialog_historical.show()  # 显示弹窗

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
        # 设置窗口属性
        self.setWindowFlags(Qt.FramelessWindowHint)  # 无边框
        self.center_dialog()  # 初始居中显示

    # 定义隐藏当前历史数据窗口，显示实时参数弹窗的方法
    def show_dialog_pop_parameter(self):
        self.hide()  # 隐藏当前窗口
        self.dialog_realtime = ParameterDialog()  # 创建实时数据曲线对话框并传递父对象
        self.dialog_realtime.show()  # 显示弹窗

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

        # 设置窗口属性
        self.setWindowFlags(Qt.FramelessWindowHint)  # 置顶+无边框
        self.right_down_dialog()  # 初始右下角显示

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
        self.timer.timeout.connect(self.update_time)  # 连接定时信号
        self.timer.start(1000)  # 启动定时器（1秒间隔）
        self.update_time()  # 立即更新时间显示

        # 创建数据管理器实例（使用默认连接参数）
        self.data_manager = DataManager()
        # 创建数据更新定时器（继承自QObject）
        self.data_timer = QTimer(self)
        # 连接定时器信号到更新方法（每秒触发一次）
        self.data_timer.timeout.connect(self.update_realtime_data)
        # 启动定时器（间隔1000毫秒=1秒）
        self.data_timer.start(1000)

        # 定义七个不连续的寄存器组（地址231读4寄存器，地址237读4寄存器，地址1读2寄存器···）
        groups_config = [
            (231, 4, ["parameter1", "parameter2"]),
            (237, 4, ["parameter3", "parameter4"]),
            (1, 2, ["parameter5"])
        ]

        # 执行组合采集（所有参数一次性写入factory1_1_production_data表）
        inserter.insert_combined_mcgs_data(
            table_name="factory1_1_production_data",
            groups=groups_config,
            ip="192.168.10.30"
        )

    def update_realtime_data(self):
        """定时更新实时数据的方法"""
        # 调用数据管理器获取factory1_1_production_data的数据
        data = self.data_manager.get_realtime_data("factory1_1_production_data")
        if data:  # 如果成功获取数据
            # 更新界面显示（示例代码，需根据实际UI控件调整）：
            self.curve1_lable2.setText(str(data['parameter1']))  # 更新数值1标签
            self.curve1_lable4.setText(str(data['parameter2']))  # 更新数值2标签
            self.curve1_lable6.setText(str(data['parameter3']))  # 更新数值3标签
            self.curve1_lable8.setText(str(data['parameter4']))  # 更新数值4标签
            self.curve1_lable10.setText(str(data['parameter5']))  # 更新数值5标签
            print('首页面曲线1数据：', data['parameter1'], data['parameter2'], data['parameter3'], data['parameter4'], data['parameter5'])  # 测试用，打印数据

    def close_all_windows(self):
        """关闭所有窗口的方法"""
        self.pop_dialog.close()  # 关闭参数弹窗（会自动关闭其子弹窗）
        self.pop_alarm_dialog.close()  # 关闭报警弹窗
        self.close()  # 关闭主窗口

    @staticmethod  # 静态方法，不依赖实例对象
    def get_localtime():
        """获取本地时间的静态方法"""
        from datetime import datetime
        now = datetime.now()  # 获取当前时间对象
        # 返回格式化后的日期和时间字符串
        return now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")

    def update_time(self):
        """更新时间显示的方法"""
        date_str, time_str = self.get_localtime()  # 解包日期时间
        self.title_DATA.setText(date_str)  # 更新日期标签
        self.title_time.setText(time_str)  # 更新时间标签

    def show_pop_parameter(self, event):
        """显示参数弹窗的槽函数"""
        self.pop_dialog.show()  # 显示弹窗
        event.accept()  # 接受事件，阻止进一步传播

    def show_pop_alarm(self, event):
        """显示报警弹窗的槽函数"""
        self.pop_alarm_dialog.show()  # 显示弹窗
        event.accept()  # 接受事件，阻止进一步传播


# ---------------------------------程序入口---------------------------------
if __name__ == '__main__':
    app = QApplication(sys.argv)  # 创建应用实例
    mainWindow = MainWindow()  # 创建主窗口对象
    mainWindow.show()  # 显示主窗口
    sys.exit(app.exec_())  # 进入主事件循环
