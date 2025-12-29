import sys
import serial
import time
import mysql.connector
from datetime import datetime
# 添加PyQt5相关导入
from PyQt5.QtCore import QObject, pyqtSignal, QThread, Qt
from PyQt5.QtWidgets import QApplication, QComboBox, QWidget, QVBoxLayout, QMainWindow
from Ui_LocalCollectParameter import Ui_MainWindow


class ReadM:
    @staticmethod
    def calculate_checksum(data):
        """计算三菱协议校验和（ASCII字符累加和取低16位）"""
        return sum(data[1:]) & 0xFFFF  # 从CMD到ETX求和

    def read_m(self, address, length, ser):
        # 计算实际要读取的字节数（每个字节对应8个M寄存器）
        byte_count = (length + 7) // 8  # 向上取整
        new_address = int(hex((address - 896) // 8), 16) + 0x170  # 地址转换公式
        print(f'读M寄存器-->转换后的地址：{hex(new_address)}')
        print(f'读M寄存器-->需要读取的字节数：{byte_count}')

        # 构建发送数据
        send_data = [0x02, 0x30, *bytes(f"{new_address:04X}", 'ascii'), *bytes(f"{byte_count:02X}", 'ascii'), 0x03]
        checksum = self.calculate_checksum(send_data)
        checksum_str = f"{checksum:04X}"[-2:]
        send_data.extend(bytes(checksum_str, 'ascii'))  # SUM

        # 发送数据
        print("读M寄存器-->发送数据:", ' '.join([f"{x:02X}" for x in send_data]))
        ser.write(send_data)  # type: ignore[attr-defined]

        # 等待数据发送完成
        time.sleep(0.2)

        if ser.in_waiting > 0:
            received_data = ser.read(ser.in_waiting)
            print("读M寄存器-->接收到的原始数据:", ' '.join([f"{x:02X}" for x in received_data]))

            try:
                # 解析M寄存器状态
                register_states = self.parse_plc_response(received_data, address)
                print(f"读M寄存器-->解析结果: {register_states}")
                return register_states
            except Exception as e:  # type: ignore[attr-defined]
                print(f"读M寄存器-->解析失败: {str(e)}")
                import traceback
                traceback.print_exc()  # 打印详细错误信息
                return []
        else:
            print("读M寄存器-->没有接收到数据")
            return []

    @staticmethod
    def parse_plc_response(response: bytes, start_address: int) -> dict:
        """
        解析PLC返回的M寄存器数据包
        :param response: 接收到的原始数据，格式如 b'\x023231\x0366' 或 b'\x0232393830\x034436'
        :param start_address: 起始M寄存器地址（如M1000）
        :return: M寄存器状态字典，格式如 {M1000: True, M1001: False, ...}
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

        # 提取数据部分（例如：b'3231' 或 b'32393830'）
        data_part = response[1:-3]
        print(f"数据部分(ASCII): {data_part.decode('ascii')}")

        # 将ASCII数据转换为十六进制字节数组
        hex_str = data_part.decode('ascii')
        if len(hex_str) % 2 != 0:
            raise ValueError(f"数据部分长度必须为偶数: {hex_str}")

        # 分割为2个字符一组，转换为十六进制字节
        byte_values = []
        for i in range(0, len(hex_str), 2):
            byte_hex = hex_str[i:i+2]
            byte_value = int(byte_hex, 16)
            byte_values.append(byte_value)
            print(f"字节{i//2+1}: 0x{byte_hex} -> {byte_value} (二进制: {bin(byte_value)[2:].zfill(8)})")

        # 解析每个字节的8个比特位，对应M寄存器的状态
        register_states = {}
        for byte_index, byte_value in enumerate(byte_values):
            for bit_index in range(8):
                # 计算当前M寄存器的地址
                current_address = start_address + byte_index * 8 + bit_index

                # 获取该位的状态（True表示置1，False表示置0）
                # 注意：这里是从最低位开始检查，对应Mxxxx到Mxxxx+7
                bit_state = (byte_value & (1 << bit_index)) != 0
                register_states[f"M{current_address}"] = bit_state

        return register_states


if __name__ == '__main__':
    read_m = ReadM()
    # 示例：读取M1000-M1015（共16个寄存器）
    read_m.read_m(1000, 16, serial.Serial(
        port='com1',  # 串口号
        baudrate=9600,  # 波特率
        bytesize=serial.SEVENBITS,  # 数据位7
        parity=serial.PARITY_EVEN,  # 偶验位
        stopbits=serial.STOPBITS_ONE,  # 停止位
        timeout=1  # 超时时间
    ))