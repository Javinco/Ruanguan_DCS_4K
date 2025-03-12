def insert_combined_mcgs_data(self, table_name: str, groups: list, ip='192.168.1.10', port=502, unit_id=1):
    """组合式MCGS数据采集（最简稳定版）"""
    sock = None
    try:
        # 创建TCP连接
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((ip, port))

        # 核心修复：修正Modbus协议头结构
        for index, group in enumerate(groups):
            start_addr, reg_count, fields = group

            # 构造标准Modbus TCP请求头
            transaction_id = 1 + index
            protocol_id = 0x0000  # 固定协议标识符
            length = 6  # 后续字节数（unit_id + 后续数据长度）
            request = struct.pack('>HHHBBHH',
                                  transaction_id,
                                  protocol_id,  # 原错误参数0x0006改为0x0000
                                  length,
                                  unit_id,
                                  0x03,  # 功能码
                                  start_addr,
                                  reg_count)

            # 发送请求（简化重试逻辑）
            sock.send(request)

            # 接收响应（限制最大长度）
            response = sock.recv(1024)

            # 基础长度验证
            if len(response) < 9:
                continue

        # 数据库写入保持最简
        with self.pool.connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO ...")  # 保持原有简单插入逻辑
            conn.commit()

    except Exception as e:
        print(f"采集失败: {str(e)}")
    finally:
        if 'sock' in locals():
            sock.close()  # 确保socket关闭