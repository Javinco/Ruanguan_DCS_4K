import serial
import time
import struct
import mysql.connector
from datetime import datetime

def calculate_checksum(data):
    """计算三菱协议校验和（ASCII字符累加和取低16位）"""
    return sum(data[1:]) & 0xFFFF  # 从CMD到ETX求和

def read_d(address, length):
    # # 配置串口参数
    # port = 'COM5'
    # baudrate = 9600
    # parity = serial.PARITY_EVEN  # 偶校验
    # bytesize = serial.SEVENBITS  # 数据位7
    # stopbits = serial.STOPBITS_ONE  # 停止位1
    new_address = int(hex(address * 2), 16) + 0x1000  # 地址转换公式
    print(f'读D寄存器-->转换后的地址：{hex(new_address)}')

    # 要发送的数据 (十六进制格式)
    # send_data = bytes([0x02, 0x30, 0x31, 0x30, 0x46, 0x36, 0x30, 0x34, 0x03, 0x37, 0x34])
    send_data = [0x02, 0x30, *bytes(f"{new_address:04X}", 'ascii'), *bytes(f"{2*length:02X}", 'ascii'), 0x03]
    checksum = calculate_checksum(send_data)
    print(f'读D寄存器-->校验和：{checksum}')
    checksum_str = f"{checksum:04X}"[-2:]
    print(f'读D寄存器-->校验和后两位：{checksum_str}')
    send_data.extend(bytes(checksum_str, 'ascii'))   # SUM
    # try:
    #     # # 打开串口
    #     # with serial.Serial(port, baudrate, bytesize=bytesize, parity=parity, stopbits=stopbits, timeout=1) as ser:
    #     #     print(f"已连接到串口 {port}")

    # 发送数据
    print("读D寄存器-->发送数据:", ' '.join([f"{x:02X}" for x in send_data]))
    ser.write(send_data)  # type: ignore[attr-defined]

    # 等待数据发送完成
    time.sleep(0.1)

    if ser.in_waiting > 0:
        received_data = ser.read(ser.in_waiting)
        print("读D寄存器-->接收到的原始数据:", ' '.join([f"{x:02X}" for x in received_data]))

        try:
            values = parse_plc_response(received_data)
            print(f"读D寄存器-->解析结果: {values}")
            return values
        except Exception as e: # type: ignore[attr-defined]
            print(f"读D寄存器-->解析失败: {str(e)}")
            return []
    else:
        print("读D寄存器-->没有接收到数据")
        return []
    #
    # except serial.SerialException as e:
    #     print(f"读D寄存器-->串口错误: {e}")
    # except Exception as e:
    #     print(f"读D寄存器-->发生错误: {e}")

def write_d(address, length, value):
    # # 配置串口参数
    # port = 'COM5'
    # baudrate = 9600
    # parity = serial.PARITY_EVEN  # 偶校验
    # bytesize = serial.SEVENBITS  # 数据位7
    # stopbits = serial.STOPBITS_ONE  # 停止位1
    new_address = int(hex(address * 2), 16) + 0x1000  # 地址转换公式
    print(f'写D寄存器-->转换后的地址：{hex(new_address)}')


    # 要发送的数据 (十六进制格式)
    # send_data = bytes([0x02, 0x30, 0x31, 0x30, 0x46, 0x36, 0x30, 0x34, 0x03, 0x37, 0x34])
    # send_data = [0x02, 0x31, *bytes(f"{new_address:04X}", 'ascii'), *bytes(f"{length:02X}", 'ascii'), *bytes(f"{value_str:04X}", 'ascii'),0x03]
    send_data = [0x02, 0x31, *bytes(f"{new_address:04X}", 'ascii'), *bytes(f"{length:02X}", 'ascii')]
    for _ in value:
        # 1. 将整数转为4位十六进制字符串（不足补零）
        hex_str = f"{_:04X}"  # 如1234转成"04D2"
        print(f'写D寄存器-->4位16进制{hex_str}')
        # 2. 重新排列字符位置 [2][3][0][1]
        # 例如 "04D2" → "D204"
        rearranged = hex_str[2] + hex_str[3] + hex_str[0] + hex_str[1]
        # 3. 将每个字符转为ASCII码值
        # 例如 "D204" → [0x44, 0x32, 0x30, 0x34]
        send_data.extend([ord(c) for c in rearranged])
    send_data.append(0x03)
    checksum = calculate_checksum(send_data)
    print(f'写D寄存器-->校验和：{checksum}')
    checksum_str = f"{checksum:04X}"[-2:]
    print(f'写D寄存器-->校验和后两位：{checksum_str}')
    send_data.extend(bytes(checksum_str, 'ascii'))   # SUM
    # try:
    #     # # 打开串口
    #     # with serial.Serial(port, baudrate, bytesize=bytesize, parity=parity, stopbits=stopbits, timeout=1) as ser:
    #     #     print(f"已连接到串口 {port}")
    # 发送数据
    print("写D寄存器-->发送数据:", ' '.join([f"{x:02X}" for x in send_data]))
    ser.write(send_data)# type: ignore[attr-defined]

    # 等待数据发送完成
    time.sleep(0.1)

    if ser.in_waiting > 0:
        received_data = ser.read(ser.in_waiting)
        print("写D寄存器-->接收到的原始数据:", ' '.join([f"{x:02X}" for x in received_data]))
    else:
        print("写D寄存器-->没有接收到数据")
        return []
    #
    # except serial.SerialException as e:
    #     print(f"串口错误: {e}")
    # except Exception as e:
    #     print(f"发生错误: {e}")

def force(address,status):
    # # 配置串口参数
    # port = 'COM5'
    # baudrate = 9600
    # parity = serial.PARITY_EVEN  # 偶校验
    # bytesize = serial.SEVENBITS  # 数据位7
    # stopbits = serial.STOPBITS_ONE  # 停止位1
    new_address = int(hex(address * 256), 16) + 0x08  # 地址转换公式
    print(f'M寄存器-->转换后的地址：{hex(new_address)}')
    send_data = [0x02]

    if status == 'on':
        # 要发送的数据 (十六进制格式
        # send_data = [0x02, 0x37, *bytes(f"{new_address:04X}", 'ascii'), 0x03]
        send_data.extend([0x37])
    elif status == 'off':
        send_data.extend([0x38])

    send_data.extend(bytes(f"{new_address:04X}", 'ascii'))
    send_data.extend([0x03])
    checksum = calculate_checksum(send_data)
    print(f'M寄存器-->校验和：{checksum}')
    checksum_str = f"{checksum:04X}"[-2:]
    print(f'M寄存器-->校验和后两位：{checksum_str}')
    send_data.extend(bytes(checksum_str, 'ascii'))   # SUM
    # try:
    #     # # 打开串口
    #     # with serial.Serial(port, baudrate, bytesize=bytesize, parity=parity, stopbits=stopbits, timeout=1) as ser:
    #     #     print(f"已连接到串口 {port}")

    # 发送数据
    print("M寄存器-->置位发送数据:", ' '.join([f"{x:02X}" for x in send_data]))
    ser.write(send_data)# type: ignore[attr-defined]

    # 等待数据发送完成
    time.sleep(0.1)

    if ser.in_waiting > 0:
        received_data = ser.read(ser.in_waiting)
        print("M寄存器-->接收到的原始数据:", ' '.join([f"{x:02X}" for x in received_data]))
    else:
        print("M寄存器-->没有接收到数据")
        return []
    # except serial.SerialException as e:
    #     print(f"串口错误: {e}")
    # except Exception as e:
    #     print(f"发生错误: {e}")
def read_float(address, length):
    # # 配置串口参数
    # port = 'COM5'
    # baudrate = 9600
    # parity = serial.PARITY_EVEN  # 偶校验
    # bytesize = serial.SEVENBITS  # 数据位7
    # stopbits = serial.STOPBITS_ONE  # 停止位1
    new_address = int(hex(address * 2), 16) + 0x1000  # 地址转换公式
    print(f'读D寄存器浮点数-->转换后的地址：{hex(new_address)}')

    # 要发送的数据 (十六进制格式)
    # send_data = bytes([0x02, 0x30, 0x31, 0x30, 0x46, 0x36, 0x30, 0x34, 0x03, 0x37, 0x34])
    send_data = [0x02, 0x30, *bytes(f"{new_address:04X}", 'ascii'), *bytes(f"{2*length:02X}", 'ascii'), 0x03]
    checksum = calculate_checksum(send_data)
    print(f'读D寄存器浮点数-->校验和：{checksum}')
    checksum_str = f"{checksum:04X}"[-2:]
    print(f'读D寄存器浮点数-->校验和后两位：{checksum_str}')
    send_data.extend(bytes(checksum_str, 'ascii'))   # SUM
    # try:
    #     # # 打开串口
    #     # with serial.Serial(port, baudrate, bytesize=bytesize, parity=parity, stopbits=stopbits, timeout=1) as ser:
    #     #     print(f"已连接到串口 {port}")

    # 发送数据
    print("读D寄存器浮点数-->发送数据:", ' '.join([f"{x:02X}" for x in send_data]))
    ser.write(send_data)# type: ignore[attr-defined]

    # 等待数据发送完成
    time.sleep(0.1)

    if ser.in_waiting > 0:
        received_data = ser.read(ser.in_waiting)
        print("读D寄存器浮点数-->接收到的原始数据:", ' '.join([f"{x:02X}" for x in received_data]))
        try:
            # 解析响应数据（每个浮点数占4字节）
            values = []
            parsed = parse_plc_response(received_data)  # 获取寄存器值列表

            # 将每个寄存器的两个字节转换为字节数据（小端字序）
            byte_data = bytearray()
            for val in parsed:
                byte_data.extend(val.to_bytes(2, byteorder='little'))  # 保持小端字序

            # 调整字节顺序：将前两个字节和后两个字节交换位置
            # 示例 [F6,C2,66,E6] → [C2,F6,E6,66]
            ordered_data = bytearray()
            for i in range(0, len(byte_data), 4):
                chunk = byte_data[i:i+4]
                if len(chunk) == 4:
                    # 交换前两个和后两个字节
                    ordered_data.extend(chunk[2:4])
                    ordered_data.extend(chunk[0:2])

            # 按大端序解析调整后的字节
            for i in range(0, len(ordered_data), 4):
                chunk = ordered_data[i:i+4]
                if len(chunk) == 4:
                    float_value = struct.unpack('>f', chunk)[0]
                    values.append(round(float_value, 4))
            print(f"读D寄存器浮点数-->解析成功: {values}")
            return values
        except Exception as e:
            print(f"读D寄存器浮点数-->解析失败: {str(e)}")
            return []
    else:
        print("读D寄存器浮点数-->没有接收到数据")
        return []

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

    def save_realtime_data(self, data_dict):
        query = """INSERT INTO factory2_4_realtime_data_jcj 
                   (timestamp, parameter3, parameter4)
                   VALUES (%(timestamp)s, %(param3)s, %(param4)s)
                   ON DUPLICATE KEY UPDATE 
                   parameter3=VALUES(parameter3), 
                   parameter4=VALUES(parameter4)
                   # parameter3=VALUES(parameter3),
                   # parameter4=VALUES(parameter4)"""

        try:
            cnx = self.cnxpool.get_connection()
            cursor = cnx.cursor()
            cursor.execute(query, data_dict)
            cnx.commit()
        except mysql.connector.Error as err:
            print(f"数据库操作失败: {err}")
        finally:
            cursor.close()# type: ignore[attr-defined]
            cnx.close()# type: ignore[attr-defined]

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


if __name__ == "__main__":
    port = 'COM5'
    baudrate = 9600
    parity = serial.PARITY_EVEN  # 偶校验
    bytesize = serial.SEVENBITS  # 数据位7
    stopbits = serial.STOPBITS_ONE  # 停止位1
    # 初始化连接池
    data_manager = PlcDataManager()
    try:
        # 打开串口
        with serial.Serial(port, baudrate, bytesize=bytesize, parity=parity, stopbits=stopbits, timeout=1) as ser:
            print(f"已连接到串口 {port}")
            while True:
                # # read_d(0,2)
                # # read_d(16,2)
                # # 读取两组数据
                # data1 = read_d(100, 4)  # 读取D100-D11
                # # data2 = read_d(16, 2)  # 读取D16-D17
                # if len(data1) >= 2:
                #     # 构建数据字典
                #     current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                #     save_data = {
                #         'timestamp': current_time,
                #         'param3': data1[0],
                #         'param4': data1[1]
                #         # 'param3': data2[0],
                #         # 'param4': data2[1]
                #     }
                #
                #     # 存储到数据库
                #     data_manager.save_realtime_data(save_data)
                #     print("数据存储成功")
                # else:
                #     print("读取数据不完整，存储取消")
                # # write_d(123,6,[4,6,8])
                # # force(4,'off')
                # # read_float(10, 2)
                # 定义采集组配置
                groups_config = [("factory2_4_realtime_data_jcj", [
                                    (4, 4, ["parameter1", "parameter2"]),
                                    (20, 12, ["parameter3", "parameter4", "parameter5", "parameter6", "parameter7", "parameter8"]),
                                    (124, 2, ["parameter9"]),
                                    (0, 2, ["parameter10"]),
                                    (2, 2, ["parameter11"])
                                    ])
                                 ]

                combined_data = {'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

                try:
                    for table_name, groups in groups_config:
                        for start_addr, reg_count, fields in groups:
                            values = read_d(start_addr, reg_count)
                            print(f'values:{values}---reg_count:{reg_count}')
                            # 添加数据有效性检查
                            if len(values) < reg_count/2:
                                raise ValueError(f"地址{start_addr}读取数据不足，预期{reg_count}个，实际{len(values)}个")

                            # 使用字典推导式映射字段
                            combined_data.update({
                                field: values[i]
                                for i, field in enumerate(fields)
                                if i < len(values)
                            })

                        data_manager.save_combined_data(table_name, combined_data)
                        print(f"向{table_name}存储数据成功: {combined_data}")

                except Exception as e:
                    print(f"数据采集异常: {str(e)}")
                    # 可选：记录失败数据到日志文件
    except serial.SerialException as e:
        print(f"串口错误: {e}")
    except Exception as e:
        print(f"发生错误: {e}")