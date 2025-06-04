# 必须在所有代码之前添加这两行
# import sys
# sys.breakpointhook = lambda: None  # 修复Python 3.13的调试器hook
#
# i = 1
# while i < 10:
#     print(i)
# try:
#     a = int(input('请输入第一条边长：'))
#     b = int(input('请输入第二条边长：'))
#     c = int(input('请输入第三条边长：'))
#     if a + b > c and a + c > b and b + c > a:
#         print('三角形周长为：%d' % (a + b + c))
#     else:
#         raise Exception('三角形不存在')
# except Exception as e:
#     print(e)

# def sum1(a, b):
#     return a + b
#
#
# print(sum1(1, 2))
# print(format(3.14, '20'))


# def fun(n):
#     if n < 0:
#         return -1
#     elif n == 1:
#         return 1
#     else:
#         lst = [2, 8]
#         for i in range(1, n):
#             lst.append(lst[-1] + lst[-2])
#             return lst[-2] % lst[-1]
#
#
# print(fun(7))
# import random
#
#
# def get_max(lst):
#     x = lst[0]
#     for i in range(1, len(lst)):
#         if x < lst[i]:
#             x = lst[i]
#     return x
#
#
# lst = [random.randint(1, 100) for i in range(10)]
# print(lst)
# print(get_max(lst))

# def get_digit(n):
#     s = 0
#     lst = []
#     for _ in n:
#         if _.isdigit():
#             lst.append(int(_))
#     s = sum(lst)
#     return lst, s
#
# a = str(input("请输入一个字符串:"))
# lst, x =get_digit(a)
# print(f'提取的数字列表为L：{lst}')
# print(f"累加和为:{x}")

# def lower_upper(s):
#     lst = []
#     for _ in s:
#         if 'A' <= _ <= 'Z':
#             lst.append(chr(ord(_) + 32))
#         elif 'a' <= _ <= 'z':
#             lst.append(chr(ord(_) - 32))
#         else:
#             lst.append(_)
#     return "".join(lst)
#
# s = input("请输入一个字符串:")
# new_s = lower_upper(s)
# print(f"转换后的字符串为:{new_s}")
# class student:
#     scholl = '清华大学'
#
#     def __init__(self, xm, age):
#         self.name = xm
#         self.age = age
#
#     def show(self):
#         print(f'姓名:{self.name},年龄:{self.age}')
#
#     @staticmethod
#     def sm():
#         print('这是一个静态方法')
#
#     @classmethod
#     def cm(cls):
#         # print(cls.scholl)
#         print('这是一个类方法')
#
#
# # # # 测试函数
# # # if __name__ == "__main__":
# # inserter = student(123, 18)
# # # print(inserter.scholl)
# # inserter.show()
# # student.sm()
# stu = student('张三', 18)
# stu2 = student('李四', 19)
# stu3 = student('王五', 20)
# stu4 = student('赵六', 21)
# lst = [stu, stu2, stu3, stu4]
# for _ in lst:
#     _.show()
#
# stu.gender = '男'
# print(stu.gender)
#
#
# def introduce():
#     print('我叫%s,今年%d岁' % (stu.name, stu.age))
#
# stu2.func = introduce
# stu2.func()

# class Circle:
#     def __init__(self, r):
#         self.r = r
#
#     def get_area(self):
#         return 3.14 * self.r ** 2
#
#     def get_perimeter(self):
#         return 2 * 3.14 * self.r
#
#
# # 创建对象
# r = int(input('请输入圆的半径：'))
#
# c = Circle(r)
# print('圆的面积：', c.get_area())
# print('圆的周长：', c.get_perimeter())
# class Student:
#     def __init__(self, name, age, gender, scores):
#         self.name = name
#         self.age = age
#         self.gender = gender
#         self.scores = scores
#
#     def info(self):
#         print(f"姓名：{self.name}，年龄：{self.age}，性别：{self.gender}，分数：{self.scores}")
#
#
# print('请输入5位学生信息：（姓名# 年龄 # 性别 #成绩）')
# lst = []
# for _ in range(1, 6):
#     s = input(f'请输入第{_}位学生信息：')
#     s_lst = s.split('#')
#
#     stu = Student(s_lst[0], int(s_lst[1]), s_lst[2], int(s_lst[3]))
#     lst.append(stu)
#
# for _ in lst:
#     _.info()

# class Instrument:
#
#     def make_sound(self):
#         print('乐器正在演奏...')
#
#
# class Erhu(Instrument):
#
#     def make_sound(self):
#         print('二胡正在演奏...')
#
#
# class Piano(Instrument):
#
#     def make_sound(self):
#         print('钢琴正在演奏...')
#
#
# class Violin(Instrument):
#
#     def make_sound(self):
#         print('小提琴正在演奏...')
#
#
# def play(obj):
#     obj.make_sound()
#
# erhu = Erhu()
# piano = Piano()
# violin = Violin()
# play(erhu)

# class Car:
#     def __init__(self, type, no):
#         self.type = type
#         self.no = no
#
#     def start(self):
#         print('汽车启动了')
#
#     def stop(self):
#         print('汽车停止了')
#
#
# class Taxi(Car):
#     def __init__(self, type, no, company):
#         super().__init__(type, no)
#         self.company = company
#
#     def start(self):
#         print(f"乘客您好，我是{self.company}出租车公司，我的车牌是{self.no}，您要去哪里？")
#
#     def stop(self):
#         print(f"目的地到了，您需要支付元")
#
#
# class FamilyCar(Car):
#     def __init__(self, type, no, name):
#         super().__init__(type, no)
#         self.name = name
#
#     def start(self):
#         print(f"我是{self.name}，我的轿车我做主")
#
#     def stop(self):
#         print(f"目的地到了我们去玩吧")
#
#
# taxi = Taxi('xioami', '京A88888', '北京小米')
# taxi.start()
# taxi.stop()
# print('-' * 30)
# familycar = FamilyCar('奔驰', '京A66666', '武大郎')
# familycar.start()
# familycar.stop()
# table_name = "factory1_1_realtime_data_jcj"
# update_strategies = {
#     # 键：表名字符串 -> 值：对应的更新方法（函数对象）
#     "factory1_1_realtime_data_jcj": 1,  # 挤出机实时数据
#     "factory1_1_realtime_data_fjj": 2,  # 放卷机实时数据
#     "factory1_1_realtime_data_zdj": 3,  # 自动机实时数据
#     "factory1_1_set_data_jcj": 4,  # 挤出机设定数据
#     "factory1_1_set_data_fjj": 5,  # 放卷机设定数据
#     "factory1_1_set_data_zdj": 6,  # 自动机设定数据
#     "factory1_1_set_data_curve": 7  # 曲线设定数据
# }
#
# # 使用海象运算符 := 在条件判断中同时完成赋值操作
# # 1. 从字典中获取对应表名的更新策略（函数对象）
# # 2. 如果找到对应策略（非None），执行该策略
# if strategy := update_strategies.get(table_name):
#     # 调用对应的更新方法，并传入获取到的数据
#     print(update_strategies.get(table_name))
#     print("strategy", strategy)
# 使用海象运算符 := 在条件判断中同时完成赋值操作
# 1. 从字典中获取对应表名的更新策略（函数对象）
# 2. 如果找到对应策略（非None），执行该策略


# import time
# now = time.time()
# print(now)
# a = time.localtime()
# print(a)
# from datetime import datetime,timedelta
# now = datetime.now()
# ago = now - timedelta(minutes=10)
# print(ago.strftime('%H:%M:%S'))

import serial
import time
import threading
from typing import List, Union, Dict, Tuple, Optional
from PyQt5.QtCore import QObject, pyqtSignal, QThread
import mysql.connector
from datetime import datetime
from Data_Manager import inserter  # 导入Data_Manager中的inserter单例


class MelsecFXCommunication:
    def __init__(self, port: str, baudrate: int = 9600, parity: str = 'E',
                 stopbits: int = 1, bytesize: int = 7, station: int = 0xFF):
        """
        初始化FX PLC通信
        :param port: 串口号(如COM3)
        :param baudrate: 波特率(默认9600)
        :param parity: 校验位(N-无校验, E-偶校验, O-奇校验)
        :param stopbits: 停止位(1或2)
        :param bytesize: 数据位(7或8)
        :param station: PLC站号(默认0xFF)
        """
        self.serial = serial.Serial(
            port=port,
            baudrate=baudrate,
            parity=parity,
            stopbits=stopbits,
            bytesize=bytesize,
            timeout=1
        )
        self.station = station
        self._parity_map = {'N': serial.PARITY_NONE, 'E': serial.PARITY_EVEN, 'O': serial.PARITY_ODD}

    def open(self) -> bool:
        """打开串口连接"""
        try:
            if not self.serial.is_open:
                self.serial.open()
            return True
        except Exception as e:
            print(f"串口打开失败: {str(e)}")
            return False

    def close(self) -> None:
        """关闭串口连接"""
        if self.serial and self.serial.is_open:
            self.serial.close()

    def _calculate_crc(self, data: bytes) -> int:
        """计算FX协议校验和"""
        return sum(data) & 0xFF

    def _send_command(self, command: bytes) -> bytes:
        """发送命令并接收响应"""
        try:
            # 添加校验和
            command_with_crc = command + bytes([self._calculate_crc(command)])

            # 发送命令
            self.serial.write(command_with_crc)

            # 读取响应
            header = self.serial.read(1)
            if not header:
                raise TimeoutError("读取响应超时")

            if header[0] == 0x06:  # ACK
                data_len = self.serial.read(1)
                if not data_len:
                    raise TimeoutError("读取数据长度超时")

                data = self.serial.read(data_len[0])
                if len(data) != data_len[0]:
                    raise ValueError("数据长度不匹配")

                crc = self.serial.read(1)
                if not crc:
                    raise TimeoutError("读取校验和超时")

                # 校验和验证
                if self._calculate_crc(header + data_len + data) != crc[0]:
                    raise ValueError("校验和错误")

                return data
            elif header[0] == 0x15:  # NAK
                error_code = self.serial.read(1)
                raise ValueError(f"PLC返回错误: {error_code.hex() if error_code else '未知'}")
            else:
                raise ValueError(f"未知的响应头: {header.hex()}")
        except Exception as e:
            print(f"命令执行失败: {str(e)}")
            return b''

    def read_words(self, address: str, length: int = 1) -> List[int]:
        """
        读取字元件(D)
        :param address: 起始地址(如 "D100")
        :param length: 读取字数
        :return: 字值列表(16位有符号整数)
        """
        try:
            # 解析地址
            if not address.startswith('D'):
                raise ValueError("仅支持D寄存器")

            reg_num = int(address[1:])

            # 构建命令
            command = bytearray([
                0x02,  # STX
                self.station,  # 站号
                0x30, 0x30,  # 命令: 读取
                # 地址(十六进制ASCII)
                *f"{reg_num:04X}".encode(),
                # 长度(十六进制ASCII)
                *f"{length:02X}".encode(),
                0x03  # ETX
            ])

            # 发送命令并接收响应
            response = self._send_command(command)

            # 解析响应
            if not response:
                return [0] * length

            # 每个字占用4个字节(ASCII十六进制)
            values = []
            for i in range(0, len(response), 4):
                if i + 4 <= len(response):
                    hex_str = response[i:i + 4].decode('ascii')
                    values.append(int(hex_str, 16))

            return values
        except Exception as e:
            print(f"读取字元件失败: {str(e)}")
            return [0] * length


# 新增FX3GA数据采集工作线程类
class FX3GAInsertWorker(QObject):
    """FX3GA数据采集工作线程类
    功能：在独立线程中执行FX3GA PLC数据采集和数据库存储
    设计：采用信号槽机制实现线程间通信"""

    # 定义信号
    finished = pyqtSignal()  # 工作完成信号
    error = pyqtSignal(str)  # 错误信号，传递错误信息
    data_updated = pyqtSignal(str, dict)  # 数据更新信号，传递表名和数据

    def __init__(self, port: str, table_groups: List[Tuple[str, List[Tuple[str, int, List[str]]]]],
                 interval: int = 1000):
        """
        初始化工作线程
        :param port: 串口端口名称(如'COM3')
        :param table_groups: 表组列表，格式为[(表名1, [(地址1, 长度1, 字段列表1), ...]), ...]
        :param interval: 采集间隔(毫秒)
        """
        super().__init__()
        self.port = port
        self.table_groups = table_groups
        self.interval = interval
        self.running = False
        self.plc = None

    def run(self):
        """线程执行方法"""
        self.running = True

        try:
            # 创建PLC通信实例
            self.plc = MelsecFXCommunication(self.port)

            # 打开串口连接
            if not self.plc.open():
                self.error.emit(f"无法打开串口 {self.port}")
                self.finished.emit()
                return

            # 主循环 - 持续采集数据
            while self.running:
                try:
                    # 遍历每个表组
                    for table_name, address_groups in self.table_groups:
                        # 收集该表的所有数据
                        table_data = {}

                        # 遍历该表的所有地址组
                        for address, length, fields in address_groups:
                            # 读取PLC数据
                            values = self.plc.read_words(address, length)

                            # 将数据与字段名关联
                            for i, field in enumerate(fields):
                                if i < len(values):
                                    table_data[field] = values[i]

                        # 添加时间戳
                        table_data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                        # 发送数据更新信号
                        self.data_updated.emit(table_name, table_data)

                        # 使用Data_Manager中的inserter将数据存入数据库
                        self._insert_to_database(table_name, table_data)

                    # 等待指定间隔
                    time.sleep(self.interval / 1000)

                except Exception as e:
                    self.error.emit(f"数据采集错误: {str(e)}")
                    # 短暂暂停后继续尝试
                    time.sleep(1)

        except Exception as e:
            self.error.emit(f"工作线程异常: {str(e)}")
        finally:
            # 确保关闭PLC连接
            if self.plc:
                self.plc.close()

            # 发送完成信号
            self.finished.emit()

    @staticmethod
    def _insert_to_database(table_name: str, data: Dict):
        """将数据插入数据库
        :param table_name: 表名
        :param data: 数据字典
        """
        try:
            # 准备字段和值
            fields = list(data.keys())
            if 'timestamp' in fields:
                fields.remove('timestamp')  # 时间戳单独处理

            values = [data[field] for field in fields]

            # 构建插入SQL
            columns = ",".join(fields)
            placeholders = ",".join(["%s"] * (len(fields) + 1))  # +1 for timestamp

            # 使用连接池获取连接
            with inserter.connection_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    # 执行插入
                    cursor.execute(f"""
                        INSERT INTO {table_name}
                        (timestamp, {columns})
                        VALUES ({placeholders})
                    """, (data['timestamp'], *values))

                    # 自动提交（连接池已设置autocommit=True）

            print(f"成功写入数据到 {table_name}")

        except Exception as e:
            print(f"数据库写入失败: {str(e)}")

    def stop(self):
        """停止工作线程"""
        self.running = False


# 新增FX3GA数据管理类
class FX3GADataManager:
    """FX3GA数据管理类
    功能：管理FX3GA PLC的数据采集线程
    设计：单例模式，确保全局唯一实例"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.__initialized = False
            return cls._instance

    def __init__(self):
        if self.__initialized:
            return
        self.__initialized = True

        self.workers = {}  # 存储工作线程
        self.threads = {}  # 存储QThread实例

    def start_data_collection(self, port: str, table_groups: List[Tuple[str, List[Tuple[str, int, List[str]]]]],
                              interval: int = 1000, worker_id: str = "default"):
        """
        启动数据采集
        :param port: 串口端口
        :param table_groups: 表组配置
        :param interval: 采集间隔(毫秒)
        :param worker_id: 工作线程ID，用于区分多个采集任务
        :return: 是否成功启动
        """
        try:
            # 如果已有同ID的工作线程，先停止它
            if worker_id in self.workers:
                self.stop_data_collection(worker_id)

            # 创建新的工作线程
            thread = QThread()
            worker = FX3GAInsertWorker(port, table_groups, interval)

            # 将工作对象移动到线程
            worker.moveToThread(thread)

            # 连接信号
            thread.started.connect(worker.run)
            worker.finished.connect(thread.quit)
            worker.finished.connect(worker.deleteLater)
            thread.finished.connect(thread.deleteLater)

            # 存储引用
            self.workers[worker_id] = worker
            self.threads[worker_id] = thread

            # 启动线程
            thread.start()

            print(f"已启动FX3GA数据采集线程: {worker_id}")
            return True

        except Exception as e:
            print(f"启动数据采集失败: {str(e)}")
            return False

    def stop_data_collection(self, worker_id: str = "default"):
        """
        停止数据采集
        :param worker_id: 工作线程ID
        :return: 是否成功停止
        """
        if worker_id in self.workers:
            try:
                # 通知工作线程停止
                self.workers[worker_id].stop()

                # 等待线程结束(最多3秒)
                self.threads[worker_id].wait(3000)

                # 清理引用
                del self.workers[worker_id]
                del self.threads[worker_id]

                print(f"已停止FX3GA数据采集线程: {worker_id}")
                return True

            except Exception as e:
                print(f"停止数据采集失败: {str(e)}")

        return False

    def stop_all(self):
        """停止所有数据采集线程"""
        worker_ids = list(self.workers.keys())
        for worker_id in worker_ids:
            self.stop_data_collection(worker_id)


# 创建全局单例实例
fx3ga_manager = FX3GADataManager()

# 使用示例
if __name__ == "__main__":
    # 定义表组配置
    table_groups = [
        # 表名, [(地址, 长度, 字段列表), ...]
        ('factory1_1_realtime_data_jcj', [
            ('D0', 5, ['parameter1', 'parameter2', 'parameter3', 'parameter4', 'parameter5']),
            ('D100', 3, ['parameter6', 'parameter7', 'parameter8'])
        ])
    ]

    # 启动数据采集
    fx3ga_manager.start_data_collection('COM5', table_groups, 1000, 'plc1')

    try:
        # 主线程保持运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # 停止所有数据采集
        fx3ga_manager.stop_all()
