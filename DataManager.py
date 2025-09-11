# -*- coding: utf-8 -*-
import threading  # Python线程模块（实现多线程安全）
import mysql.connector  # 导入MySQL官方连接驱动
# 从驱动中导入错误处理模块
from mysql.connector import Error
# 导入时间处理模块
from datetime import datetime, timedelta
import socket
import struct
from asyncua import Client


# 定义数据插入器类（单例模式实现）
class DataInserter:
    """实时数据插入器（独立维护插入逻辑）
    功能：专门处理实时数据的批量插入操作
    设计考虑：采用mysql-connector连接池实现，与DataManager保持技术栈统一"""
    _instance = None  # 单例实例
    _lock = threading.Lock()  # 添加线程锁

    def __new__(cls, *args, **kwargs):
        """实例创建方法（线程安全单例模式实现）"""
        with cls._lock:  # 获取线程锁（保证多线程环境下单例创建安全）
            # 检查是否已有实例存在
            if cls._instance is None:
                # 调用父类__new__方法创建新实例
                cls._instance = super().__new__(cls)
                # 初始化标记（防止重复初始化）
                cls._instance.__initialized = False
            return cls._instance  # 返回单例实例

    def __init__(self, host='localhost', user='root', password='admin', database='digital_mold'):
        """类初始化构造器
        Args参数:
            host: MySQL服务器地址（默认localhost本地主机）
            user: 数据库用户名（默认root管理员账号）
            password: 数据库访问密码（需按实际环境修改）
            database: 目标数据库名称（默认digital_mold数据控制系统）"""
        # 连接池配置字典（包含所有数据库连接参数）
        self.conn_config = {
            'host': host,  # 数据库服务器IP地址或域名
            'user': user,  # 数据库认证用户名
            'password': password,  # 数据库认证密码（生产环境需加密存储）
            'database': database,  # 默认操作的数据库名称
            'charset': 'utf8mb4',  # 字符集配置（支持4字节UTF-8 编码）
            'pool_size': 20,  # 连接池最大连接数（根据并发量调整）
            'autocommit': True  # 自动提交模式（确保实时数据立即持久化）
        }
        # （在Python中，每次实例化对象时，__init__会被调用，
        # 即使__new__返回的是已有的实例。
        # 因此，即使__new__返回了已经存在的实例，__init__仍然会被再次执行，这可能导致重复初始化，破坏单例的正确性。
        # 为了避免这种情况，代码中添加了__initialized标志。
        # 当实例第一次被初始化时，该标志被设置为True，之后每次__init__被调用时，检查该标志，如果已经初始化过，则直接返回，不再执行后续的初始化代码。
        # 这样可以确保单例实例只被初始化一次，避免资源重复分配或其他副作用。）
        # 单例初始化控制（防止重复初始化）
        if self.__initialized:  # 检查是否已经初始化
            return  # 如果已初始化则直接返回
        self.__initialized = True  # 设置初始化标记
        self._init_pool()  # 立即执行连接池初始化（类实例化时自动完成）

    def _init_pool(self):
        """连接池初始化私有方法
        功能：创建MySQL连接池实例
        异常：初始化失败时终止程序执行"""
        try:
            # 使用mysql.connector官方连接池实现
            self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name=f"dcs_inserter_pool_{id(self)}",  # 唯一标识
                pool_reset_session=True,  # 重置会话状态后回收连接
                **self.conn_config  # 解包传递连接配置参数
            )
        except Error as e:
            # 连接池初始化失败处理（严重错误需立即终止）
            print(f"DataInserter连接池初始化失败: {e}")
            # exit(1)
            self.connection_pool = None

    # 在DataInserter类中添加以下方法
    def insert_multiple_tables_data(self, table_groups: list, sock: socket.socket):
        """多表组合采集方法（新增核心方法）
        功能：处理多个表的Modbus数据采集和插入操作
        参数：
            table_groups: 表组列表，格式为[(表名1, [(起始地址1, 寄存器数1, 字段列表1), ...]), ...]
            sock: 已建立的socket连接对象
        返回：
            bool: 操作成功返回True，失败返回False
        """
        try:
            # 第一步：合并所有寄存器请求，优化通信效率
            merged_requests = self._merge_register_requests(table_groups)

            # 第二步：通过socket发送合并后的Modbus请求并获取响应
            responses = self._send_merged_requests(merged_requests, sock)

            # 第三步：解析响应数据并插入到对应的数据库表中
            return self._parse_and_insert(responses, table_groups)
        except Exception as e:
            # 捕获所有异常并打印错误信息
            print(f"多表采集失败: {str(e)}")
            return False

    @staticmethod
    def _merge_register_requests(table_groups):
        """合并寄存器请求（通信优化关键）
        功能：将多个表的寄存器请求合并为连续的地址块，减少通信次数
        参数：
            table_groups: 表组列表，格式同上
        返回：
            list: 合并后的寄存器块列表，格式为[(起始地址, 寄存器数量), ...]
        """
        all_registers = []  # 存储所有需要读取的寄存器地址
        # 遍历每个表及其寄存器组配置
        for table_name, groups in table_groups:
            for start_addr, reg_count, _ in groups:
                # 将每个寄存器组的地址范围添加到总列表
                all_registers.extend(range(start_addr, start_addr + reg_count))

        # 如果没有寄存器需要读取，返回空列表
        if not all_registers:
            return []

        # 对寄存器地址进行去重和排序
        sorted_registers = sorted(list(set(all_registers)))
        merged = []  # 存储合并后的连续地址块
        current_start = sorted_registers[0]  # 当前连续块的起始地址
        current_end = current_start  # 当前连续块的结束地址

        # 遍历排序后的寄存器地址，合并连续地址
        for addr in sorted_registers[1:]:
            if addr == current_end + 1:  # 如果地址连续
                current_end = addr  # 扩展当前连续块
            else:  # 如果不连续
                # 保存当前连续块（起始地址, 块长度）
                merged.append((current_start, current_end - current_start + 1))
                current_start = addr  # 开始新的连续块
                current_end = addr
        # 添加最后一个连续块
        merged.append((current_start, current_end - current_start + 1))

        return merged

    @staticmethod
    def _send_merged_requests(merged_blocks, sock):
        """发送合并后的请求（完整修正版）
        功能：发送合并后的Modbus请求并接收响应
        参数：
            merged_blocks: 合并后的寄存器块列表
            sock: 已建立的socket连接
        返回：
            dict: 响应数据字典，键为(起始地址, 寄存器数)，值为响应数据
        """
        responses = {}  # 存储响应数据
        transaction_id = 0x0001  # Modbus事务ID初始值（协议要求单调递增）

        # 遍历每个合并后的寄存器块
        for start_addr, reg_count in merged_blocks:
            try:
                # 构造Modbus TCP请求帧（大端字节序）
                # 格式说明：
                # >: 大端字节序
                # H: 2字节无符号短整型
                # B: 1字节无符号字符
                modbus_request = struct.pack(
                    '>HHHBBHH',
                    transaction_id,  # 事务ID（2字节）
                    0x0000,  # 协议标识符（ModbusTCP固定值）
                    0x0006,  # 剩余字节数（后续数据包长度）
                    0x01,  # 单元ID（设备地址）
                    0x03,  # 功能码（读保持寄存器）
                    start_addr,  # 起始寄存器地址
                    reg_count  # 要读取的寄存器数量
                )

                # 发送请求帧（确保完整发送）
                sock.sendall(modbus_request)
                # 接收响应数据（缓冲区大小1KB）
                response = sock.recv(1024)

                # 响应头验证（Modbus TCP头部固定8字节）
                if len(response) < 8:
                    raise ValueError("响应头长度不足")

                # 解析响应头（大端字节序）
                # 格式：事务ID|协议ID|长度|单元ID|功能码
                resp_tid, resp_pid, resp_len, resp_uid, resp_fc = struct.unpack(
                    '>HHHBB', response[:8]  # 只解析前8字节头部
                )

                # 事务ID校验（响应应与请求匹配）
                if resp_tid != transaction_id:
                    raise ValueError(f"事务ID不匹配 请求:{transaction_id} 响应:{resp_tid}")

                # 错误处理（功能码高位为1表示异常）
                if resp_fc & 0x80:
                    error_code = response[8]  # 异常码位于第 9 字节
                    raise ValueError(f"Modbus异常 错误码:{error_code}")

                # 数据区长度验证
                byte_count = response[8]  # 数据部分字节数（位于第 9 字节）
                if byte_count != reg_count * 2:  # 每个寄存器 2 字节
                    raise ValueError(f"字节数不匹配 预期:{reg_count * 2} 实际:{byte_count}")

                # 提取有效数据部分（从第9字节开始，长度为byte_count）
                data = response[9:9 + byte_count]
                # 存储响应数据，键为(起始地址, 寄存器数)
                responses[(start_addr, reg_count)] = data

                # 更新事务ID（循环递增，防止溢出）
                transaction_id = (transaction_id % 0xFFFF) + 1

            except Exception as e:
                # 记录请求失败信息
                print(f"寄存器{start_addr}-{reg_count}请求失败: {str(e)}")
                responses[(start_addr, reg_count)] = None  # 标记为失败
        return responses

    def _parse_and_insert(self, responses, table_groups):
        """解析响应并插入多表数据（修正数据类型）
        功能：解析Modbus响应数据并插入到对应的数据库表中
        参数：
            responses: 响应数据字典
            table_groups: 表组列表
        返回：
            bool: 操作成功返回True，失败返回False
        """
        # 从连接池获取数据库连接
        with self.connection_pool.get_connection() as conn:
            cursor = conn.cursor()  # 创建数据库游标
            try:
                # 遍历每个表及其寄存器组配置
                for table_name, groups in table_groups:
                    table_data = {'timestamp': datetime.now()}  # 初始化数据字典

                    # 处理每个寄存器组
                    for start_addr, reg_count, fields in groups:
                        data = None  # 存储当前寄存器组的响应数据

                        # 在响应中查找匹配的数据块
                        for (block_start, block_size), block_data in responses.items():
                            # 检查当前寄存器组是否包含在某个响应块中
                            if (block_start <= start_addr and
                                    (block_start + block_size) >= (start_addr + reg_count)):
                                # 计算数据偏移量（字节为单位）
                                offset = (start_addr - block_start) * 2
                                # 提取对应数据段
                                data = block_data[offset: offset + reg_count * 2]
                                break

                        if not data:  # 如果没有找到匹配数据，跳过该组
                            continue

                        values = []  # 存储解析后的数值
                        # 根据寄存器数量判断数据类型
                        if reg_count % 2 == 0:  # 浮点数类型（4 字节）
                            for i in range(0, len(data), 4):  # 每4 字节处理
                                if i + 4 > len(data):  # 检查边界
                                    break
                                # # 大端字节序解析为浮点数，保留4位小数
                                # value = round(struct.unpack('>f', data[i:i + 4])[0], 4)
                                # values.append(value)
                                # 提取高16位和低16位
                                # 提取D0（整数部分）和D1（小数部分）
                                integer_part = struct.unpack('>H', data[i:i+2])[0]  # D0
                                decimal_part = struct.unpack('>H', data[i+2:i+4])[0]   # D1
                                # 组合成带小数的值
                                value = float(integer_part) + float(decimal_part) / 10
                                values.append(value)
                        else:  # 整数类型（2 字节）
                            for i in range(0, len(data), 2):  # 每2 字节处理
                                if i + 2 > len(data):  # 检查边界
                                    break
                                # 大端字节序解析为无符号短整型
                                value = struct.unpack('>H', data[i:i + 2])[0]
                                values.append(value)

                        # 将数值映射到字段
                        if len(values) >= len(fields):  # 检查数据与字段数量匹配
                            for i, field in enumerate(fields):
                                table_data[field] = values[i]  # 添加到数据字典

                    # 执行数据库插入（确保有有效数据）
                    if table_data and len(table_data) > 1:  # 排除仅有timestamp的情况
                        try:
                            # 动态构造SQL语句
                            columns = ', '.join(table_data.keys())  # 列名
                            placeholders = ', '.join(['%s'] * len(table_data))  # 占位符
                            sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                            # 执行参数化查询（防止SQL注入）
                            cursor.execute(sql, list(table_data.values()))
                        except Exception as e:
                            print(f"表{table_name}插入失败: {str(e)}")
                            continue

                conn.commit()  # 提交事务
                return True
            except Exception as e:
                conn.rollback()  # 回滚事务
                print(f"数据库事务失败: {str(e)}")
                return False
            finally:
                cursor.close()  # 确保关闭游标


class DataManager:
    # 定义全局表名常量（新增）
    CLASS_TABLES = [
        "factory1_1_main_curve",
        "factory1_1_realtime_plc1",
        "factory1_1_realtime_zsj",
        "factory1_1_set_zsj"
    ]
    _instance = None  # 单例实例
    _lock = threading.Lock()  # 添加线程锁

    def __new__(cls, *args, **kwargs):
        """实例创建方法（线程安全单例模式实现）"""
        with cls._lock:  # 获取线程锁（保证多线程环境下单例创建安全）
            # 检查是否已有实例存在
            if cls._instance is None:
                # 调用父类__new__方法创建新实例
                cls._instance = super().__new__(cls)
                # 初始化标记（防止重复初始化）
                cls._instance.__initialized = False
            return cls._instance  # 返回单例实例

    # 初始化方法（构造器）
    def __init__(self, host='localhost', user='root', password='admin', database='digital_mold'):
        """数据库管理器
        Args参数说明:
            host: MySQL服务器地址（默认本地）
            user: 数据库用户名（默认root）
            password: 数据库密码（需根据实际修改）
            database: 要连接的数据库名称（默认digital_mold）
        """
        # 创建配置字典存储连接参数
        self.config = {
            'host': host,  # 数据库服务器的主机名或IP地址
            'user': user,  # 登录数据库的用户名凭证
            'password': password,  # 登录数据库的密码凭证
            'database': database,  # 要操作的数据库名称
            'pool_size': 20,  # 连接池中保持的活跃连接数（防止多线程竞争）
            'autocommit': True
        }
        # 单例初始化控制（防止重复初始化）
        if self.__initialized:  # 检查是否已经初始化
            return  # 如果已初始化则直接返回
        self.__initialized = True  # 设置初始化标记
        self._init_pool()  # 调用私有方法初始化连接池

    def get_data_versions(self):
        """获取各表数据版本号（实际查询数据库）"""
        versions = {}
        try:
            with self.connection_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    # 首先检查所有表的存在性
                    existing_tables = []
                    for table in self.CLASS_TABLES:
                        # 检查表是否存在
                        cursor.execute(f"SHOW TABLES LIKE '{table}'")
                        if cursor.fetchone():
                            # 检查id字段是否存在
                            cursor.execute(f"""
                                SELECT COUNT(*)
                                FROM information_schema.columns 
                                WHERE table_name = '{table}' AND column_name = 'id'
                            """)
                            if cursor.fetchone()[0] > 0:
                                existing_tables.append(table)
                            else:
                                print(f"警告：数据表 {table} 缺少id字段")
                        else:
                            print(f"警告：数据表 {table} 不存在")

                    # 对存在的表进行优化查询
                    if existing_tables:
                        union_queries = []
                        for table in existing_tables:
                            union_queries.append(f"SELECT '{table}' as table_name, COALESCE(MAX(id), 0) as max_id FROM `{table}`")

                        combined_query = " UNION ALL ".join(union_queries)
                        cursor.execute(combined_query)
                        results = cursor.fetchall()

                        for table_name, max_id in results:
                            versions[table_name] = max_id

                    # 为不存在的表设置默认值
                    for table in self.CLASS_TABLES:
                        if table not in versions:
                            versions[table] = 0

        except Exception as e:
            print(f"版本查询失败: {str(e)}")
            # 返回空字典避免后续错误
            return {}
        return versions

    def _init_pool(self):
        """初始化连接池（解决多线程访问问题）"""
        try:
            # 使用mysql.connector的连接池功能创建连接池
            self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name=f"dcs_inserter_pool_{id(self)}",  # 连接池的名称标识
                pool_reset_session=True,  # 重置会话状态后返回连接池
                **self.config  # 解包连接配置参数
            )
        except Error as e:
            print(f"连接池初始化失败: {e}")  # 输出错误详细信息
            # exit(1)  # 严重错误直接终止程序（无法继续运行）
            self.connection_pool = None

    def get_realtime_data(self, table_name):
        """获取实时数据（完全重构）
        Args参数:
            id: int类型，设备唯一标识符（当前版本暂未使用，保留参数位）
        Returns返回:
            dict: 包含最新实时数据的字典，键为字段名（timestamp/parameter1/parameter2）
                  None表示查询失败
        """
        try:  # try关键字：异常处理开始，捕获代码块中可能发生的异常
            # with语句：上下文管理器，自动管理连接对象的关闭操作
            # self.connection_pool.get_connection()：从连接池获取一个数据库连接
            with self.connection_pool.get_connection() as connection:  # connection变量：数据库连接对象实例

                # dictionary=True参数：使游标返回字典类型的结果（键为字段名）
                with connection.cursor(dictionary=True) as cursor:  # cursor变量：数据库游标对象，用于执行SQL语句

                    # f-string：Python格式化字符串语法，动态插入表名参数
                    # 三引号字符串：定义跨行SQL语句（保留原有缩进格式）
                    cursor.execute(f"""     # execute()方法：执行SQL查询语句
                        SELECT *            # SQL关键字：选择所有字段
                        FROM {table_name}   # SQL关键字：指定查询的表名（通过参数动态传入）
                        ORDER BY id DESC    # SQL子句：按id字段降序排列（DESC表示降序）
                        LIMIT 1             # SQL子句：限制返回1条记录
                    """)  # 分号：SQL语句结束符（Python中可省略）

                    result = cursor.fetchone()  # fetchone()方法：获取查询结果的第一行数据

                    if result:  # if条件判断：检查结果是否非空
                        # isoformat()方法：将datetime对象转换为ISO 8601格式字符串
                        result['timestamp'] = result['timestamp'].isoformat()  # 赋值操作：更新timestamp字段格式

                    return result  # return关键字：返回查询结果字典（无数据时返回None）

        except Error as e:  # except关键字：捕获mysql.connector.Error类型的异常
            # f-string格式化：将错误对象转换为字符串嵌入输出信息
            print(f"数据库操作失败: {e}")  # print函数：输出错误信息到控制台
            return None  # 返回空值：表示查询操作失败


class HistoricalDataManager:
    """历史数据管理器（采用相同连接池配置）
    功能：独立管理历史数据的数据库连接与查询操作
    设计特点：与DataManager解耦，但保持表结构一致"""

    # 复用实时数据表结构定义（保持数据结构一致性）
    CLASS_TABLES = DataManager.CLASS_TABLES  # 从DataManager继承表名常量

    def __init__(self, host='localhost', user='root', password='admin', database='digital_mold'):
        """构造器初始化（独立配置连接池）
        Args参数：
            host: 数据库服务器地址（默认本地）
            user: 数据库用户名（root管理员）
            password: 数据库访问密码
            database: 目标数据库名称"""
        # 连接池配置字典（独立配置项）
        self.config = {
            'host': host,  # MySQL服务器IP/域名
            'user': user,  # 数据库认证用户名
            'password': password,  # 数据库访问密码（需加密存储）
            'database': database,  # 指定操作数据库
            'pool_size': 1,  # 连接池容量（根据历史查询并发量设置）
            'autocommit': True  # 自动提交模式（查询操作无需事务）
        }
        self.connection_pool = None  # 连接池对象占位符
        self._init_pool()  # 立即初始化连接池

    def _init_pool(self):
        """私有方法：初始化MySQL连接池
        异常处理：连接失败时终止程序"""
        try:
            # 创建独立命名的连接池（避免与实时数据池冲突）
            self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name=f"dcs_inserter_pool_{id(self)}",  # 连接池唯一标识
                pool_reset_session=True,  # 重置会话状态后回收连接
                **self.config  # 解包连接配置参数
            )
        except Error as e:  # 捕获数据库驱动异常
            print(f"历史数据连接池初始化失败: {e}")  # 输出详细错误信息
            # exit(1)  # 严重错误直接退出程序
            self.connection_pool = None

    def get_historical_data(self, table_name, start_time, end_time):
        """历史数据查询核心方法
        Args参数：
            table_name: 目标数据表名（需存在于CLASS_TABLES）
            start_time: 查询起始时间（格式：'YYYY-MM-DD HH:MM:SS'）
            end_time: 查询结束时间（格式同上）
        Returns返回：
            list[dict]: 查询结果集（字典列表），无数据返回空列表"""

        # 连接池有效性验证（防御性编程）
        if not self.connection_pool:
            raise ConnectionError("连接池未正确初始化")

        conn = None
        try:
            # 从连接池获取数据库连接
            conn = self.connection_pool.get_connection()
            # 创建字典游标（结果以字段名为键）
            cursor = conn.cursor(dictionary=True)

            # 验证目标表存在性（防止SQL注入）
            cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
            if not cursor.fetchone():  # 无匹配表时返回空
                print(f"[历史数据] 数据表 {table_name} 不存在")
                return []

            # 构造参数化SQL查询（BETWEEN时间范围查询）
            query = f"""SELECT * FROM {table_name}      
                      WHERE timestamp BETWEEN %s AND %s 
                      ORDER BY timestamp"""  # 按时间正序排列  ORDER BY timestamp ASC
            cursor.execute(query, (start_time, end_time))

            # 获取全部结果（无数据时返回空列表）
            return cursor.fetchall() or []  # or []确保返回列表类型

        except Error as e:  # 捕获数据库操作异常
            print(f"[历史数据] 查询失败: {e}")
            return []  # 异常时返回空列表保证程序健壮性
        finally:  # 资源清理块（确保连接回收）
            if conn.is_connected():  # 检查连接状态
                conn.close()  # 归还连接到连接池

    # 在Data_Manager.py的HistoricalDataManager类中修改
    def get_nearest_data(self, table_name, target_time, start_time=None, end_time=None):
        """
        增强版最近数据查询（支持时间范围）
        :param table_name: 目标数据表名（需存在于CLASS_TABLES白名单）
        :param target_time: 目标查询时间（datetime对象）
        :param start_time: 可选时间范围起始（datetime对象）
        :param end_time: 可选时间范围结束（datetime对象）
        :return: 字典格式的单条数据记录 | None表示查询失败
        """
        
        conn = None
        try:
            # 从连接池获取数据库连接
            conn = self.connection_pool.get_connection()
            # 创建字典游标（查询结果以字段名为键）
            with conn.cursor(dictionary=True) as cursor:
                # 表名白名单验证（防御SQL注入攻击）
                if table_name not in self.CLASS_TABLES:
                    return None

                # 动态构建WHERE条件（支持时间范围筛选）
                where_clause = "WHERE 1=1"  # 基础真值条件（便于后续AND拼接）
                params = []  # SQL参数列表（保证参数化查询安全）

                # 添加时间范围筛选条件（当参数有效时）
                if start_time and end_time:
                    where_clause += " AND timestamp BETWEEN %s AND %s"
                    params.extend([start_time, end_time])  # 扩展参数列表

                # 构建参数化SQL查询语句
                query = f"""
                    SELECT * 
                    FROM {table_name}
                    {where_clause}
                    ORDER BY 
                        # 按时间差绝对值排序（数值越小越接近目标时间）
                        ABS(TIMESTAMPDIFF(SECOND, %s, timestamp)),
                        # 次排序条件（时间戳倒序，取最新记录）
                        timestamp DESC
                    LIMIT 1  # 仅返回最优解
                """
                params.append(target_time)  # 添加目标时间参数

                # 执行参数化查询（防止SQL注入）
                cursor.execute(query, params)
                # 获取单条结果（无数据返回None）
                return cursor.fetchone()
        except Error as e:
            # 打印错误日志（保留排查线索）
            print(f"最近数据查询失败: {e}")
            return None
        finally:
            # 确保连接归还连接池（避免连接泄漏）
            if conn.is_connected():
                conn.close()

class OPCDataInserter:
    """OPC UA数据插入器（单例模式实现）
    功能：通过OPC UA协议采集数据并批量插入数据库
    设计考虑：使用asyncua库实现OPC UA客户端，保持与DataInserter相同的连接池配置"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.__initialized = False
            return cls._instance

    def __init__(self, opc_server_url='opc.tcp://localhost:49320',
                 db_config=None, username = None , password = None):
        if self.__initialized:
            return

        # OPC UA连接配置
        self.opc_server_url = opc_server_url
        self.opc_namespace = 'ns=2;s='
        self.username = username
        self.password = password

        # 数据库连接配置（默认值与DataInserter保持一致）
        self.db_config = db_config or {
            'host': 'localhost',
            'user': 'root',
            'password': 'admin',
            'database': 'digital_mold',
            'charset': 'utf8mb4',
            'pool_size': 20,
            'autocommit': True
        }
        self.connection_pool = None
        self.opc_client = None

        self.__initialized = True
        self._init_components()

    def _init_components(self):
        """初始化OPC客户端和数据库连接池"""
        try:
            # 初始化OPC UA客户端
            self.opc_client = Client(self.opc_server_url)
            # # 设置会话超时时间为服务器端配置的 60000ms。在 asyncua 库中，客户端在建立连接时会有默认的会话超时时间配置。尽管你没有在代码里显式设定超时时间，但 asyncua 客户端默认会请求一个较长的会话超时时间，像 3600000ms 这种。而服务器端会依据自身的配置对客户端请求的超时时间进行调整，最终返回服务器端所允许的超时时间，在你的情形下就是 60000ms。
            # self.opc_client.set_session_timeout(60000) # 设置服务器端会话超时时间为60000ms

            # 初始化MySQL连接池
            self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name=f"opc_inserter_pool_{id(self)}",
                pool_reset_session=True,
                **self.db_config
            )
        except Exception as e:
            print(f"初始化失败: {e}")
            # exit(1)
            self.connection_pool = None

    async def connect_opc(self):
        """建立OPC UA连接"""
        try:
            if self.username and self.password:
                self.opc_client.set_user(self.username)
                self.opc_client.set_password(self.password)
                # 尝试不同安全策略
                security_policies = [
                    ('http://opcfoundation.org/UA/SecurityPolicy#None', None, None),
                    ('http://opcfoundation.org/UA/SecurityPolicy#Basic128Rsa15', 'path/to/certificate.der', 'path/to/private_key.pem'),
                    ('http://opcfoundation.org/UA/SecurityPolicy#Basic256', 'path/to/certificate.der', 'path/to/private_key.pem')
                ]
                for policy, cert_path, key_path in security_policies:
                    try:
                        if cert_path and key_path:
                            await self.opc_client.connect_and_secure(
                                security_policy=policy,
                                certificate_path=cert_path,
                                private_key_path=key_path
                            )
                        else:
                            await self.opc_client.connect()
                        print(f"使用安全策略 {policy} 连接OPC UA成功")
                        break
                    except Exception as e:
                        print(f"使用安全策略 {policy} 连接失败: {e}")
                        if policy == security_policies[-1][0]:
                            raise
            else:
                await self.opc_client.connect()
                print("使用无安全策略连接OPC UA成功")
        except Exception as e:
            print(f"OPC连接失败: {e}")
            # exit(1)
            self.opc_client = None


    async def insert_multiple_nodes(self, node_groups: list):
        """多节点采集存储方法
        参数：
            node_groups: 节点组列表，格式为[(表名, [('节点路径1', '字段名1'), ...]), ...]
        返回：
            bool: 操作成功返回True，失败返回False
        """
        try:
            # 批量读取节点数据
            data_dict = await self._read_opc_nodes(node_groups)
            print(f'批量读取节点数据data_dict: {data_dict}')

            # 插入数据库
            return self._insert_to_database(data_dict)

        except Exception as e:
            print(f"数据采集存储失败: {str(e)}")
            return False

    async def _read_opc_nodes(self, node_groups):
        """读取OPC节点数据（核心方法）"""
        data_dict = {}
        try:
            # # 手动建立连接
            # await self.opc_client.connect()
            for table_name, nodes in node_groups:
                table_data = {'timestamp': datetime.now()}

                # 构造节点列表
                node_list = [self.opc_client.get_node(f"{self.opc_namespace}{path}")
                             for path, _ in nodes]
                print(f'节点列表node_list: {node_list}')
                # 相当于
                # node_list = []
                # for path, _ in nodes:
                #     node_id = f"{self.opc_namespace}{path}"
                #     node = self.opc_client.get_node(node_id)
                #     node_list.append(node)

                # 批量读取节点值
                values = await self.opc_client.read_values(node_list)
                print(f'节点值values: {values}')

                # 映射数据到字段
                for (path, field_name), value in zip(nodes, values):
                    table_data[field_name] = value

                data_dict[table_name] = table_data

        except Exception as e:
            raise RuntimeError(f"OPC数据读取失败: {str(e)}")

        return data_dict

    def _insert_to_database(self, data_dict):
        """数据库插入操作"""
        with self.connection_pool.get_connection() as conn:
            cursor = conn.cursor()
            try:
                for table_name, table_data in data_dict.items():
                    if not table_data:
                        continue

                    columns = ', '.join(table_data.keys())
                    placeholders = ', '.join(['%s'] * len(table_data))
                    sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

                    cursor.execute(sql, list(table_data.values()))

                conn.commit()
                print(f'向数据库表:{table_name}  插入数据：{table_data}成功')
                return True

            except Error as e:
                conn.rollback()
                print(f"数据库插入失败: {str(e)}")
                return False
            finally:
                cursor.close()


# 使用示例
# # 初始化连接
# await opc_inserter.connect_opc()
#
# # 定义采集组（表名 + (节点路径, 字段名)列表）
# node_groups = [
#     ('factory_opc_data', [
#         ('PLC1.Device1.Temperature', 'temp1'),
#         ('PLC1.Device1.Pressure', 'press1')
#     ])
# ]
#
# # 执行采集存储
# result = await opc_inserter.insert_multiple_nodes(node_groups)


# 单例实例
inserter = DataInserter()
data_manager = DataManager()
historical_data_manager = HistoricalDataManager()
opc_inserter = OPCDataInserter()


if __name__ == '__main__':
    import asyncio

    async def main():
        # 定义测试采集组（表名需要与数据库实际表结构匹配）
        node_groups = [
            ('factory1_1_realtime_plc1', [
                ('PLC1.Device1.D0', 'temperature0'),  # 字段名需与实际表字段对应
                ('PLC1.Device1.D1', 'temperature1'),
                ('PLC1.Device1.D2', 'temperature2'),
                ('PLC1.Device1.D3', 'temperature3'),
                ('PLC1.Device1.D5', 'temperature5'),
                ('PLC1.Device1.D10', 'temperature10')
            ])
        ]
        try:
            # 初始化连接（异步方法需要await）
            await opc_inserter.connect_opc()
            # 执行采集存储（异步方法）
            result = await opc_inserter.insert_multiple_nodes(node_groups)
            print(f"数据插入结果: {'成功' if result else '失败'}")
        except Exception as e:
            print(f"数据插入失败: {str(e)}")
        finally:
            # 断开连接（异步方法）,关闭OPC连接
            await opc_inserter.opc_client.disconnect()

    asyncio.run(main())