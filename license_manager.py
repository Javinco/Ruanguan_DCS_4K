# license_manager.py
import os
import json
from datetime import datetime, timedelta
import base64


class LicenseManager:
    def __init__(self, license_file="license.key"):
        self.license_file = license_file
        # 预定义激活码字典 - 在部署前生成并在此定义
        # 短期激活码：延长30天，数量较多，格式随机
        # 长期激活码：永久授权，数量较少
        self.valid_codes = {
            # 短期激活码 - 延长30天 (随机生成，避免相似性)
            "SRT001XVJQKLMNPQR": {"type": "short_term", "days": 30},
            "SRT002ABCPQRYZABC": {"type": "short_term", "days": 30},
            "SRT003MNOPQRSTUVW": {"type": "short_term", "days": 30},
            "SRT004EFGHIJKLMNO": {"type": "short_term", "days": 30},
            "SRT005UVWXYZABCDE": {"type": "short_term", "days": 30},
            "SRT006HIJKLMNOPQR": {"type": "short_term", "days": 30},
            "SRT007RSTUVWXABCD": {"type": "short_term", "days": 30},
            "SRT008BCDEFGHIJKL": {"type": "short_term", "days": 30},
            "SRT009LMNOPQRSTUV": {"type": "short_term", "days": 30},
            "SRT010YZABCDEFGH": {"type": "short_term", "days": 30},
            "SRT011CDEFGHIJKLM": {"type": "short_term", "days": 30},
            "SRT012JKLMNOPQRST": {"type": "short_term", "days": 30},
            "SRT013VWXYZABCDEF": {"type": "short_term", "days": 30},
            "SRT014GHIJKLMNOPQ": {"type": "short_term", "days": 30},
            "SRT015RSTUVWXABCD": {"type": "short_term", "days": 30},
            "SRT016EFGHIJKLMNO": {"type": "short_term", "days": 30},
            "SRT017PQRSTUVWXY": {"type": "short_term", "days": 30},
            "SRT018ZABCDEFGHJK": {"type": "short_term", "days": 30},
            "SRT019LMNOPQRSTUV": {"type": "short_term", "days": 30},
            "SRT020CDEFGHIJKLM": {"type": "short_term", "days": 30},
            "SRT021NOPQRSTUVWX": {"type": "short_term", "days": 30},
            "SRT022FGHIJKLMNOP": {"type": "short_term", "days": 30},
            "SRT023WXYZABCDEFG": {"type": "short_term", "days": 30},
            "SRT024HIJKLMNOPQR": {"type": "short_term", "days": 30},
            "SRT025STUVWXABCD": {"type": "short_term", "days": 30},
            "SRT026KLMNOPQRST": {"type": "short_term", "days": 30},
            "SRT027VWXYZABCDEF": {"type": "short_term", "days": 30},
            "SRT028GHIJKLMNO": {"type": "short_term", "days": 30},
            "SRT029PQRSTUVWXY": {"type": "short_term", "days": 30},
            "SRT030ZABCDEFGHJK": {"type": "short_term", "days": 30},
            "SRT031LMNOPQRSTUV": {"type": "short_term", "days": 30},
            "SRT032CDEFGHIJKLM": {"type": "short_term", "days": 30},
            "SRT033NOPQRSTUVWX": {"type": "short_term", "days": 30},
            "SRT034FGHIJKLMNOP": {"type": "short_term", "days": 30},
            "SRT035WXYZABCDEFG": {"type": "short_term", "days": 30},
            "SRT036HIJKLMNOPQR": {"type": "short_term", "days": 30},
            "SRT037STUVWXABCD": {"type": "short_term", "days": 30},
            "SRT038KLMNOPQRST": {"type": "short_term", "days": 30},
            "SRT039VWXYZABCDEF": {"type": "short_term", "days": 30},
            "SRT040GHIJKLMNO": {"type": "short_term", "days": 30},
            "SRT041PQRSTUVWXY": {"type": "short_term", "days": 30},
            "SRT042ZABCDEFGHJK": {"type": "short_term", "days": 30},
            "SRT043LMNOPQRSTUV": {"type": "short_term", "days": 30},
            "SRT044CDEFGHIJKLM": {"type": "short_term", "days": 30},
            "SRT045NOPQRSTUVWX": {"type": "short_term", "days": 30},
            "SRT046FGHIJKLMNOP": {"type": "short_term", "days": 30},
            "SRT047WXYZABCDEFG": {"type": "short_term", "days": 30},
            "SRT048HIJKLMNOPQR": {"type": "short_term", "days": 30},
            "SRT049STUVWXABCD": {"type": "short_term", "days": 30},
            "SRT050KLMNOPQRST": {"type": "short_term", "days": 30},

            # 长期激活码 - 永久授权 (数量少，更安全)
            "LNG001PERMANENT": {"type": "long_term", "days": 0},
            "LNG002FOREVER": {"type": "long_term", "days": 0},
            "LNG003ETERNAL": {"type": "long_term", "days": 0},
            "LNG004LIFETIME": {"type": "long_term", "days": 0},
            "LNG005INFINITE": {"type": "long_term", "days": 0},
        }
        # 确保许可证文件存在
        self.ensure_license_file()

    @staticmethod
    def encode_license_data(data):
        """将许可证数据编码为非明文格式"""
        json_str = json.dumps(data, separators=(',', ':'))
        encoded_bytes = base64.b64encode(json_str.encode('utf-8'))
        return encoded_bytes.decode('utf-8')

    @staticmethod
    def decode_license_data(encoded_str):
        """解码许可证数据"""
        try:
            decoded_bytes = base64.b64decode(encoded_str.encode('utf-8'))
            json_str = decoded_bytes.decode('utf-8')
            return json.loads(json_str)
        except:
            return None

    def ensure_license_file(self):
        """确保许可证文件存在并具有正确的格式"""
        if not os.path.exists(self.license_file):
            initial_date = datetime.now()
            license_data = {
                'install_date': initial_date.isoformat(),
                'expiry_date': (initial_date + timedelta(days=30)).isoformat(),  # 0.1天有效期，约2.4小时，用于测试
                'status': 'active',
                'permanent': False,  # 是否永久授权
                'used_codes': []     # 已使用的激活码列表
            }

            # 将许可证数据编码后保存
            encoded_data = self.encode_license_data(license_data)

            with open(self.license_file, 'w', encoding='utf-8') as f:
                json.dump({'license': encoded_data}, f)

    def create_initial_license(self):
        """创建初始许可证（首次运行时）"""
        self.ensure_license_file()

    def check_license_validity(self):
        """检查许可证是否有效"""
        if not os.path.exists(self.license_file):
            return False, "许可证文件不存在"

        try:
            with open(self.license_file, 'r', encoding='utf-8') as f:
                file_content = json.load(f)

            # 解码许可证数据
            encoded_data = file_content.get('license', '')
            license_info = self.decode_license_data(encoded_data)

            if license_info is None:
                return False, "许可证解码失败"

            # 检查是否永久授权
            if license_info.get('permanent', False):
                return True, "永久授权"

            # 检查临时授权
            expiry_date = datetime.fromisoformat(license_info['expiry_date'])
            current_date = datetime.now()

            if current_date > expiry_date:
                return False, f"授权已过期 {expiry_date.strftime('%Y-%m-%d %H:%M:%S')}"
            else:
                remaining_days = (expiry_date - current_date).days
                return True, f"授权有效，剩余 {remaining_days} 天"

        except json.JSONDecodeError:
            return False, "许可证文件格式错误"
        except Exception as e:
            return False, f"许可证验证失败: {str(e)}"

    def validate_and_apply_activation_code(self, activation_code):
        """验证并应用激活码"""
        # 支持输入激活码时包含分隔符的情况，移除分隔符
        clean_code = activation_code.replace('-', '').replace(' ', '').strip().upper()

        # 读取现有许可证以检查已使用的激活码
        with open(self.license_file, 'r', encoding='utf-8') as f:
            file_content = json.load(f)
        encoded_data = file_content.get('license', '')
        license_info = self.decode_license_data(encoded_data)

        if license_info is None:
            return False, "许可证解码失败"

        # 检查激活码是否已被使用
        used_codes = license_info.get('used_codes', [])
        if clean_code in used_codes:
            return False, "激活码已被使用，无法重复使用"

        if clean_code not in self.valid_codes:
            return False, "激活码无效或不存在"

        code_info = self.valid_codes[clean_code]
        result = self._apply_activation_code(code_info["type"], code_info["days"], clean_code)
        return result

    def _apply_activation_code(self, code_type, days, used_code):
        """应用激活码到许可证"""
        try:
            # 读取现有许可证
            with open(self.license_file, 'r', encoding='utf-8') as f:
                file_content = json.load(f)

            # 解码许可证数据
            encoded_data = file_content.get('license', '')
            license_info = self.decode_license_data(encoded_data)

            if license_info is None:
                return False, "许可证解码失败"

            if code_type == 'long_term':
                # 长期激活码：设置为永久授权
                license_info['permanent'] = True
                license_info['status'] = 'active'
            elif code_type == 'short_term':
                # 短期激活码：延长指定天数
                current_expiry = datetime.fromisoformat(license_info['expiry_date'])
                new_expiry = current_expiry + timedelta(days=days)
                license_info['expiry_date'] = new_expiry.isoformat()
                license_info['permanent'] = False
            else:
                return False, "未知的激活码类型"

            # 添加已使用的激活码到列表
            used_codes = license_info.get('used_codes', [])
            if used_code not in used_codes:
                used_codes.append(used_code)
            license_info['used_codes'] = used_codes

            # 重新编码并保存许可证
            encoded_data = self.encode_license_data(license_info)

            with open(self.license_file, 'w', encoding='utf-8') as f:
                json.dump({'license': encoded_data}, f)

            return True, f"{code_type} 激活码应用成功"

        except FileNotFoundError:
            return False, "许可证文件不存在"
        except json.JSONDecodeError:
            return False, "许可证文件格式错误"
        except Exception as e:
            return False, f"应用激活码失败: {str(e)}"


# 全局许可证管理器实例
license_manager = LicenseManager()
