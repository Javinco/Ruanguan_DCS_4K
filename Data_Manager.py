import threading# Python线程模块（实现多线程安全）
from random import randint

import mysql.connector# 导入MySQL官方连接驱动
# 从驱动中导入错误处理模块
from mysql.connector import Error
# 导入时间处理模块
from datetime import datetime, timedelta
import socket
import struct

# 定义数据插入器类（单例模式实现）
class DataInserter:
    """实时数据插入器（独立维护插入逻辑）
    功能：专门处理实时数据的批量插入操作
    设计考虑：采用mysql-connector连接池实现，与DataManager保持技术栈统一"""
    # 单例模式相关变量
    _instance = None  # 存储单例实例的类变量（私有属性）
    _lock = threading.Lock()  # 添加线程锁（保证线程安全的单例创建）
    # 第一次实例化                        # 后续实例化请求
    # ↓                               ↓
    # ┌─────────────┐                 ┌─────────────┐
    # │ 获取线程锁    │                 │ 获取线程锁    │
    # └─────┬───────┘                 └─────┬───────┘
    # ↓                               ↓
    # ┌─────────────┐                 ┌─────────────┐
    # │ 创建新实例    │                 │ 返回现有实例  │
    # └─────┬───────┘                 └─────┬───────┘
    # ↓                               ↓
    # ┌─────────────┐                 ┌─────────────┐
    # │ 执行__init__ │                 │ 跳过__init__ │
    # └─────────────┘                 └─────────────┘
    # 这种双重检查机制是Python单例模式的经典实现，既保证了线程安全，又避免了不必要的资源消耗。
    # 单例模式实现（__new__方法重写）
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
            'pool_size': 15,  # 连接池最大连接数（根据并发量调整）
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
                pool_name="dcs_inserter_pool",  # 连接池唯一标识（避免多池冲突）
                pool_reset_session=True,  # 重置会话状态后回收连接
                **self.conn_config  # 解包传递连接配置参数
            )
        except Error as e:
            # 连接池初始化失败处理（严重错误需立即终止）
            print(f"DataInserter连接池初始化失败: {e}")
            exit(1)

    def insert_combined_mcgs_data(self,
                                  table_name: str,
                                  groups: list,
                                  ip='192.168.1.10',
                                  port=502,
                                  unit_id=1,
                                  sock=None):# 新增sock参数
        """组合式MCGS设备数据采集方法
        Args参数:
            table_name: 目标数据表名称
            groups: 寄存器组配置列表（格式：[起始地址, 寄存器数, 字段列表]）
            ip: 设备IP地址（默认Modbus TCP常用地址）
            port: 设备端口号（默认Modbus 502端口）
            unit_id: 设备单元标识号（默认1号单元）
            sock: 持久化TCP连接（新增参数）
        流程：1.建立TCP连接 2.轮询读取寄存器 3.批量写入数据库
        异常：采集失败时自动回滚事务"""
        try:
            # 初始化数据存储容器
            all_params = []  # 采集参数值缓存列表
            all_fields = []  # 数据库字段名缓存列表
            transaction_id = 0x0001  # Modbus事务ID初始值（协议要求单调递增）

            # 连接有效性验证（新增）
            if not sock:
                raise ValueError("必须提供有效的socket连接")

            # 寄存器组遍历采集（enumerate生成组索引）
            for group_idx, group in enumerate(groups, 1):  # 索引从1开始计数
                start_addr, reg_count, fields = group  # 解包寄存器组配置

                # 输入参数有效性验证
                if reg_count % 2 != 0:  # Modbus浮点数需要2个寄存器
                    raise ValueError(f"第{group_idx}组（地址{start_addr}）寄存器数必须为偶数")
                if len(fields) != reg_count // 2:  # 字段数应与寄存器对数量匹配
                    raise ValueError(f"第{group_idx}组字段数{len(fields)}与寄存器数{reg_count}不匹配")

                # Modbus协议帧构造（大端字节序）
                modbus_request = struct.pack(
                    '>HHHBBHH',  # 格式字符串说明：
                    transaction_id,  # 事务ID（2字节无符号短整型）
                    0x0000,  # 协议标识符（ModbusTCP固定值）
                    0x0006,  # 剩余字节数（后续数据包长度）
                    unit_id,  # 设备单元号（1字节无符号字符）
                    0x03,  # 功能码03（读保持寄存器）
                    start_addr,  # 寄存器起始地址（2字节无符号短整型）
                    reg_count  # 请求读取的寄存器数量（2字节无符号短整型）
                )
                transaction_id = (transaction_id % 0xFFFF) + 1  # 事务ID循环递增（防止溢出）

                # 数据收发处理（带异常捕获）
                try:
                    sock.sendall(modbus_request)  # 完整发送请求帧（避免分包）
                    response = sock.recv(1024)  # 接收响应数据（缓冲区1KB）
                except (socket.timeout, ConnectionResetError) as e:
                    raise ConnectionError(f"第{group_idx}组通信错误: {str(e)}")
                except Exception as e:
                    raise RuntimeError(f"第{group_idx}组网络错误: {str(e)}")

                # 响应基础校验
                if len(response) < 8:  # ModbusTCP头部固定8字节
                    raise ValueError(f"第{group_idx}组响应头不完整（长度不足）")

                # 响应头解析（大端字节序解包）
                resp_tid, resp_pid, resp_len, resp_uid, resp_fc = struct.unpack(
                    '>HHHBB', response[:8]  # 解析前8字节头部
                )

                # 协议一致性验证
                if resp_tid != transaction_id - 1:  # 响应事务ID应匹配请求ID
                    raise ValueError(f"第{group_idx}组事务ID不匹配")
                if resp_uid != unit_id:  # 单元ID必须一致
                    raise ValueError(f"第{group_idx}组单元ID不匹配")
                if resp_fc != 0x03:  # 检查功能码异常
                    error_code = response[8] if resp_fc & 0x80 else None
                    raise ValueError(f"第{group_idx}组Modbus异常" +
                                     (f"，错误码: {error_code}" if error_code else ""))

                # 数据区校验
                byte_count = response[8]  # 数据部分字节数（位于第9字节）
                if byte_count != reg_count * 2:  # 每个寄存器2字节
                    raise ValueError(f"第{group_idx}组返回字节数{byte_count}与预期{reg_count * 2}不符")

                # 浮点数解析（大端字节序）
                group_params = [
                    round(struct.unpack('>f', response[9 + i * 4: 13 + i * 4])[0], 4)
                    for i in range(reg_count // 2)  # 每4字节解析为一个浮点数
                ]
                all_params.extend(group_params)  # 参数值追加到总列表
                all_fields.extend(fields)  # 字段名追加到总列表

            # 数据库写入（使用连接池获取连接）
            with self.connection_pool.get_connection() as conn:  # 从池中获取连接
                with conn.cursor() as cursor:  # 获取数据库游标
                    # SQL语句动态构造
                    columns = ",".join(all_fields)  # 字段列表逗号拼接
                    placeholders = ",".join(["%s"] * (len(all_fields) + 1))  # 占位符生成

                    # 执行参数化SQL（防止SQL注入）
                    cursor.execute(f"""
                        INSERT INTO {table_name}
                        (timestamp, {columns})
                        VALUES ({placeholders})
                    """, (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), *all_params))

                    conn.commit()  # 显式提交事务（确保数据持久化）
                    print(f"组合插入：成功写入{len(all_fields)}个参数到{table_name}")
            return True
        except Exception as e:  # 全局异常捕获
            print(f"组合采集失败: {str(e)}")
            if 'conn' in locals():  # 回滚条件检查（仅当连接已建立）
                conn.rollback()  # 事务回滚（保证数据一致性）
            return False
    def insert_combined_mcgs_int_data(self,
                                  table_name: str,
                                  groups: list,
                                  ip='192.168.1.10',
                                  port=502,
                                  unit_id=1,
                                  sock=None):  # 新增sock参数
        """组合式MCGS设备数据采集方法
        Args参数:
            table_name: 目标数据表名称
            groups: 寄存器组配置列表（格式：[起始地址, 寄存器数, 字段列表]）
            ip: 设备IP地址（默认Modbus TCP常用地址）
            port: 设备端口号（默认Modbus 502端口）
            unit_id: 设备单元标识号（默认1号单元）
            sock: 持久化TCP连接（新增参数）
        流程：1.建立TCP连接 2.轮询读取寄存器 3.批量写入数据库
        异常：采集失败时自动回滚事务"""
        try:
            # 初始化数据存储容器
            all_params = []  # 采集参数值缓存列表
            all_fields = []  # 数据库字段名缓存列表
            transaction_id = 0x0001  # Modbus事务ID初始值（协议要求单调递增）

            # 连接有效性验证（新增）
            if not sock:
                raise ValueError("必须提供有效的socket连接")

            # 寄存器组遍历采集（enumerate生成组索引）
            for group_idx, group in enumerate(groups, 1):  # 索引从1开始计数
                start_addr, reg_count, fields = group  # 解包寄存器组配置

                if len(fields) != reg_count:  # 字段数应与寄存器对数量匹配
                    raise ValueError(f"第{group_idx}组字段数{len(fields)}与寄存器数{reg_count}不匹配")

                # Modbus协议帧构造（大端字节序）
                modbus_request = struct.pack(
                    '>HHHBBHH',  # 格式字符串说明：
                    transaction_id,  # 事务ID（2字节无符号短整型）
                    0x0000,  # 协议标识符（ModbusTCP固定值）
                    0x0006,  # 剩余字节数（后续数据包长度）
                    unit_id,  # 设备单元号（1字节无符号字符）
                    0x03,  # 功能码03（读保持寄存器）
                    start_addr,  # 寄存器起始地址（2字节无符号短整型）
                    reg_count  # 请求读取的寄存器数量（2字节无符号短整型）
                )
                transaction_id = (transaction_id % 0xFFFF) + 1  # 事务ID循环递增（防止溢出）

                # 数据收发处理（带异常捕获）
                try:
                    sock.sendall(modbus_request)  # 完整发送请求帧（避免分包）
                    response = sock.recv(1024)  # 接收响应数据（缓冲区1KB）
                except (socket.timeout, ConnectionResetError) as e:
                    raise ConnectionError(f"第{group_idx}组通信错误: {str(e)}")
                except Exception as e:
                    raise RuntimeError(f"第{group_idx}组网络错误: {str(e)}")

                # 基础响应验证
                if len(response) < 9 + reg_count * 2:
                    raise ValueError("响应数据长度不足")

                # 解析寄存器值（直接读取每个寄存器的16位无符号整数）
                group_params = [
                    struct.unpack('>H', response[9 + i * 2: 11 + i * 2])[0]
                    for i in range(reg_count)
                ]

                all_params.extend(group_params)
                all_fields.extend(fields)

            # 数据库写入（使用连接池获取连接）
            with self.connection_pool.get_connection() as conn:  # 从池中获取连接
                with conn.cursor() as cursor:  # 获取数据库游标
                    # SQL语句动态构造
                    columns = ",".join(all_fields)  # 字段列表逗号拼接
                    placeholders = ",".join(["%s"] * (len(all_fields) + 1))  # 占位符生成

                    # 执行参数化SQL（防止SQL注入）
                    cursor.execute(f"""
                        INSERT INTO {table_name}
                        (timestamp, {columns})
                        VALUES ({placeholders})
                    """, (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), *all_params))

                    conn.commit()  # 显式提交事务（确保数据持久化）
                    print(f"组合插入：成功写入{len(all_fields)}个参数到{table_name}")
            return True
        except Exception as e:  # 全局异常捕获
            print(f"组合采集失败: {str(e)}")
            if 'conn' in locals():  # 回滚条件检查（仅当连接已建立）
                conn.rollback()  # 事务回滚（保证数据一致性）
            return False

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
        'factory2_3_alarm_data'
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
                pool_name="dcs_pool",  # 连接池的名称标识
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
            'pool_size': 10,  # 连接池容量（根据历史查询并发量设置）
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
                pool_name="hist_pool",  # 连接池唯一标识
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
                print(f"[历史数据] 数据表 {table_name} 不存在")
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
