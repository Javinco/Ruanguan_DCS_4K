# 导入MySQL官方连接驱动
import mysql.connector
# 从驱动中导入错误处理模块
from mysql.connector import Error
# 导入时间处理模块
from datetime import datetime
import pymysql
import random


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
        # 增加连接池配置
        self.pool = None
        self.create_connection_pool()

    def create_connection_pool(self):
        """创建数据库连接池（解决连接资源冲突）"""
        try:
            self.pool = pymysql.ConnectionPool(
                mincached=1,
                maxcached=5,
                **self.conn_config
            )
        except pymysql.Error as e:
            print(f"连接池创建失败: {str(e)}")

    def insert_realtime_data(self):
        """批量插入方法（保持原有pymysql实现）
        功能流程：
        1. 建立数据库连接
        2. 创建数据表（如果不存在）
        3. 生成并插入100条模拟数据
        4. 处理事务提交/回滚
        5. 确保连接关闭"""
        try:
            # 建立数据库连接（使用pymysql库的connect方法）
            # **操作符将字典解包为关键字参数
            self.conn = pymysql.connect(**self.conn_config)

            # 使用with语句管理游标（自动释放资源）
            with self.conn.cursor() as cursor:  # cursor()创建游标对象
                # 执行建表语句（IF NOT EXISTS保障幂等性）
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS real_timedata (
                        id INT AUTO_INCREMENT PRIMARY KEY,  # 自增主键（从1开始自动增长）
                        timestamp DATETIME NOT NULL,       # 时间戳字段（不允许为空）
                        parameter1 DECIMAL(6,2),            # 数值字段1（共6位，含2位小数）
                        parameter2 DECIMAL(6,2)             # 数值字段2（共6位，含2位小数）
                    )""")  # 使用三重引号定义多行SQL语句

                # 循环插入100条模拟数据（_为占位符，表示不关心循环变量值）
                for _ in range(100):  # range(100)生成0-99的整数序列
                    # 生成当前时间（精确到秒）
                    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    # 构造参数元组（使用round保证小数点后两位）
                    params = (
                        current_time,  # 时间参数（字符串格式）
                        round(random.uniform(0.00, 9999.99), 2),  # 生成0.00-9999.99的随机数
                        round(random.uniform(0.00, 9999.99), 2)  # 第二个参数同理
                    )
                    # 执行参数化查询（使用字符串拼接优化可读性）
                    cursor.execute(
                        "INSERT INTO real_timedata (timestamp, parameter1, parameter2) "
                        "VALUES (%s, %s, %s)", params  # %s是参数占位符（非字符串格式化）使用占位符防止SQL注入，然后传入参数元组
                    )

                # 提交事务（保证100条数据原子性写入）
                self.conn.commit()
                # 输出成功信息（f-string格式化字符串）
                print(f"独立插入类：成功插入{100}条数据！")

        except pymysql.Error as e:  # 捕获pymysql特定异常
            print(f"插入失败: {str(e)}")  # 输出错误信息（转换为字符串）
            if self.conn:  # 检查连接是否有效
                self.conn.rollback()  # 事务回滚（保证数据一致性）
        finally:  # 无论是否异常都会执行
            if self.conn and self.conn.open:  # 检查连接状态
                self.conn.close()  # 关闭连接（释放数据库资源）
                self.conn = None  # 重置连接对象（避免重复关闭）

    def insert_jcj_realtime_data(self):
        """批量插入方法（保持原有pymysql实现）
        功能流程：
        1. 建立数据库连接
        2. 创建数据表（如果不存在）
        3. 生成并插入100条模拟数据
        4. 处理事务提交/回滚
        5. 确保连接关闭"""
        try:
            # 建立数据库连接（使用pymysql库的connect方法）
            # **操作符将字典解包为关键字参数
            self.conn = pymysql.connect(**self.conn_config)

            # 使用with语句管理游标（自动释放资源）
            with self.conn.cursor() as cursor:  # cursor()创建游标对象
                # 执行建表语句（IF NOT EXISTS保障幂等性）
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS factory1_1_realtime_data_jcj (
                        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                        timestamp DATETIME NOT NULL,
                        start_time DATETIME,
                        end_time DATETIME,
                        parameter1 FLOAT,
                        parameter2 FLOAT,
                        parameter3 FLOAT,
                        parameter4 FLOAT,
                        parameter5 FLOAT,
                        parameter6 FLOAT,
                        parameter7 FLOAT,
                        parameter8 FLOAT,
                        parameter9 FLOAT,
                        parameter10 FLOAT,
                        parameter11 FLOAT
                    )""")  # 使用三重引号定义多行SQL语句

                # 循环插入100条模拟数据（_为占位符，表示不关心循环变量值）
                for _ in range(100):  # range(100)生成0-99的整数序列
                    # 生成当前时间（精确到秒）
                    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    # 构造参数元组（使用round保证小数点后两位）
                    params = (
                        current_time,  # 时间参数（字符串格式）
                        *[round(random.uniform(0, 100), 2) for _ in range(11)]  # 生成11个参数
                    )
                    # 执行参数化查询（使用字符串拼接优化可读性）
                    cursor.execute(
                        "INSERT INTO factory1_1_realtime_data_jcj (timestamp,parameter1, parameter2,parameter3,parameter4,parameter5,parameter6,parameter7,"
                        "parameter8,parameter9,parameter10,parameter11) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", params  # %s是参数占位符（非字符串格式化）使用占位符防止SQL注入，然后传入参数元组
                    )

                # 提交事务（保证100条数据原子性写入）
                self.conn.commit()
                # 输出成功信息（f-string格式化字符串）
                print(f"独立插入类：成功插入{100}条数据！")

        except pymysql.Error as e:  # 捕获pymysql特定异常
            print(f"插入失败: {str(e)}")  # 输出错误信息（转换为字符串）
            if self.conn:  # 检查连接是否有效
                self.conn.rollback()  # 事务回滚（保证数据一致性）
        finally:  # 无论是否异常都会执行
            if self.conn and self.conn.open:  # 检查连接状态
                self.conn.close()  # 关闭连接（释放数据库资源）
                self.conn = None  # 重置连接对象（避免重复关闭）

    def insert_combined_mcgs_data(self,
                                  table_name: str,  # 目标数据表名称（字符串类型）
                                  groups: list,  # 寄存器组配置列表（元组集合）
                                  ip='192.168.1.10',  # 触摸屏IP地址（默认工业地址）
                                  port=502,  # Modbus TCP端口（默认502）
                                  unit_id=1):  # 设备单元号（默认1）
        """组合式MCGS数据采集（支持多地址批量操作）
        参数说明：
        table_name: 目标表名（必须包含所有字段）
        groups: 寄存器组列表，每个元素为元组(start_address, register_count, field_names)
        ip: 触摸屏IP地址
        port: Modbus TCP端口
        unit_id: 设备站号"""
        try:
            import socket  # 导入socket模块用于TCP通信
            import struct  # 导入struct模块用于二进制解析
            all_params = []  # 全局参数存储列表（用于累积所有采集点数据）
            all_fields = []  # 全局字段存储列表（用于累积所有数据库字段名）

            # 建立TCP长连接（复用连接提升效率）
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:  # AF_INET=IPv4，SOCK_STREAM=TCP
                sock.settimeout(5)  # 设置5秒超时（防止网络阻塞）
                sock.connect((ip, port))  # 建立TCP连接（IP+端口）

                # 遍历每个寄存器组
                for group in groups:  # 遍历配置列表中的每个寄存器组
                    start_addr, reg_count, fields = group  # 系列解包赋值，元组（起始地址，寄存器数，字段列表）

                    # 参数校验
                    if reg_count % 2 != 0:  # 检查寄存器数量是否为偶数（每个浮点数占2个寄存器）
                        raise ValueError(f"寄存器组{start_addr}数量必须为偶数")
                    if len(fields) != reg_count // 2:  # 验证字段数量匹配（寄存器数/2=浮点数参数数量）
                        raise ValueError(f"寄存器组{start_addr}字段数量不匹配")

                    # 构造Modbus请求（大端字节序）
                    request = struct.pack('>HHHBBHH',  # >表示大端序，H=2字节无符号短整型
                                          0x0001,  # 事务ID（每组不同，实际应递增）
                                          start_addr,  # 当前组的寄存器起始地址
                                          0x0006,  # 后续字节长度（固定6字节）
                                          unit_id,  # 设备单元号
                                          0x03,  # 功能码03（读保持寄存器）
                                          start_addr,  # 寄存器起始地址（同第2个参数）
                                          reg_count)  # 当前组需读取的寄存器总数

                    sock.send(request)  # 发送Modbus请求帧
                    response = sock.recv(1024)  # 接收响应数据（最大1024字节）

                    # 解析响应数据
                    if len(response) < 9 + reg_count * 2:  # 校验数据长度（9字节头+寄存器数×2字节）
                        raise ValueError(f"寄存器组{start_addr}响应数据异常")

                    # 提取当前组参数
                    group_params = [
                        # 解析大端序浮点数（从响应第9字节开始，每4字节解析一个float）
                        round(struct.unpack('>f', response[9 + i * 4:13 + i * 4])[0], 2)
                        for i in range(reg_count // 2)  # 遍历当前组所有参数
                    ]

                    all_params.extend(group_params)  # 累积全局参数（用于最终插入）
                    all_fields.extend(fields)  # 累积全局字段（用于构建SQL）

            # 数据库批量写入
            self.conn = pymysql.connect(**self.conn_config)  # 创建新数据库连接
            with self.conn.cursor() as cursor:  # 获取数据库游标
                # 生成动态SQL语句
                columns = ",".join(all_fields)  # 拼接所有字段名称（field1,field2...）
                placeholders = ",".join(["%s"] * (len(all_fields) + 1))  # 生成占位符链（%s,%s...）

                # 执行组合插入（注意：表名字段需提前做好防注入处理）
                cursor.execute(f"""
                    INSERT INTO {table_name} 
                    (timestamp, {columns})    # 时间戳+所有动态字段
                    VALUES ({placeholders})    # 对应占位符数量
                """, (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), *all_params))  # 绑定参数

                self.conn.commit()  # 提交事务（保证原子性）
                print(f"组合插入：成功写入{len(all_fields)}个参数到{table_name}")  # 反馈写入结果

        except Exception as e:  # 捕获所有异常类型
            print(f"组合采集失败: {str(e)}")  # 输出错误详细信息
            if self.conn:
                self.conn.rollback()  # 事务回滚（保证数据一致性）
        finally:  # 最终清理块
            if self.conn and self.conn.open:  # 确保连接有效且已打开
                self.conn.close()  # 关闭数据库连接
                self.conn = None  # 重置连接对象


class DataManager:
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
            'pool_size': 1  # 连接池中保持的活跃连接数（防止多线程竞争）
        }
        self.connection_pool = None  # MySQL连接池对象初始化（替代原有单一连接）
        self._init_pool()  # 调用私有方法初始化连接池

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


# 测试函数
if __name__ == "__main__":
    inserter = DataInserter()

    # 测试挤出机数据插入
    inserter.insert_jcj_realtime_data()

    # # 测试数据查询
    # manager = DataManager()
    # print(manager.get_realtime_data('jcj', 1))
# 添加模块级实例（在测试块外）
inserter = DataInserter()
