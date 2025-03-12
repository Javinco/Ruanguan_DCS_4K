# # 导入MySQL官方连接驱动
# import mysql.connector
# # 从驱动中导入错误处理模块
# from mysql.connector import Error
# # 导入时间处理模块
# from datetime import datetime
# import pymysql
# import random
#
#
# class DataInserter:
#     """实时数据插入器（独立维护插入逻辑）
#     功能：专门处理实时数据的批量插入操作
#     设计考虑：采用pymysql库实现，与DataManager的mysql-connector解耦"""
#
#     def __init__(self, host='localhost', user='root', password='admin', database='dcs_data'):
#         # 初始化方法（构造器），参数说明：
#         # host: MySQL服务器地址（默认值'localhost'本地主机）
#         # user: 数据库用户名（默认值'root'管理员账号）
#         # password: 数据库访问密码（默认值'admin'需按实际修改）
#         # database: 目标数据库名称（默认值'dcs_data'数据控制系统数据库）
#         self.conn_config = {  # 连接配置字典
#             'host': host,  # 服务器IP地址配置项
#             'user': user,  # 用户名配置项
#             'password': password,  # 密码配置项（敏感信息需加密处理）
#             'database': database,  # 数据库名称配置项
#             'charset': 'utf8mb4'  # 字符集配置（支持emoji和特殊字符）
#         }
#         self.conn = None  # 数据库连接对象初始化（None表示未连接状态）
#
#     def insert_realtime_data(self):
#         """批量插入方法（保持原有pymysql实现）
#         功能流程：
#         1. 建立数据库连接
#         2. 创建数据表（如果不存在）
#         3. 生成并插入100条模拟数据
#         4. 处理事务提交/回滚
#         5. 确保连接关闭"""
#         try:
#             # 建立数据库连接（使用pymysql库的connect方法）
#             # **操作符将字典解包为关键字参数
#             self.conn = pymysql.connect(**self.conn_config)
#
#             # 使用with语句管理游标（自动释放资源）
#             with self.conn.cursor() as cursor:  # cursor()创建游标对象
#                 # 执行建表语句（IF NOT EXISTS保障幂等性）
#                 cursor.execute("""
#                     CREATE TABLE IF NOT EXISTS real_timedata (
#                         id INT AUTO_INCREMENT PRIMARY KEY,  # 自增主键（从1开始自动增长）
#                         timestamp DATETIME NOT NULL,       # 时间戳字段（不允许为空）
#                         parameter1 DECIMAL(6,2),            # 数值字段1（共6位，含2位小数）
#                         parameter2 DECIMAL(6,2)             # 数值字段2（共6位，含2位小数）
#                     )""")  # 使用三重引号定义多行SQL语句
#
#                 # 循环插入100条模拟数据（_为占位符，表示不关心循环变量值）
#                 for _ in range(100):  # range(100)生成0-99的整数序列
#                     # 生成当前时间（精确到秒）
#                     current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#                     # 构造参数元组（使用round保证小数点后两位）
#                     params = (
#                         current_time,  # 时间参数（字符串格式）
#                         round(random.uniform(0.00, 9999.99), 2),  # 生成0.00-9999.99的随机数
#                         round(random.uniform(0.00, 9999.99), 2)  # 第二个参数同理
#                     )
#                     # 执行参数化查询（使用字符串拼接优化可读性）
#                     cursor.execute(
#                         "INSERT INTO real_timedata (timestamp, parameter1, parameter2) "
#                         "VALUES (%s, %s, %s)", params  # %s是参数占位符（非字符串格式化）使用占位符防止SQL注入，然后传入参数元组
#                     )
#
#                 # 提交事务（保证100条数据原子性写入）
#                 self.conn.commit()
#                 # 输出成功信息（f-string格式化字符串）
#                 print(f"独立插入类：成功插入{100}条数据！")
#
#         except pymysql.Error as e:  # 捕获pymysql特定异常
#             print(f"插入失败: {str(e)}")  # 输出错误信息（转换为字符串）
#             if self.conn:  # 检查连接是否有效
#                 self.conn.rollback()  # 事务回滚（保证数据一致性）
#         finally:  # 无论是否异常都会执行
#             if self.conn and self.conn.open:  # 检查连接状态
#                 self.conn.close()  # 关闭连接（释放数据库资源）
#                 self.conn = None  # 重置连接对象（避免重复关闭）
#
#     def insert_jcj_realtime_data(self):
#         """批量插入方法（保持原有pymysql实现）
#         功能流程：
#         1. 建立数据库连接
#         2. 创建数据表（如果不存在）
#         3. 生成并插入100条模拟数据
#         4. 处理事务提交/回滚
#         5. 确保连接关闭"""
#         try:
#             # 建立数据库连接（使用pymysql库的connect方法）
#             # **操作符将字典解包为关键字参数
#             self.conn = pymysql.connect(**self.conn_config)
#
#             # 使用with语句管理游标（自动释放资源）
#             with self.conn.cursor() as cursor:  # cursor()创建游标对象
#                 # 执行建表语句（IF NOT EXISTS保障幂等性）
#                 cursor.execute("""
#                     CREATE TABLE IF NOT EXISTS factory1_1_realtime_data_jcj (
#                         id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
#                         timestamp DATETIME NOT NULL,
#                         start_time DATETIME,
#                         end_time DATETIME,
#                         parameter1 FLOAT,
#                         parameter2 FLOAT,
#                         parameter3 FLOAT,
#                         parameter4 FLOAT,
#                         parameter5 FLOAT,
#                         parameter6 FLOAT,
#                         parameter7 FLOAT,
#                         parameter8 FLOAT,
#                         parameter9 FLOAT,
#                         parameter10 FLOAT,
#                         parameter11 FLOAT
#                     )""")  # 使用三重引号定义多行SQL语句
#
#                 # 循环插入100条模拟数据（_为占位符，表示不关心循环变量值）
#                 for _ in range(100):  # range(100)生成0-99的整数序列
#                     # 生成当前时间（精确到秒）
#                     current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#                     # 构造参数元组（使用round保证小数点后两位）
#                     params = (
#                         current_time,  # 时间参数（字符串格式）
#                         *[round(random.uniform(0, 100), 2) for _ in range(11)]  # 生成11个参数
#                     )
#                     # 执行参数化查询（使用字符串拼接优化可读性）
#                     cursor.execute(
#                         "INSERT INTO factory1_1_realtime_data_jcj (timestamp,parameter1, parameter2,parameter3,parameter4,parameter5,parameter6,parameter7,"
#                         "parameter8,parameter9,parameter10,parameter11) "
#                         "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", params  # %s是参数占位符（非字符串格式化）使用占位符防止SQL注入，然后传入参数元组
#                     )
#
#                 # 提交事务（保证100条数据原子性写入）
#                 self.conn.commit()
#                 # 输出成功信息（f-string格式化字符串）
#                 print(f"独立插入类：成功插入{100}条数据！")
#
#         except pymysql.Error as e:  # 捕获pymysql特定异常
#             print(f"插入失败: {str(e)}")  # 输出错误信息（转换为字符串）
#             if self.conn:  # 检查连接是否有效
#                 self.conn.rollback()  # 事务回滚（保证数据一致性）
#         finally:  # 无论是否异常都会执行
#             if self.conn and self.conn.open:  # 检查连接状态
#                 self.conn.close()  # 关闭连接（释放数据库资源）
#                 self.conn = None  # 重置连接对象（避免重复关闭）
#
#
# class DataManager:
#     # 初始化方法（构造器）
#     def __init__(self, host='localhost', user='root', password='admin', database='dcs_data'):
#         """数据库管理器
#         Args参数说明:
#             host: MySQL服务器地址（默认本地）
#             user: 数据库用户名（默认root）
#             password: 数据库密码（需根据实际修改）
#             database: 要连接的数据库名称（默认dcs_data）
#         """
#         # 创建配置字典存储连接参数
#         self.config = {
#             'host': host,  # 数据库服务器的主机名或IP地址
#             'user': user,  # 登录数据库的用户名凭证
#             'password': password,  # 登录数据库的密码凭证
#             'database': database,  # 要操作的数据库名称
#             'pool_size': 1  # 连接池中保持的活跃连接数（防止多线程竞争）
#         }
#         self.connection_pool = None  # MySQL连接池对象初始化（替代原有单一连接）
#         self._init_pool()  # 调用私有方法初始化连接池
#
#     def _init_pool(self):
#         """初始化连接池（解决多线程访问问题）"""
#         try:
#             # 使用mysql.connector的连接池功能创建连接池
#             self.connection_pool = mysql.connector.pooling.MySQLConnectionPool(
#                 pool_name="dcs_pool",  # 连接池的名称标识
#                 pool_reset_session=True,  # 重置会话状态后返回连接池
#                 **self.config  # 解包连接配置参数
#             )
#         except Error as e:
#             print(f"连接池初始化失败: {e}")  # 输出错误详细信息
#             exit(1)  # 严重错误直接终止程序（无法继续运行）
#
#     def get_realtime_data(self):
#         """获取实时数据（完全重构）
#         Args参数:
#             id: int类型，设备唯一标识符（当前版本暂未使用，保留参数位）
#         Returns返回:
#             dict: 包含最新实时数据的字典，键为字段名（timestamp/parameter1/parameter2）
#                   None表示查询失败
#         """
#         try:
#             # 使用with语句自动管理连接生命周期（确保连接正确释放）
#             # self.connection_pool.get_connection()：从连接池获取数据库连接
#             with self.connection_pool.get_connection() as connection:  # connection是连接对象
#
#                 # 使用with语句自动管理游标生命周期（确保游标正确关闭）
#                 # dictionary=True：使查询结果以字典形式返回（键为字段名）
#                 with connection.cursor(dictionary=True) as cursor:  # cursor是游标对象
#
#                     # 执行参数化SQL查询（使用三重引号定义多行字符串）
#                     # 查询逻辑说明：
#                     # 1. SELECT选择三个字段：timestamp时间戳、parameter1参数1、parameter2参数2
#                     # 2. FROM指定数据表（需与DataInserter插入的表名保持一致）
#                     # 3. WHERE筛选条件（当前使用id=%s但表结构无设备ID字段，需要修正）
#                     # 4. ORDER BY按时间戳降序排列（DESC表示从大到小）
#                     # 5. LIMIT 1限制返回1条记录
#                     cursor.execute("""
#                         SELECT
#                             timestamp,    -- 字段注释：数据记录的时间戳（DATETIME类型）
#                             parameter1,   -- 字段注释：设备参数1的测量值（DECIMAL类型）
#                             parameter2    -- 字段注释：设备参数2的测量值（DECIMAL类型）
#                         FROM factory1_1_realtime_data_jcj  -- 修正为DataInserter实际使用的表名（原表名有误）
#                         ORDER BY id DESC    -- 按自增主键降序排列（替代时间戳排序方案）
#                         LIMIT 1             -- 限制返回最新一条记录
#                     """)  # 移除了WHERE条件参数
#
#                     # 获取单行查询结果（fetchone()返回字典或None）
#                     result = cursor.fetchone()  # result示例：{'timestamp':, 'parameter1':, 'parameter2':}
#
#                     if result:
#                         # 时间戳格式转换：将datetime对象转为ISO8601标准格式字符串
#                         # isoformat()输出示例：'2023-08-08T12:34:56'
#                         result['timestamp'] = result['timestamp'].isoformat()  # 转换时间格式
#
#                     return result  # 返回结果字典（无数据时返回None）
#
#         # 异常处理部分（捕获数据库操作错误）
#         except Error as e:
#             # 格式化输出错误信息（e包含具体错误类型和代码）
#             print(f"数据库操作失败: {e}")  # 示例输出：数据库操作失败: 1146 (42S02): Table 'xxx' doesn't exist
#             return None  # 返回空值表示查询失败
#
#
# # 测试函数
# if __name__ == "__main__":
#     inserter = DataInserter()
#
#     # 测试挤出机数据插入
#     inserter.insert_jcj_realtime_data()
#
#     # # 测试数据查询
#     # manager = DataManager()
#     # print(manager.get_realtime_data('jcj', 1))
