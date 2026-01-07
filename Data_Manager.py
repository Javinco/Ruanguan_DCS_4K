import threading# Python线程模块（实现多线程安全）
import mysql.connector# 导入MySQL官方连接驱动
# 从驱动中导入错误处理模块
from mysql.connector import Error
# 导入时间处理模块
from datetime import datetime, timedelta
import socket
import struct
from PyQt5.QtCore import QObject, pyqtSignal

# 定义数据插入器类（单例模式实现）
class DataInserter:
    """实时数据插入器（独立维护插入逻辑）
    功能：专门处理实时数据的批量插入操作
    设计考虑：采用mysql-connector连接池实现，与DataManager保持技术栈统一"""
    _instance = None  # 单例实例
    _lock = threading.Lock()  # 添加线程锁

    def __new__(cls, *args, **kwargs):
        """实例创建方法（线程安全单例模式实现）"""
        with cls._lock:   # 获取线程锁（保证多线程环境下单例创建安全）
            # 检查是否已有实例存在
            if cls._instance is None:
                # 调用父类__new__方法创建新实例
                cls._instance = super().__new__(cls)
                # 初始化标记（防止重复初始化）
                cls._instance.__initialized = False
            return cls._instance    # 返回单例实例
    def __init__(self, host='localhost', user='root', password='admin', database='dcs_data'):
        """类初始化构造器
        Args参数:
            host: MySQL服务器地址（默认localhost本地主机）
            user: 数据库用户名（默认root管理员账号）
            password: 数据库访问密码（需按实际环境修改）
            database: 目标数据库名称（默认dcs_data数据控制系统）"""
        # 连接池配置字典（包含所有数据库连接参数）
        self.conn_config = {
            'host': host,  # 数据库服务器IP地址或域名
            'user': user,  # 数据库认证用户名
            'password': password,  # 数据库认证密码（生产环境需加密存储）
            'database': database,  # 默认操作的数据库名称
            'charset': 'utf8mb4',  # 字符集配置（支持4字节UTF-8编码）
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
        self.__initialized = True   # 设置初始化标记
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
            exit(1)

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
                    error_code = response[8]  # 异常码位于第9字节
                    raise ValueError(f"Modbus异常 错误码:{error_code}")

                # 数据区长度验证
                byte_count = response[8]  # 数据部分字节数（位于第9字节）
                if byte_count != reg_count * 2:  # 每个寄存器2字节
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
                        if reg_count % 2 == 0:  # 浮点数类型（4字节）
                            for i in range(0, len(data), 4):  # 每4字节处理
                                if i + 4 > len(data):  # 检查边界
                                    break
                                # 大端字节序解析为浮点数，保留4位小数
                                value = round(struct.unpack('>f', data[i:i + 4])[0], 4)
                                values.append(value)
                        else:  # 整数类型（2字节）
                            for i in range(0, len(data), 2):  # 每2字节处理
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
        'factory1_1_realtime_data_jcj',
        'factory1_1_realtime_data_fjj',
        'factory1_1_realtime_data_zdj',
        'factory1_1_set_data_jcj',
        'factory1_1_set_data_fjj',
        'factory1_1_set_data_zdj',
        'factory1_1_set_data_curve',
        'factory1_1_production_data',  # 新增生产数据表
        'factory1_1_alarm_data',
        'factory1_2_realtime_data_jcj',
        'factory1_2_realtime_data_fjj',
        'factory1_2_realtime_data_zdj',
        'factory1_2_set_data_jcj',
        'factory1_2_set_data_fjj',
        'factory1_2_set_data_zdj',
        'factory1_2_set_data_curve',
        'factory1_2_production_data',  # 新增生产数据表
        'factory1_2_alarm_data',
        'factory1_3_realtime_data_jcj',
        'factory1_3_realtime_data_fjj',
        'factory1_3_realtime_data_zdj',
        'factory1_3_set_data_jcj',
        'factory1_3_set_data_fjj',
        'factory1_3_set_data_zdj',
        'factory1_3_set_data_curve',
        'factory1_3_production_data',  # 新增生产数据表
        'factory1_3_alarm_data',
        'factory1_4_realtime_data_jcj',
        'factory1_4_realtime_data_fjj',
        'factory1_4_realtime_data_zdj',
        'factory1_4_set_data_jcj',
        'factory1_4_set_data_fjj',
        'factory1_4_set_data_zdj',
        'factory1_4_set_data_curve',
        'factory1_4_production_data',  # 新增生产数据表
        'factory1_4_alarm_data',
        'factory2_1_realtime_data_jcj',
        'factory2_1_realtime_data_fjj',
        'factory2_1_realtime_data_zdj',
        'factory2_1_set_data_jcj',
        'factory2_1_set_data_fjj',
        'factory2_1_set_data_zdj',
        'factory2_1_set_data_curve',
        'factory2_1_production_data',  # 新增生产数据表
        'factory2_1_alarm_data',
        'factory2_2_realtime_data_jcj',
        'factory2_2_realtime_data_fjj',
        'factory2_2_realtime_data_zdj',
        'factory2_2_set_data_jcj',
        'factory2_2_set_data_fjj',
        'factory2_2_set_data_zdj',
        'factory2_2_set_data_curve',
        'factory2_2_production_data',  # 新增生产数据表
        'factory2_2_alarm_data',
        'factory2_3_realtime_data_jcj',
        'factory2_3_realtime_data_fjj',
        'factory2_3_realtime_data_zdj',
        'factory2_3_set_data_jcj',
        'factory2_3_set_data_fjj',
        'factory2_3_set_data_zdj',
        'factory2_3_set_data_curve',
        'factory2_3_production_data',  # 新增生产数据表
        'factory2_3_alarm_data',
        # 'factory2_4_realtime_data_jcj',
        # 'factory2_4_realtime_data_fjj',
        # 'factory2_4_realtime_data_zdj',
        # 'factory2_4_set_data_jcj',
        # 'factory2_4_set_data_fjj',
        # 'factory2_4_set_data_zdj',
        # 'factory2_4_set_data_curve',
        # 'factory2_4_production_data',  # 新增生产数据表
        # 'factory2_4_alarm_data',
    ]
    _instance = None  # 单例实例
    _lock = threading.Lock()  # 添加线程锁

    def __new__(cls, *args, **kwargs):
        """实例创建方法（线程安全单例模式实现）"""
        with cls._lock:   # 获取线程锁（保证多线程环境下单例创建安全）
            # 检查是否已有实例存在
            if cls._instance is None:
                # 调用父类__new__方法创建新实例
                cls._instance = super().__new__(cls)
                # 初始化标记（防止重复初始化）
                cls._instance.__initialized = False
            return cls._instance    # 返回单例实例
    # 初始化方法（构造器）
    def __init__(self, host='localhost', user='root', password='admin', database='dcs_data'):
        """数据库管理器
        Args参数说明:
            host: MySQL服务器地址（默认本地）
            user: 数据库用户名（默认root）
            password: 数据库密码（需根据实际修改）
            database: 要连接的数据库名称（默认dcs_data）
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
        self.__initialized = True   # 设置初始化标记
        self._init_pool()  # 调用私有方法初始化连接池

    def get_data_versions(self):
        """获取各表数据版本号（实际查询数据库）"""
        versions = {}
        try:
            # 使用连接池获取连接
            with self.connection_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    # 查询所有监控表的最新ID
                    for table in self.CLASS_TABLES:
                        # 添加表存在性检查
                        cursor.execute(f"SHOW TABLES LIKE '{table}'")
                        if not cursor.fetchone():
                            print(f"警告：数据表 {table} 不存在")
                            continue
                        # 添加字段存在性检查
                        cursor.execute(f"""
                            SELECT COUNT(*)
                            FROM information_schema.columns 
                            WHERE table_name = '{table}' AND column_name = 'id'
                        """)
                        if cursor.fetchone()[0] == 0:
                            print(f"警告：数据表 {table} 缺少id字段")
                            continue

                        # 添加COALESCE处理空值
                        cursor.execute(f"SELECT COALESCE(MAX(id), 0) FROM `{table}`")
                        result = cursor.fetchone()
                        versions[table] = result[0] if result else 0
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
            exit(1)  # 严重错误直接终止程序（无法继续运行）

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

    def __init__(self, host='localhost', user='root', password='admin', database='dcs_data'):
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
            exit(1)  # 严重错误直接退出程序

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

        # 从连接池获取数据库连接
        conn = self.connection_pool.get_connection()
        try:
            # 创建字典游标（结果以字段名为键）
            cursor = conn.cursor(dictionary=True)

            # 验证目标表存在性（防止SQL注入）
            cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
            if not cursor.fetchone():  # 无匹配表时返回空
                print(f"[历史数据123] 数据表 {table_name} 不存在")
                return []

            # 构造参数化SQL查询（BETWEEN时间范围查询）
            query = f"""SELECT * FROM {table_name} 
                      WHERE timestamp BETWEEN %s AND %s 
                      ORDER BY timestamp ASC"""  # 按时间正序排列
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
        # 从连接池获取数据库连接（使用连接池管理避免资源泄漏）
        conn = self.connection_pool.get_connection()
        try:
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

class PLCDataManager(QObject):
    """PLC数据管理器，支持连接状态通知"""
    # 定义连接状态变化信号
    connection_status_changed = pyqtSignal(bool)  # True: 连接可用, False: 连接不可用
    
    # 定义全局表名常量（新增）
    CLASS_TABLES = [
        'factory2_4_realtime_data_jcj',
        'factory2_4_realtime_data_fjj',
        'factory2_4_realtime_data_zdj',
        'factory2_4_set_data_jcj',
        'factory2_4_set_data_fjj',
        'factory2_4_set_data_zdj',
        'factory2_4_set_data_curve',
        'factory2_4_production_data',  # 新增生产数据表
        'factory2_4_alarm_data',
    ]

    # 初始化方法（构造器）
    def __init__(self, host='192.168.10.99', user='root', password='admin', database='dcs_data'):
        """数据库管理器
        Args参数说明:
            host: MySQL服务器地址（默认mini机192.168.10.99）
            user: 数据库用户名（默认root）
            password: 数据库密码（需根据实际修改）
            database: 要连接的数据库名称（默认dcs_data）
        """
        super().__init__()  # 调用QObject的构造函数
        # 创建配置字典存储连接参数
        self.config = {
            'host': host,  # 数据库服务器的主机名或IP地址
            'user': user,  # 登录数据库的用户名凭证
            'password': password,  # 登录数据库的密码凭证
            'database': database,  # 要操作的数据库名称
            'pool_size': 20,  # 连接池中保持的活跃连接数（防止多线程竞争）
            'autocommit': True
        }
        self.host = host
        self.connection_pool = None  # 添加连接池状态标记
        self.connection_available = False  # 添加连接可用性标记
        # self._init_pool()  # 调用私有方法初始化连接池
        self._start_reconnect_thread()  # 启动后台连接线程

    def get_data_versions(self):
        """获取各表数据版本号（实际查询数据库）"""
        # 新增：连接可用性守卫
        if not self.connection_available or not self.connection_pool:
            # print("版本查询跳过：DataManager连接不可用")
            return {}
        versions = {}
        try:
            # 使用连接池获取连接
            with self.connection_pool.get_connection() as conn:
                with conn.cursor() as cursor:
                    # 查询所有监控表的最新ID
                    for table in self.CLASS_TABLES:
                        # 添加表存在性检查
                        cursor.execute(f"SHOW TABLES LIKE '{table}'")
                        if not cursor.fetchone():
                            print(f"警告：数据表 {table} 不存在")
                            continue
                        # 添加字段存在性检查
                        cursor.execute(f"""
                            SELECT COUNT(*)
                            FROM information_schema.columns 
                            WHERE table_name = '{table}' AND column_name = 'id'
                        """)
                        if cursor.fetchone()[0] == 0:
                            print(f"警告：数据表 {table} 缺少id字段")
                            continue

                        # 添加COALESCE处理空值
                        cursor.execute(f"SELECT COALESCE(MAX(id), 0) FROM `{table}`")
                        result = cursor.fetchone()
                        versions[table] = result[0] if result else 0
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
            self.connection_available = True  # 标记连接可用
            print(f"PLCDataManager{self.host}连接池初始化成功")
        except Error as e:
            print(f"PLCDataManager{self.host}连接池初始化失败: {e}")  # 输出错误详细信息
            print(f"将在后台尝试重连mini机{self.host}数据库...")
            self.connection_available = False  # 标记连接不可用
            self.connection_pool = None
            # 启动重连线程，不退出程序
            self._start_reconnect_thread()

    def _start_reconnect_thread(self):
        """启动重连线程"""
        import threading
        import time

        def reconnect_worker():
            retry_count = 0
            max_retries = -1  # -1表示无限重试
            retry_interval = 1  # 重连间隔30秒

            while not self.connection_available and (max_retries == -1 or retry_count < max_retries):
                retry_count += 1
                print(f"PLCDataManager{self.host}第{retry_count}次尝试重连mini机数据库...")

                try:
                    self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                        pool_name=f"dcs_inserter_pool_{id(self)}_{retry_count}",
                        pool_reset_session=True,
                        **self.config
                    )
                    self.connection_available = True
                    print(f"PLCDataManager{self.host}重连成功！")
                    # 发送连接状态变化信号
                    self.connection_status_changed.emit(True)
                    break
                except Error as e:
                    print(f"PLCDataManager{self.host}重连失败: {e}，{retry_interval}秒后重试...")
                    time.sleep(retry_interval)

        # 创建并启动重连线程
        reconnect_thread = threading.Thread(target=reconnect_worker, daemon=True)
        reconnect_thread.start()

    def get_realtime_data(self, table_name):
        """获取实时数据（完全重构）
        Args参数:
            id: int类型，设备唯一标识符（当前版本暂未使用，保留参数位）
        Returns返回:
            dict: 包含最新实时数据的字典，键为字段名（timestamp/parameter1/parameter2）
                  None表示查询失败
        """
        if not self.connection_available or not self.connection_pool:
            print(f"PLCDataManager{self.host}连接不可用，跳过数据查询")
            return None

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

class PLCHistoricalDataManager(QObject):
    """历史数据管理器（采用相同连接池配置）
    功能：独立管理历史数据的数据库连接与查询操作
    设计特点：与DataManager解耦，但保持表结构一致"""
    # 定义连接状态变化信号
    connection_status_changed = pyqtSignal(bool)  # True: 连接可用, False: 连接不可用

    # 复用实时数据表结构定义（保持数据结构一致性）
    CLASS_TABLES = PLCDataManager.CLASS_TABLES  # 从DataManager继承表名常量

    def __init__(self, host='192.168.10.99', user='root', password='admin', database='dcs_data'):
        """构造器初始化（独立配置连接池）
        Args参数：
            host: MySQL服务器地址（默认mini机192.168.10.99）
            user: 数据库用户名（root管理员）
            password: 数据库访问密码
            database: 目标数据库名称"""
        super().__init__()  # 调用QObject的构造函数
        # 连接池配置字典（独立配置项）
        self.config = {
            'host': host,  # MySQL服务器IP/域名
            'user': user,  # 数据库认证用户名
            'password': password,  # 数据库访问密码（需加密存储）
            'database': database,  # 指定操作数据库
            'pool_size': 1,  # 连接池容量（根据历史查询并发量设置）
            'autocommit': True  # 自动提交模式（查询操作无需事务）
        }
        self.host = host
        self.connection_pool = None  # 连接池对象占位符
        self.connection_available = False  # 添加连接可用性标记
        # self._init_pool()  # 立即初始化连接池
        self._start_reconnect_thread()  # 启动后台连接线程

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
            self.connection_available = True  # 标记连接可用
            print(f"PLCHistoricalDataManager{self.host}连接池初始化成功")
        except Error as e:  # 捕获数据库驱动异常
            print(f"PLCHistoricalDataManager{self.host}连接池初始化失败: {e}")  # 输出详细错误信息
            print(f"将在后台尝试重连mini机{self.host}数据库...")
            self.connection_available = False  # 标记连接不可用
            self.connection_pool = None
            # 启动重连线程，不退出程序
            self._start_reconnect_thread()

    def _start_reconnect_thread(self):
        """启动重连线程"""
        import threading
        import time

        def reconnect_worker():
            retry_count = 0
            max_retries = -1  # -1表示无限重试
            retry_interval = 1  # 重连间隔30秒

            while not self.connection_available and (max_retries == -1 or retry_count < max_retries):
                retry_count += 1
                print(f"PLCHistoricalDataManager{self.host}第{retry_count}次尝试重连mini机数据库...")

                try:
                    self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                        pool_name=f"dcs_inserter_pool_{id(self)}_{retry_count}",
                        pool_reset_session=True,
                        **self.config
                    )
                    self.connection_available = True
                    print(f"PLCHistoricalDataManager{self.host}重连成功！")
                    # 发送连接状态变化信号
                    self.connection_status_changed.emit(True)
                    break
                except Error as e:
                    print(f"PLCHistoricalDataManager{self.host}重连失败: {e}，{retry_interval}秒后重试...")
                    time.sleep(retry_interval)

        # 创建并启动重连线程
        reconnect_thread = threading.Thread(target=reconnect_worker, daemon=True)
        reconnect_thread.start()

    def get_historical_data(self, table_name, start_time, end_time):
        """历史数据查询核心方法
        Args参数：
            table_name: 目标数据表名（需存在于CLASS_TABLES）
            start_time: 查询起始时间（格式：'YYYY-MM-DD HH:MM:SS'）
            end_time: 查询结束时间（格式同上）
        Returns返回：
            list[dict]: 查询结果集（字典列表），无数据返回空列表"""

        # 连接池有效性验证（防御性编程）
        # 检查连接是否可用
        if not self.connection_available or not self.connection_pool:
            print(f"PLCHistoricalDataManager{self.host}连接不可用，跳过历史数据查询")
            return []

        # 从连接池获取数据库连接
        conn = self.connection_pool.get_connection()
        try:
            # 创建字典游标（结果以字段名为键）
            cursor = conn.cursor(dictionary=True)

            # 验证目标表存在性（防止SQL注入）
            cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
            if not cursor.fetchone():  # 无匹配表时返回空
                print(f"[历史数据12] 数据表 {table_name} 不存在")
                return []

            # 构造参数化SQL查询（BETWEEN时间范围查询）
            query = f"""SELECT * FROM {table_name} 
                      WHERE timestamp BETWEEN %s AND %s 
                      ORDER BY timestamp ASC"""  # 按时间正序排列
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
        # 从连接池获取数据库连接（使用连接池管理避免资源泄漏）
        conn = self.connection_pool.get_connection()
        try:
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

# # 测试函数
# if __name__ == "__main__":
#     inserter = DataInserter()
#
#     # 测试挤出机数据插入
#     inserter.insert_jcj_realtime_data()

# # 测试数据查询
# manager = DataManager()
# print(manager.get_realtime_data('jcj', 1))
# 模块级单例实例
inserter = DataInserter()
data_manager = DataManager()
historical_data_manager = HistoricalDataManager()


# plc1_data_manager = PLCDataManager(host= '192.168.1.10')
# plc2_data_manager = PLCDataManager(host= '192.168.1.11')
# plc3_data_manager = PLCDataManager(host= '192.168.1.12')
# plc1_historical_data_manager = PLCHistoricalDataManager(host= '192.168.1.10')
# plc2_historical_data_manager = PLCHistoricalDataManager(host= '192.168.1.11')
# plc3_historical_data_manager = PLCHistoricalDataManager(host= '192.168.1.12')