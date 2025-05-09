# import serial
# import time
# from typing import List, Union
#
#
# class MelsecFXCommunication:
#     def __init__(self, port: str, baudrate: int = 9600, parity: str = 'E',
#                  stopbits: int = 1, bytesize: int = 7, station: int = 0xFF):
#         """
#         初始化FX PLC通信
#         :param port: 串口号(如COM3)
#         :param baudrate: 波特率(默认9600)
#         :param parity: 校验位(N-无校验, E-偶校验, O-奇校验)
#         :param stopbits: 停止位(1或2)
#         :param bytesize: 数据位(7或8)
#         :param station: PLC站号(默认0xFF)
#         """
#         self.serial = serial.Serial(
#             port=port,
#             baudrate=baudrate,
#             parity=parity,
#             stopbits=stopbits,
#             bytesize=bytesize,
#             timeout=1
#         )
#         self.station = station
#         self._parity_map = {'N': serial.PARITY_NONE, 'E': serial.PARITY_EVEN, 'O': serial.PARITY_ODD}
#
#     def open(self) -> bool:
#         """打开串口连接"""
#         try:
#             if not self.serial.is_open:
#                 self.serial.open()
#             return True
#         except Exception:
#             return False
#
#     def close(self):
#         """关闭连接"""
#         if self.serial and self.serial.is_open:
#             self.serial.close()
#
#     def _calculate_lrc(self, data: bytes) -> int:
#         """计算LRC校验码(异或校验)"""
#         lrc = 0
#         for byte in data:
#             lrc ^= byte
#         return lrc
#
#     def _convert_address(self, address: str) -> int:
#         """
#         将PLC地址转换为协议地址
#         :param address: 如 "X0", "Y10", "M100", "D200"
#         :return: 协议内部地址
#         """
#         prefix = address[0].upper()
#         num = int(address[1:])
#
#         if prefix == 'X':  # 输入继电器
#             return 0x0080 + num
#         elif prefix == 'Y':  # 输出继电器
#             return 0x00A0 + num
#         elif prefix == 'M':  # 辅助继电器
#             return 0x0100 + num
#         elif prefix == 'D':  # 数据寄存器
#             return num
#         else:
#             raise ValueError(f"不支持的地址类型: {prefix}")
#
#     def _build_command(self, address: str, length: int, is_bit: bool) -> bytes:
#         """
#         构建读命令帧
#         :param address: PLC地址(如 "X0")
#         :param length: 读取长度
#         :param is_bit: 是否为位操作
#         :return: 命令字节流
#         """
#         cmd = bytearray()
#         cmd.append(0x02)  # STX
#         cmd.append(self.station)
#         cmd.append(0x30 if is_bit else 0x44)  # 位/字操作码
#         cmd.append(0x34)  # 读指令
#
#         # 地址转换
#         addr = self._convert_address(address)
#         cmd.extend(addr.to_bytes(2, 'big'))
#
#         # 数据长度
#         cmd.extend(length.to_bytes(2, 'big'))
#
#         # LRC校验(从站号开始到长度结束)
#         cmd.append(self._calculate_lrc(cmd[1:7]))
#         return bytes(cmd)
#
#     def _build_write_command(self, address: str, values: Union[List[bool], List[int]], is_bit: bool) -> bytes:
#         """
#         构建写命令帧
#         :param address: PLC地址(如 "Y0", "M100", "D200")
#         :param values: 要写入的值列表
#         :param is_bit: 是否为位操作
#         :return: 命令字节流
#         """
#         cmd = bytearray()
#         cmd.append(0x02)  # STX
#         cmd.append(self.station)
#         cmd.append(0x31 if is_bit else 0x45)  # 位/字写入操作码
#         cmd.append(0x34)  # 写指令
#
#         # 地址转换
#         addr = self._convert_address(address)
#         cmd.extend(addr.to_bytes(2, 'big'))
#
#         # 数据长度
#         length = len(values)
#         cmd.extend(length.to_bytes(2, 'big'))
#
#         # 数据部分
#         if is_bit:
#             # 位写入，每8位组成一个字节
#             byte_count = (length + 7) // 8
#             data_bytes = bytearray(byte_count)
#             for i, value in enumerate(values):
#                 if value:
#                     data_bytes[i // 8] |= (1 << (i % 8))
#             cmd.extend(data_bytes)
#         else:
#             # 字写入，每个值占2字节
#             for value in values:
#                 cmd.extend(value.to_bytes(2, 'big', signed=True))
#
#         # LRC校验(从站号开始到数据结束)
#         cmd.append(self._calculate_lrc(cmd[1:]))
#         return bytes(cmd)
#
#     def _send_command(self, command: bytes, read_length: int) -> bytes:
#         """
#         发送命令并获取响应
#         :param command: 命令字节流
#         :param read_length: 预期响应长度
#         :return: 响应数据部分
#         """
#         self.serial.reset_input_buffer()
#         self.serial.write(command)
#
#         # 等待响应(根据数据量调整等待时间)
#         time.sleep(max(0.05, read_length * 0.01))
#
#         # 读取响应
#         response = self.serial.read_all()
#
#         # 基本校验
#         if len(response) < 5:
#             raise IOError("响应数据长度不足")
#         if response[0] != 0x02:
#             raise IOError("无效的响应起始字节")
#
#         # 提取数据部分(去掉STX、站号、ETX、LRC)
#         data = response[3:-2]
#
#         # LRC校验
#         received_lrc = response[-1]
#         calculated_lrc = self._calculate_lrc(response[1:-2])
#         if received_lrc != calculated_lrc:
#             raise IOError("LRC校验失败")
#
#         return data
#
#     def read_bits(self, address: str, length: int = 1) -> List[bool]:
#         """
#         读取位元件(X/Y/M)
#         :param address: 起始地址(如 "X0")
#         :param length: 读取位数
#         :return: 位状态列表
#         """
#         if length <= 0 or length > 256:
#             raise ValueError("读取长度必须在1-256之间")
#
#         cmd = self._build_command(address, length, is_bit=True)
#         data = self._send_command(cmd, length // 8 + 3)
#
#         # 将字节转换为位列表
#         bits = []
#         for byte in data:
#             for i in range(8):
#                 bits.append(bool(byte & (1 << i)))
#                 if len(bits) >= length:
#                     break
#         return bits[:length]
#
#     def read_words(self, address: str, length: int = 1) -> List[int]:
#         """
#         读取字元件(D)
#         :param address: 起始地址(如 "D100")
#         :param length: 读取字数
#         :return: 字值列表(16位有符号整数)
#         """
#         if length <= 0 or length > 64:
#             raise ValueError("读取长度必须在1-64之间")
#
#         cmd = self._build_command(address, length, is_bit=False)
#         data = self._send_command(cmd, length * 2 + 3)
#
#         # 每2字节转换为一个16位整数
#         words = []
#         for i in range(0, len(data), 2):
#             word_bytes = data[i:i + 2]
#             if len(word_bytes) == 2:
#                 words.append(int.from_bytes(word_bytes, 'big', signed=True))
#         return words[:length]
#
#     def write_bits(self, address: str, values: List[bool]) -> bool:
#         """
#         写入位元件(Y/M)
#         :param address: 起始地址(如 "Y0", "M100")
#         :param values: 要写入的位值列表
#         :return: 是否成功
#         注意: FX系列PLC通常不允许直接写入X输入点
#         """
#         if not values:
#             raise ValueError("写入值列表不能为空")
#         if len(values) > 256:
#             raise ValueError("写入长度必须在1-256之间")
#
#         # 检查地址类型，X点通常不允许写入
#         if address[0].upper() == 'X':
#             raise ValueError("不允许写入X输入点")
#
#         cmd = self._build_write_command(address, values, is_bit=True)
#         try:
#             # 写入命令的响应通常只包含确认信息
#             self._send_command(cmd, 3)
#             return True
#         except Exception as e:
#             print(f"写入位元件失败: {str(e)}")
#             return False
#
#     def write_words(self, address: str, values: List[int]) -> bool:
#         """
#         写入字元件(D)
#         :param address: 起始地址(如 "D100")
#         :param values: 要写入的字值列表(16位有符号整数)
#         :return: 是否成功
#         """
#         if not values:
#             raise ValueError("写入值列表不能为空")
#         if len(values) > 64:
#             raise ValueError("写入长度必须在1-64之间")
#
#         # 检查数值范围
#         for value in values:
#             if value < -32768 or value > 32767:
#                 raise ValueError(f"写入值 {value} 超出16位有符号整数范围")
#
#         cmd = self._build_write_command(address, values, is_bit=False)
#         try:
#             # 写入命令的响应通常只包含确认信息
#             self._send_command(cmd, 3)
#             return True
#         except Exception as e:
#             print(f"写入字元件失败: {str(e)}")
#             return False
#
#
# # 使用示例
# if __name__ == "__main__":
#     plc = MelsecFXCommunication("COM13")
#     try:
#         if plc.open():
#             # 读取X0-X7
#             x_status = plc.read_bits("X0", 8)
#             print(f"X0-X7状态: {x_status}")
#
#             # 读取D100-D101
#             d_values = plc.read_words("D14", 2)
#             print(f"D100-D101值: {d_values}")
#
#             # 写入Y0-Y3
#             plc.write_bits("Y0", [True, False, True, False])
#             print("Y0-Y3写入成功")
#
#             # 写入D200-D201
#             plc.write_words("D200", [1234, 5678])
#             print("D200-D201写入成功")
#
#     except Exception as e:
#         print(f"通信错误: {str(e)}")
#     finally:
#         plc.close()
# import serial
# import time
# from typing import List, Optional, Union
#
#
# class FX3GAReader:
#     def __init__(self, port: str, baudrate: int = 9600, parity: str = 'E',
#                  stopbits: int = 1, bytesize: int = 7, station: int = 0x00):
#         """
#         初始化FX3GA PLC通信
#         :param port: 串口号(如COM3)
#         :param baudrate: 波特率(默认9600)
#         :param parity: 校验位(E-偶校验)
#         :param stopbits: 停止位(1)
#         :param bytesize: 数据位(7)
#         :param station: PLC站号(默认0x00)
#         """
#         self.serial = serial.Serial(
#             port=port,
#             baudrate=baudrate,
#             parity=parity,
#             stopbits=stopbits,
#             bytesize=bytesize,
#             timeout=2
#         )
#         self.station = station
#         self.debug = True
#
#     def open(self) -> bool:
#         """打开串口连接"""
#         try:
#             if not self.serial.is_open:
#                 self.serial.open()
#             return True
#         except Exception as e:
#             print(f"打开串口失败: {str(e)}")
#             return False
#
#     def close(self):
#         """关闭连接"""
#         if self.serial and self.serial.is_open:
#             self.serial.close()
#
#     @staticmethod
#     def _calculate_lrc(data: bytes) -> int:
#         """计算LRC校验码(异或校验)"""
#         lrc = 0
#         for byte in data:
#             lrc ^= byte
#         return lrc
#
#     def _build_read_command_format4(self, address: int, length: int) -> bytes:
#         """
#         构建读取D寄存器的命令帧 (格式4 - 使用0x01命令)
#         :param address: D寄存器地址(如 0表示D0)
#         :param length: 读取长度
#         :return: 命令字节流
#         """
#         cmd = bytearray()
#         cmd.append(0x01)  # ENQ
#         cmd.append(self.station)
#         cmd.append(0x0A)  # 读取命令
#
#         # 地址 - 使用BCD码格式
#         addr_bcd = self._int_to_bcd(address)
#         cmd.extend(addr_bcd)
#
#         # 数据长度 - BCD码
#         length_bcd = self._int_to_bcd(length)
#         cmd.append(length_bcd[1])  # 只使用低位字节
#
#         # 计算校验和
#         sum_value = sum(cmd[1:]) & 0xFF
#         cmd.append(sum_value)
#
#         if self.debug:
#             print(f"发送命令(格式4): {' '.join([f'{b:02X}' for b in cmd])}")
#
#         return bytes(cmd)
#
#     @staticmethod
#     def _int_to_bcd(value: int) -> bytes:
#         """将整数转换为2字节BCD码"""
#         bcd_high = ((value // 1000) % 10) << 4 | ((value // 100) % 10)
#         bcd_low = ((value // 10) % 10) << 4 | (value % 10)
#         return bytes([bcd_high, bcd_low])
#
#     def _send_command_format4(self, command: bytes) -> Optional[bytes]:
#         """
#         发送格式4命令并获取响应
#         :param command: 命令字节流
#         :return: 响应数据部分
#         """
#         self.serial.reset_input_buffer()
#         self.serial.write(command)
#
#         # 等待响应
#         time.sleep(0.3)
#
#         # 读取响应
#         response = self.serial.read_all()
#
#         if self.debug:
#             print(f"收到响应: {' '.join([f'{b:02X}' for b in response]) if response else '无响应'}")
#
#         # 检查响应格式
#         if not response:
#             print("未收到响应")
#             return None
#
#         if response[0] == 0x06:  # ACK
#             # 继续读取数据帧
#             time.sleep(0.2)
#             data_frame = self.serial.read_all()
#
#             if self.debug:
#                 print(f"数据帧: {' '.join([f'{b:02X}' for b in data_frame]) if data_frame else '无数据帧'}")
#
#             if data_frame and data_frame[0] == 0x02:  # STX
#                 # 提取数据部分
#                 data = data_frame[1:-2]  # 去掉STX和校验和
#                 return data
#
#         elif response[0] == 0x15:  # NAK
#             print("命令被拒绝")
#
#         return None
#
#     def read_d_register_format4(self, address: int) -> Optional[int]:
#         """
#         使用格式4读取D寄存器
#         :param address: D寄存器地址
#         :return: 寄存器值或None
#         """
#         print(f"\n尝试读取D{address} (格式4)")
#         try:
#             cmd = self._build_read_command_format4(address, 1)
#             data = self._send_command_format4(cmd)
#
#             if data and len(data) >= 2:
#                 # 解析BCD码数据
#                 value = self._bcd_to_int(data)
#                 print(f"D{address}寄存器值(BCD): {value}")
#                 return value
#             else:
#                 print(f"未收到有效数据")
#                 return None
#
#         except Exception as e:
#             print(f"格式4读取失败: {str(e)}")
#             return None
#
#     def _bcd_to_int(self, bcd_data: bytes) -> int:
#         """将BCD码转换为整数"""
#         result = 0
#         for byte in bcd_data:
#             high = (byte >> 4) & 0x0F
#             low = byte & 0x0F
#             result = result * 100 + high * 10 + low
#         return result
#
#     def try_communication_test(self) -> bool:
#         """
#         尝试发送通信测试命令
#         :return: 是否成功
#         """
#         print("\n尝试通信测试")
#         try:
#             # 构建测试命令
#             cmd = bytearray([0x05, self.station])  # ENQ + 站号
#
#             self.serial.reset_input_buffer()
#             self.serial.write(cmd)
#             time.sleep(0.3)
#
#             response = self.serial.read_all()
#             print(f"测试响应: {' '.join([f'{b:02X}' for b in response]) if response else '无响应'}")
#
#             if response and response[0] == 0x06:  # ACK
#                 print("通信测试成功")
#                 return True
#             else:
#                 print("通信测试失败")
#                 return False
#
#         except Exception as e:
#             print(f"通信测试异常: {str(e)}")
#             return False
#
#     def try_different_stations(self, address: int) -> Optional[int]:
#         """
#         尝试不同站号读取寄存器
#         :param address: 寄存器地址
#         :return: 读取到的值或None
#         """
#         original_station = self.station
#         stations = [0x00, 0xFF, 0x01, 0x02]
#
#         for station in stations:
#             if station == original_station:
#                 continue
#
#             print(f"\n尝试站号: {station:02X}H")
#             self.station = station
#
#             # 先测试通信
#             if self.try_communication_test():
#                 # 尝试读取
#                 value = self.read_d_register_format4(address)
#                 if value is not None:
#                     print(f"使用站号 {station:02X}H 成功读取D{address}: {value}")
#                     return value
#
#         # 恢复原始站号
#         self.station = original_station
#         print(f"恢复原始站号: {original_station:02X}H")
#
#         return None
#
#
# # 主程序
# if __name__ == "__main__":
#     # 请修改为您的实际串口号
#     plc = FX3GAReader("COM13")
#
#     try:
#         if plc.open():
#             print("成功连接到FX3GA PLC")
#
#             # 添加串口参数信息
#             print(f"串口参数: 波特率={plc.serial.baudrate}, 数据位={plc.serial.bytesize}, "
#                   f"校验位={plc.serial.parity}, 停止位={plc.serial.stopbits}")
#
#             # 通信测试
#             plc.try_communication_test()
#
#             # 尝试格式4读取
#             d0_value = plc.read_d_register_format4(0)
#             if d0_value is not None:
#                 print(f"D0寄存器值: {d0_value}")
#             else:
#                 print("尝试不同站号读取D0")
#                 d0_value = plc.try_different_stations(0)
#                 if d0_value is None:
#                     print("无法读取D0寄存器")
#
#             # 读取D2寄存器
#             d2_value = plc.read_d_register_format4(2)
#             if d2_value is not None:
#                 print(f"D2寄存器值: {d2_value}")
#             else:
#                 print("无法读取D2寄存器")
#
#     except Exception as e:
#         print(f"通信错误: {str(e)}")
#     finally:
#         plc.close()
#         print("已关闭PLC连接")
# import serial
# import time
#
#
# def calculate_checksum(data):
#     """计算三菱协议校验和（ASCII字符累加和取低16位）"""
#     return sum(data[1:-1]) & 0xFFFF  # 从CMD到ETX求和
#
#
# def read_plc_register(port, baudrate=9600, timeout=1):
#     """
#     读取D123寄存器（4字节数据）
#     返回：解析后的寄存器值列表（16位整型）
#     """
#     # 1. 构造读取命令帧（D123开始读4字节）
#     address = 123 * 2 + 0x1000  # 地址转换公式
#     cmd_frame = [
#         0x02,  # STX
#         0x30,  # CMD: Read
#         0x31, 0x30,  # GROUP: 10(D区)
#         *bytes(f"{address:04X}", 'ascii'),  # ADDRESS: 10F6
#         0x30, 0x34,  # BYTES: 04(4字节)
#         0x03  # ETX
#     ]
#     checksum = calculate_checksum(cmd_frame)
#     cmd_frame.extend(bytes(f"{checksum:02X}", 'ascii'))  # SUM
#     print(f"发送的数据：{cmd_frame}")
#
#     # 2. 发送命令
#     with serial.Serial(port, baudrate, timeout=timeout) as ser:
#         ser.write(bytes(cmd_frame))
#         time.sleep(0.1)  # 等待响应
#
#         # 3. 接收响应（示例：02 33 34 31 32 43 44 41 42 03 44 37）
#         response = ser.read(ser.in_waiting or 1)
#         if not response.startswith(b'\x02'):
#             raise ValueError("无效的响应起始符")
#
#         # 4. 解析数据（假设返回2个16位寄存器）
#         # 示例数据：33 34 31 32 | 43 44 41 42 → 0x3132, 0x4142
#         data_part = response[1:-3]  # 去掉STX/ETX/SUM
#         registers = []
#         for i in range(0, len(data_part), 4):
#             # 每4字节转为一个16位值（注意小端序）
#             hex_str = data_part[i:i + 4].decode('ascii')
#             registers.append(int(hex_str[2:4] + hex_str[0:2], 16))
#
#         return registers


# # 使用示例
# if __name__ == "__main__":
#     try:
#         values = read_plc_register('COM15')  # 修改为实际串口号
#         print(f"D123: {values[0]} (0x{values[0]:04X})")
#         print(f"D124: {values[1]} (0x{values[1]:04X})")
#     except Exception as e:
#         print(f"通信错误: {e}")

import serial
import time

def calculate_checksum(data):
    """计算三菱协议校验和（ASCII字符累加和取低16位）"""
    return sum(data[1:]) & 0xFFFF  # 从CMD到ETX求和
# def calculate_checksum(data):
#     """计算三菱协议校验和（16进制加法）"""
#     checksum = 0
#     for byte in data[1:-1]:  # 从CMD到ETX求和
#         checksum += byte
#         checksum &= 0xFFFF  # 保持16位
#     return checksum
def send_to_plc(address, length):
    # 配置串口参数
    port = 'COM15'
    baudrate = 9600
    parity = serial.PARITY_EVEN  # 偶校验
    bytesize = serial.SEVENBITS  # 数据位7
    stopbits = serial.STOPBITS_ONE  # 停止位1
    new_address = int(hex(address * 2), 16) + 0x1000  # 地址转换公式
    print(f'转换后的地址：{hex(new_address)}')

    # 要发送的数据 (十六进制格式)
    # send_data = bytes([0x02, 0x30, 0x31, 0x30, 0x46, 0x36, 0x30, 0x34, 0x03, 0x37, 0x34])
    send_data = [0x02, 0x30, *bytes(f"{new_address:04X}", 'ascii'), *bytes(f"{length:02X}", 'ascii'), 0x03]
    checksum = calculate_checksum(send_data)
    print(f'校验和：{checksum}')
    send_data.extend(bytes(f"{checksum:02X}", 'ascii'))  # SUM
    # send_data = send_data.extend(bytes(f"{checksum:02X}", 'ascii'))  # SUM
    # print(f"发送的数据：{send_data}")
    try:
        # 打开串口
        with serial.Serial(port, baudrate, bytesize=bytesize, parity=parity, stopbits=stopbits, timeout=1) as ser:
            print(f"已连接到串口 {port}")

            # 发送数据
            print("发送数据:", ' '.join([f"{x:02X}" for x in send_data]))
            ser.write(send_data)

            # 等待数据发送完成
            time.sleep(0.1)

            # 接收数据
            if ser.in_waiting > 0:
                received_data = ser.read(ser.in_waiting)
                print("接收到的原始数据:", ' '.join([f"{x:02X}" for x in received_data]))
            else:
                print("没有接收到数据")

    except serial.SerialException as e:
        print(f"串口错误: {e}")
    except Exception as e:
        print(f"发生错误: {e}")


if __name__ == "__main__":
    send_to_plc(10,2)
