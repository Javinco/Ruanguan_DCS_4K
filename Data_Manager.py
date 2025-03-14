# 导入MySQL官方连接驱动
import mysql.connector
# 从驱动中导入错误处理模块
from mysql.connector import Error
# 导入时间处理模块
from datetime import datetime
import pymysql
from collections import defaultdict
import socket
import struct


class DataInserter:
    """实时数据插入器（独立维护插入逻辑）
    功能：专门处理实时数据的批量插入操作
    设计考虑：采用pymysql库实现，与DataManager的mysql-connector解耦"""

    def __init__(self, host='localhost', user='root', password='admin', database='dcs_data'):
        # 初始化方法（构造器），参数说明：
        # host: MySQL服务器地址（默认值'localhost'本地主机）
        # user: 数据库用户名（默认值'root'管理员账号）
        # password: 数据库访问密码（默认值'admin'需按实际修改）
        # database: 目标数据库名称（默认值'dcs_data'数据控制系统数据库）
        self.conn_config = {  # 连接配置字典
            'host': host,  # 服务器IP地址配置项
            'user': user,  # 用户名配置项
            'password': password,  # 密码配置项（敏感信息需加密处理）
            'database': database,  # 数据库名称配置项
            'charset': 'utf8mb4'  # 字符集配置（支持emoji和特殊字符）
        }
        self.conn = None  # 数据库连接对象初始化（None表示未连接状态）

    def insert_combined_mcgs_data(self,
                                  table_name: str,
                                  groups: list,
                                  ip='192.168.1.10',
                                  port=502,
                                  unit_id=1):
        """组合式MCGS数据采集（支持多地址批量操作）"""
        try:
            import socket
            import struct
            all_params = []
            all_fields = []
            transaction_id = 0x0001  # 初始化事务ID（Modbus协议要求唯一）

            # 建立TCP长连接（增加重连机制）
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                # 设置TCP保活参数（防止连接中断）
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                sock.settimeout(5)  # 延长超时到5秒（工业设备响应较慢）

                try:
                    sock.connect((ip, port))
                except socket.error as e:
                    raise ConnectionError(f"连接失败: {str(e)}，请检查IP/端口配置")

                # 遍历寄存器组（增加组索引跟踪）
                for group_idx, group in enumerate(groups, 1):
                    start_addr, reg_count, fields = group

                    # 参数校验（增加错误上下文）
                    if reg_count % 2 != 0:
                        raise ValueError(f"第{group_idx}组（地址{start_addr}）寄存器数必须为偶数")
                    if len(fields) != reg_count // 2:
                        raise ValueError(f"第{group_idx}组字段数{len(fields)}与寄存器数{reg_count}不匹配")

                    # 构造标准Modbus TCP请求（修正协议格式）
                    modbus_request = struct.pack(
                        '>HHHBBHH',  # 格式说明：
                        transaction_id,  # 事务ID（每个请求递增）
                        0x0000,  # 协议标识符（Modbus TCP固定值）
                        0x0006,  # 后续字节长度（单元ID+功能码+地址+寄存器数=6字节）
                        unit_id,  # 设备单元号
                        0x03,  # 功能码03（读保持寄存器）
                        start_addr,  # 寄存器起始地址
                        reg_count  # 寄存器数量
                    )
                    transaction_id = (transaction_id % 0xFFFF) + 1  # 事务ID循环递增

                    # 发送/接收数据（增加错误处理）
                    try:
                        sock.sendall(modbus_request)  # 使用sendall确保完整发送
                        response = sock.recv(1024)
                    except socket.timeout:
                        raise TimeoutError(f"第{group_idx}组响应超时")
                    except socket.error as e:
                        raise ConnectionError(f"第{group_idx}组网络错误: {str(e)}")

                    # 校验响应完整性（修正响应头校验）
                    if len(response) < 8:
                        raise ValueError(f"第{group_idx}组响应头不完整（长度不足）")

                    # 解析响应头（事务ID | 协议ID | 长度 | 单元ID | 功能码）
                    resp_tid, resp_pid, resp_len, resp_uid, resp_fc = struct.unpack('>HHHBB', response[:8])

                    # 验证协议一致性
                    if resp_tid != transaction_id - 1:
                        raise ValueError(f"第{group_idx}组事务ID不匹配")
                    if resp_uid != unit_id:
                        raise ValueError(f"第{group_idx}组单元ID不匹配")
                    if resp_fc != 0x03:
                        error_code = response[8] if resp_fc & 0x80 else None
                        raise ValueError(f"第{group_idx}组Modbus异常" + (f"，错误码: {error_code}" if error_code else ""))

                    # 解析数据部分（增加字节数校验）
                    byte_count = response[8]
                    if byte_count != reg_count * 2:
                        raise ValueError(f"第{group_idx}组返回字节数{byte_count}与预期{reg_count * 2}不符")

                    # 提取浮点参数（保留原有解析逻辑）
                    group_params = [
                        round(struct.unpack('>f', response[9 + i * 4: 13 + i * 4])[0], 2)
                        for i in range(reg_count // 2)
                    ]
                    all_params.extend(group_params)
                    all_fields.extend(fields)

            # 数据库写入（保持原有逻辑）
            self.conn = pymysql.connect(**self.conn_config)
            with self.conn.cursor() as cursor:
                columns = ",".join(all_fields)
                placeholders = ",".join(["%s"] * (len(all_fields) + 1))
                cursor.execute(f"""
                    INSERT INTO {table_name}
                    (timestamp, {columns})
                    VALUES ({placeholders})
                """, (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), *all_params))
                self.conn.commit()
                print(f"组合插入：成功写入{len(all_fields)}个参数到{table_name}")

        except Exception as e:
            print(f"组合采集失败: {str(e)}")
            if self.conn:
                self.conn.rollback()
        finally:
            if self.conn and self.conn.open:
                self.conn.close()
                self.conn = None

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
        'factory1_1_production_data'  # 新增生产数据表
    ]

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
            'pool_size': 10,  # 连接池中保持的活跃连接数（防止多线程竞争）
            'autocommit': True
        }
        self.connection_pool = None  # MySQL连接池对象初始化（替代原有单一连接）
        self._init_pool()  # 调用私有方法初始化连接池
        self.data_versions = defaultdict(int)

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

    def on_data_inserted(self, table_name):
        """当有新数据插入时调用此方法"""
        self.data_versions[table_name] += 1

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


# # 测试函数
# if __name__ == "__main__":
#     inserter = DataInserter()
#
#     # 测试挤出机数据插入
#     inserter.insert_jcj_realtime_data()

# # 测试数据查询
# manager = DataManager()
# print(manager.get_realtime_data('jcj', 1))
# 添加模块级实例（在测试块外）
inserter = DataInserter()
