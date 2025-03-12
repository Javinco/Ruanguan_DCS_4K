# 必须在所有代码之前添加这两行
# import sys
# sys.breakpointhook = lambda: None  # 修复Python 3.13的调试器hook
#
# i = 1
# while i < 10:
#     print(i)
# try:
#     a = int(input('请输入第一条边长：'))
#     b = int(input('请输入第二条边长：'))
#     c = int(input('请输入第三条边长：'))
#     if a + b > c and a + c > b and b + c > a:
#         print('三角形周长为：%d' % (a + b + c))
#     else:
#         raise Exception('三角形不存在')
# except Exception as e:
#     print(e)

# def sum1(a, b):
#     return a + b
#
#
# print(sum1(1, 2))
# print(format(3.14, '20'))


# def fun(n):
#     if n < 0:
#         return -1
#     elif n == 1:
#         return 1
#     else:
#         lst = [2, 8]
#         for i in range(1, n):
#             lst.append(lst[-1] + lst[-2])
#             return lst[-2] % lst[-1]
#
#
# print(fun(7))
# import random
#
#
# def get_max(lst):
#     x = lst[0]
#     for i in range(1, len(lst)):
#         if x < lst[i]:
#             x = lst[i]
#     return x
#
#
# lst = [random.randint(1, 100) for i in range(10)]
# print(lst)
# print(get_max(lst))

# def get_digit(n):
#     s = 0
#     lst = []
#     for _ in n:
#         if _.isdigit():
#             lst.append(int(_))
#     s = sum(lst)
#     return lst, s
#
# a = str(input("请输入一个字符串:"))
# lst, x =get_digit(a)
# print(f'提取的数字列表为L：{lst}')
# print(f"累加和为:{x}")

# def lower_upper(s):
#     lst = []
#     for _ in s:
#         if 'A' <= _ <= 'Z':
#             lst.append(chr(ord(_) + 32))
#         elif 'a' <= _ <= 'z':
#             lst.append(chr(ord(_) - 32))
#         else:
#             lst.append(_)
#     return "".join(lst)
#
# s = input("请输入一个字符串:")
# new_s = lower_upper(s)
# print(f"转换后的字符串为:{new_s}")
# class student:
#     scholl = '清华大学'
#
#     def __init__(self, xm, age):
#         self.name = xm
#         self.age = age
#
#     def show(self):
#         print(f'姓名:{self.name},年龄:{self.age}')
#
#     @staticmethod
#     def sm():
#         print('这是一个静态方法')
#
#     @classmethod
#     def cm(cls):
#         # print(cls.scholl)
#         print('这是一个类方法')
#
#
# # # # 测试函数
# # # if __name__ == "__main__":
# # inserter = student(123, 18)
# # # print(inserter.scholl)
# # inserter.show()
# # student.sm()
# stu = student('张三', 18)
# stu2 = student('李四', 19)
# stu3 = student('王五', 20)
# stu4 = student('赵六', 21)
# lst = [stu, stu2, stu3, stu4]
# for _ in lst:
#     _.show()
#
# stu.gender = '男'
# print(stu.gender)
#
#
# def introduce():
#     print('我叫%s,今年%d岁' % (stu.name, stu.age))
#
# stu2.func = introduce
# stu2.func()

# class Circle:
#     def __init__(self, r):
#         self.r = r
#
#     def get_area(self):
#         return 3.14 * self.r ** 2
#
#     def get_perimeter(self):
#         return 2 * 3.14 * self.r
#
#
# # 创建对象
# r = int(input('请输入圆的半径：'))
#
# c = Circle(r)
# print('圆的面积：', c.get_area())
# print('圆的周长：', c.get_perimeter())
# class Student:
#     def __init__(self, name, age, gender, scores):
#         self.name = name
#         self.age = age
#         self.gender = gender
#         self.scores = scores
#
#     def info(self):
#         print(f"姓名：{self.name}，年龄：{self.age}，性别：{self.gender}，分数：{self.scores}")
#
#
# print('请输入5位学生信息：（姓名# 年龄 # 性别 #成绩）')
# lst = []
# for _ in range(1, 6):
#     s = input(f'请输入第{_}位学生信息：')
#     s_lst = s.split('#')
#
#     stu = Student(s_lst[0], int(s_lst[1]), s_lst[2], int(s_lst[3]))
#     lst.append(stu)
#
# for _ in lst:
#     _.info()

# class Instrument:
#
#     def make_sound(self):
#         print('乐器正在演奏...')
#
#
# class Erhu(Instrument):
#
#     def make_sound(self):
#         print('二胡正在演奏...')
#
#
# class Piano(Instrument):
#
#     def make_sound(self):
#         print('钢琴正在演奏...')
#
#
# class Violin(Instrument):
#
#     def make_sound(self):
#         print('小提琴正在演奏...')
#
#
# def play(obj):
#     obj.make_sound()
#
# erhu = Erhu()
# piano = Piano()
# violin = Violin()
# play(erhu)

# class Car:
#     def __init__(self, type, no):
#         self.type = type
#         self.no = no
#
#     def start(self):
#         print('汽车启动了')
#
#     def stop(self):
#         print('汽车停止了')
#
#
# class Taxi(Car):
#     def __init__(self, type, no, company):
#         super().__init__(type, no)
#         self.company = company
#
#     def start(self):
#         print(f"乘客您好，我是{self.company}出租车公司，我的车牌是{self.no}，您要去哪里？")
#
#     def stop(self):
#         print(f"目的地到了，您需要支付元")
#
#
# class FamilyCar(Car):
#     def __init__(self, type, no, name):
#         super().__init__(type, no)
#         self.name = name
#
#     def start(self):
#         print(f"我是{self.name}，我的轿车我做主")
#
#     def stop(self):
#         print(f"目的地到了我们去玩吧")
#
#
# taxi = Taxi('xioami', '京A88888', '北京小米')
# taxi.start()
# taxi.stop()
# print('-' * 30)
# familycar = FamilyCar('奔驰', '京A66666', '武大郎')
# familycar.start()
# familycar.stop()
table_name = "factory1_1_realtime_data_jcj"
update_strategies = {
    # 键：表名字符串 -> 值：对应的更新方法（函数对象）
    "factory1_1_realtime_data_jcj": 1,  # 挤出机实时数据
    "factory1_1_realtime_data_fjj": 2,  # 放卷机实时数据
    "factory1_1_realtime_data_zdj": 3,  # 自动机实时数据
    "factory1_1_set_data_jcj": 4,  # 挤出机设定数据
    "factory1_1_set_data_fjj": 5,  # 放卷机设定数据
    "factory1_1_set_data_zdj": 6,  # 自动机设定数据
    "factory1_1_set_data_curve": 7  # 曲线设定数据
}

# 使用海象运算符 := 在条件判断中同时完成赋值操作
# 1. 从字典中获取对应表名的更新策略（函数对象）
# 2. 如果找到对应策略（非None），执行该策略
if strategy := update_strategies.get(table_name):
    # 调用对应的更新方法，并传入获取到的数据
    print(update_strategies.get(table_name))
    print("strategy", strategy)
