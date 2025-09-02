import sys
import serial
import time
import struct
import mysql.connector
from datetime import datetime
# 添加PyQt5相关导入
from PyQt5.QtCore import QObject, pyqtSignal, QThread, Qt
from PyQt5.QtWidgets import QApplication, QComboBox, QWidget, QVBoxLayout, QMainWindow
from Ui_LocalCollectParameter import Ui_MainWindow

class PlcDataManager:
    def __init__(self, pool_name='plc_pool', pool_size=3):
        self.config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'admin',
            'database': 'dcs_data',
            'pool_name': pool_name,
            'pool_size': pool_size
        }
        self.cnxpool = mysql.connector.pooling.MySQLConnectionPool(**self.config)

    def save_combined_data(self, table_name: str, data_dict: dict):
        """通用组合数据存储方法"""
        fields = [k for k in data_dict if k != 'timestamp']

        # 修复占位符格式
        query = f"""INSERT INTO {table_name} 
                   (timestamp, {','.join(fields)})
                   VALUES (%(timestamp)s, {','.join([f'%({f})s' for f in fields])})
                   ON DUPLICATE KEY UPDATE 
                   {','.join([f"{f}=VALUES({f})" for f in fields])}"""

        try:
            cnx = self.cnxpool.get_connection()
            cursor = cnx.cursor()
            cursor.execute(query, data_dict)  # 直接传递整个字典
            cnx.commit()
        except mysql.connector.Error as err:
            print(f"数据库操作失败: {err}")
        finally:
            cursor.close()
            cnx.close()

    @staticmethod
    def calculate_checksum(data):
        """计算三菱协议校验和（ASCII字符累加和取低16位）"""
        return sum(data[1:]) & 0xFFFF  # 从CMD到ETX求和

    def read_d(self, address, length, ser):
        new_address = int(hex(address * 2), 16) + 0x1000  # 地址转换公式
        print(f'读D寄存器-->转换后的地址：{hex(new_address)}')

        # 要发送的数据 (十六进制格式)
        # send_data = bytes([0x02, 0x30, 0x31, 0x30, 0x46, 0x36, 0x30, 0x34, 0x03, 0x37, 0x34])
        send_data = [0x02, 0x30, *bytes(f"{new_address:04X}", 'ascii'), *bytes(f"{2 * length:02X}", 'ascii'), 0x03]
        checksum = self.calculate_checksum(send_data)
        print(f'读D寄存器-->校验和：{checksum}')
        checksum_str = f"{checksum:04X}"[-2:]
        print(f'读D寄存器-->校验和后两位：{checksum_str}')
        send_data.extend(bytes(checksum_str, 'ascii'))  # SUM

        # 发送数据
        print("读D寄存器-->发送数据:", ' '.join([f"{x:02X}" for x in send_data]))
        ser.write(send_data)  # type: ignore[attr-defined]

        # 等待数据发送完成
        time.sleep(0.2)

        if ser.in_waiting > 0:
            received_data = ser.read(ser.in_waiting)
            print("读D寄存器-->接收到的原始数据:", ' '.join([f"{x:02X}" for x in received_data]))

            try:
                values = self.parse_plc_response(received_data)
                print(f"读D寄存器-->解析结果: {values}")
                return values
            except Exception as e:  # type: ignore[attr-defined]
                print(f"读D寄存器-->解析失败: {str(e)}")
                return []
        else:
            print("读D寄存器-->没有接收到数据")
            return []

    @staticmethod
    def parse_plc_response(response: bytes) -> list:
        """
        解析PLC返回数据包
        输入示例：b'\x02334132CDAB\x03D7'
        返回十进制数值列表，如：[4660, 43981]
        """
        if len(response) < 5:
            raise ValueError("响应数据过短")

        # 校验帧结构
        if response[0] != 0x02 or response[-3] != 0x03:
            raise ValueError("无效的帧头/帧尾")

        # 计算校验和
        calc_checksum = sum(response[1:-2]) & 0xFFFF
        expected_checksum = bytes(f"{calc_checksum:04X}"[-2:], 'ascii')

        if response[-2:] != expected_checksum:
            raise ValueError(f"校验失败: 收到{response[-2:]} vs 计算{expected_checksum}")

        # 提取数据部分（示例：b'334132CDAB'）
        data_part = response[1:-3]

        # 每4个字符解析为一个寄存器值（小端序处理）
        registers = []
        for i in range(0, len(data_part), 8):
            chunk = data_part[i:i + 8].decode('ascii')  # 实际收到的是 "9CFF"

            # 将8字符拆分为两个16位部分处理
            part1 = chunk[4:]  # 高位部分（如："FF9C"）
            part2 = chunk[:4]  # 低位部分（如："3412"）

            # 将ASCII字符转换为原始字节数据（"9CFF" -> b'\x39\x43\x46\x46 这个有问题）
            # 需要先转换为真正的十六进制字节（"9CFF" 实际应该是 "FF9C"）
            # 修正方法：交换前两个和后两个字符
            corrected_chunk = (part1[2:] + part1[:2]) + (part2[2:] + part2[:2])
            byte_data = bytes.fromhex(corrected_chunk)

            # 使用小端序解析（因为PLC实际传输的是高位在前）
            value = struct.unpack('>i', byte_data)[0]  # 使用大端序解析 FF9C 为 -100

            registers.append(value)

        return registers


# 添加PLC数据工作线程类
class PlcDataWorker(QObject):
    """执行PLC数据读取和保存的工作类（在线程中运行）"""
    # 定义信号
    finished = pyqtSignal()  # 完成信号
    data_updated = pyqtSignal(str, dict)  # 数据更新信号：表名和数据字典

    def __init__(self, groups_config, com, serial_port=None):
        """
        构造函数
        参数:
            groups_config: PLC配置参数，包含地址映射和表名
            com: 串口号
            serial_port: 串口对象
        """
        super().__init__()
        self.groups_config = groups_config  # PLC配置参数
        self.com = com  # com口对象
        self.serial_port = serial_port  # 串口对象
        self.keep_running = True  # 控制线程运行的标志
        self.data_manager = plc_data_manager  # 数据管理器实例

    def init_serial(self):
        """初始化串口连接"""
        if not self.serial_port or not self.serial_port.is_open:
            try:
                # 如果没有提供串口对象或串口未打开，则创建新的串口连接
                self.serial_port = serial.Serial(
                    port=self.com,  # 串口号
                    baudrate=9600,  # 波特率
                    bytesize=serial.SEVENBITS,  # 数据位7
                    parity=serial.PARITY_EVEN,  # 偶验位
                    stopbits=serial.STOPBITS_ONE,  # 停止位
                    timeout=1  # 超时时间
                )
                print(f"成功打开串口 {self.com}")
                return True
            except Exception as e:
                print(f"串口{self.com}打开失败: {str(e)}")
                self.serial_port = None
                return False
        return True

    def run(self):
        """线程运行方法，定期读取PLC数据并保存"""
        from time import sleep

        try:
            while self.keep_running:
                try:
                    if not self.init_serial():
                        sleep(1)  # 连接失败则休眠1秒
                        continue  # 跳过本次循环，重新尝试

                    combined_data = {'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

                    for table_name, groups in self.groups_config:
                        for start_addr, reg_count, fields in groups:
                            values = self.data_manager.read_d(start_addr, reg_count, self.serial_port)
                            print(f'values:{values}---reg_count:{reg_count}')
                            # 添加数据有效性检查
                            if len(values) < reg_count / 2:
                                raise ValueError(f"地址{start_addr}读取数据不足，预期{reg_count}个，实际{len(values)}个")

                            # 使用字典推导式映射字段
                            combined_data.update({
                                field: values[i]
                                for i, field in enumerate(fields)
                                if i < len(values)
                            })

                        self.data_manager.save_combined_data(table_name, combined_data)
                        print(f"向{table_name}存储数据成功: {combined_data}")

                    # # 短暂休眠，控制读取频率
                    # sleep(1)

                except serial.SerialException as e:
                    print(f"串口异常: {str(e)}")
                    self.serial_port = None  # 清除串口对象，下次循环重新初始化
                    sleep(1)
                except Exception as e:
                    print(f"运行时异常: {str(e)}")
                    sleep(1)

        finally:
            # 清理资源
            self.cleanup()
            # 发送完成信号
            self.finished.emit()

    def cleanup(self):
        """清理资源"""
        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.close()
                print(f"串口 {self.com} 已关闭")
            except Exception as e:
                print(f"关闭串口时出错: {str(e)}")

    def stop(self):
        """停止线程运行"""
        self.keep_running = False
        print(f"停止 {self.com} 数据采集线程")


plc_data_manager = PlcDataManager()

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        # 初始化UI界面
        self.setupUi(self)
        # 设置窗口全屏显示
        self.setWindowFlags(Qt.FramelessWindowHint)  # 设置无边框窗口样式（隐藏标题栏和边框）
        self.comboBox_1.currentIndexChanged.connect(lambda: self.get_com(self.comboBox_1))
        self.comboBox_2.currentIndexChanged.connect(lambda: self.get_com(self.comboBox_2))
        self.comboBox_3.currentIndexChanged.connect(lambda: self.get_com(self.comboBox_3))
        # self.comboBox_4.currentIndexChanged.connect(lambda: self.get_com(self.comboBox_4)) #预留放卷机
        self.threads = {}
        # 启动三个独立的数据采集线程
        self.start_plc_threads()


    @staticmethod
    def get_com(index):
        try:
            com = index.currentText()
            print(f'当前COM口：{com}')
            return com

        except Exception as e:
            print(f'{e}')

    # 添加启动线程的函数
    def start_plc_threads(self):
        """启动三个PLC数据采集线程"""

        # 工厂2设备4产量数据采集 - 线程1
        thread1 = QThread()
        worker1 = PlcDataWorker(
            groups_config=[(
                "factory2_4_plc0", [
                    (900, 30, ["parameter1", "parameter2", "parameter3", "parameter4", "parameter5",
                               "parameter6", "parameter7", "parameter8", "parameter9", "parameter10",
                               "parameter11", "parameter12", "parameter13", "parameter14", "parameter15"])
                ]
            )],
            com=self.get_com(self.comboBox_1)
        )
        worker1.moveToThread(thread1)
        thread1.started.connect(worker1.run)
        worker1.finished.connect(thread1.quit)
        worker1.finished.connect(worker1.deleteLater)
        thread1.finished.connect(thread1.deleteLater)
        self.threads['thread1'] = (thread1, worker1)
        thread1.start()

        # 工厂2设备4产量数据采集 - 线程2
        thread2 = QThread()
        worker2 = PlcDataWorker(
            groups_config=[(
                "factory2_4_plc1", [
                    (900, 14, ["parameter1", "parameter2", "parameter3", "parameter4", "parameter5",
                               "parameter6", "parameter7"])
                ]
            )],
            com=self.get_com(self.comboBox_2)
        )
        worker2.moveToThread(thread2)
        thread2.started.connect(worker2.run)
        worker2.finished.connect(thread2.quit)
        worker2.finished.connect(worker2.deleteLater)
        thread2.finished.connect(thread2.deleteLater)
        self.threads['thread2'] = (thread2, worker2)
        thread2.start()

        # 工厂2设备4产量数据采集 - 线程3
        thread3 = QThread()
        worker3 = PlcDataWorker(
            groups_config=[(
                "factory2_4_plc2", [
                    (1000, 32, ["parameter1", "parameter2", "parameter3", "parameter4", "parameter5",
                                "parameter6", "parameter7", "parameter8", "parameter9", "parameter10",
                                "parameter11", "parameter12", "parameter13", "parameter14", "parameter15", "parameter16"])
                ]
            )],
            com=self.get_com(self.comboBox_3)
        )
        worker3.moveToThread(thread3)
        thread3.started.connect(worker3.run)
        worker3.finished.connect(thread3.quit)
        worker3.finished.connect(worker3.deleteLater)
        thread3.finished.connect(thread3.deleteLater)
        self.threads['thread3'] = (thread3, worker3)
        thread3.start()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()  # 创建主窗口对象
    mainWindow.show()  # 显示主窗口
    # 进入Qt事件循环
    sys.exit(app.exec_())