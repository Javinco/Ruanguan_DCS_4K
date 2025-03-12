def insert_mcgs_realtime_data(self,
                              table_name: str,  # 目标数据表名称（字符串类型）
                              start_address: int,  # Modbus寄存器起始地址（十进制整数）
                              register_count: int,  # 需要读取的寄存器总数（必须为偶数）
                              field_names: list,  # 字段名称列表（对应浮点参数）
                              ip='192.168.10.30',  # 触摸屏IP地址（默认工业常用地址）
                              port=502,  # Modbus TCP端口（默认502）
                              unit_id=1):  # 设备站号（默认1）
    """增强版MCGS数据采集（支持地址选择和表名指定）
    参数说明：
    table_name: 目标表名（必须与表结构匹配）
    start_address: Modbus起始地址（十进制）
    register_count: 需读取的寄存器总数（必须为偶数）
    field_names: 字段名称列表（对应浮点参数）"""
    try:
        import socket  # 导入socket模块用于TCP通信
        import struct  # 导入struct模块用于二进制数据解析

        # 参数校验
        if register_count % 2 != 0:  # 检查寄存器数量是否为偶数（每个浮点数占2个寄存器）
            raise ValueError("寄存器数量必须为偶数")
        if len(field_names) != register_count // 2:  # 校验字段数量匹配寄存器数量（寄存器数/2=浮点参数数）
            raise ValueError("字段数量与寄存器数量不匹配")

        # 建立TCP连接（使用IPv4地址族和TCP协议）
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:  # AF_INET=IPv4，SOCK_STREAM=TCP
            sock.settimeout(5)  # 设置5秒超时
            sock.connect((ip, port))  # 连接目标设备（IP+端口）

            # 动态构造Modbus请求（大端字节序）
            request = struct.pack('>HHHBBHH',  # >表示大端序，H=2字节无符号短整型，B=1字节无符号字符
                                  0x0001,  # 事务ID（每次请求递增）
                                  0x0000,  # 协议ID（Modbus固定为0）
                                  0x0006,  # 后续字节长度（固定6字节）
                                  unit_id,  # 单元号/站号
                                  0x03,  # 功能码03（读保持寄存器）
                                  start_address,  # 寄存器起始地址（来自参数）
                                  register_count)  # 读取寄存器总数（来自参数）

            sock.send(request)  # 发送Modbus请求帧
            response = sock.recv(1024)  # 接收响应数据（最大1024字节）

            # 数据解析
            if len(response) < 9 + register_count * 2:  # 校验响应数据长度（9字节头+寄存器数×2字节）
                raise ValueError("响应数据长度异常")

            # 提取浮点参数（每个参数占2个寄存器）
            params = [
                # 使用struct解包大端序浮点数（从第9字节开始，每4字节解析一个float）
                round(struct.unpack('>f', response[9 + i * 4:13 + i * 4])[0], 2)  # 保留两位小数
                for i in range(register_count // 2)  # 遍历所有参数（寄存器数/2）
            ]

            # 数据库操作
            self.conn = pymysql.connect(**self.conn_config)  # 创建数据库连接
            with self.conn.cursor() as cursor:  # 获取数据库游标
                # 动态生成插入语句
                columns = ",".join(field_names)  # 拼接字段名称（parameter1,parameter2...）
                placeholders = ",".join(["%s"] * (len(field_names) + 1))  # 生成占位符（%s,%s...）

                # 执行参数化SQL查询
                cursor.execute(f"""
                    INSERT INTO {table_name} 
                    (timestamp, {columns})    # 时间戳字段+动态字段
                    VALUES ({placeholders})   # 对应占位符
                """, (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), *params))  # 参数绑定

                self.conn.commit()  # 提交事务
                # 输出成功信息（f-string格式化字符串）
                print(f"独立插入类：成功插入{columns}数据！")  # 打印插入的字段名称
                print(f"{params}")  # 打印插入的参数值

    except Exception as e:
        print(f"MCGS采集失败: {str(e)}")  # 异常信息输出
        if self.conn:
            self.conn.rollback()  # 事务回滚
    finally:
        if self.conn and self.conn.open:  # 确保连接有效且已打开
            self.conn.close()  # 关闭数据库连接
            self.conn = None  # 重置连接对象