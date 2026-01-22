# license_expired_dialog.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QApplication, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor
from activation_code_dialog import ActivationCodeDialog


class LicenseExpiredDialog(QDialog):
    def __init__(self, parent=None, license_manager=None):
        super().__init__(parent)
        self.license_manager = license_manager
        self.setModal(True)
        # 移除 FramelessWindowHint，保留 WindowStaysOnTopHint
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        # 不设置 WA_TranslucentBackground 属性
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        # 设置样式
        self.setStyleSheet("""
            QDialog {
                background-color: rgb(192, 192, 192);  /* 灰色底色 */
                border-radius: 15px;
                border: 1px solid gray;  /* 添加边框确保可见性 */
            }
            QLabel {
                color: black;  /* 改为黑色以提高可读性 */
                font-size: 28px;
                font-weight: bold;
            }
            QPushButton {
                background-color: #ff4444;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 26px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #cc0000;
            }
            QPushButton#activate_btn {
                background-color: #00aa00;
            }
            QPushButton#activate_btn:hover {
                background-color: #008800;
            }
        """)

        # 标题
        title_label = QLabel("⚠ 授权验证失败 ⚠")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)

        # 内容
        content_label = QLabel("授权已失效，请联系厂商重新授权\n\n"
                               "联系方式: 13757905793\n"
                               "邮箱: blznkj2015@163.com")
        content_label.setAlignment(Qt.AlignCenter)
        content_label.setWordWrap(True)

        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # 联系厂商按钮（禁用）
        contact_button = QPushButton("联系厂商")
        contact_button.setEnabled(False)  # 禁用按钮

        # 激活码按钮
        activate_button = QPushButton("输入激活码")
        activate_button.setObjectName("activate_btn")  # 设置对象名称以便样式应用
        activate_button.clicked.connect(self.open_activation_dialog)

        button_layout.addWidget(contact_button)
        button_layout.addWidget(activate_button)
        button_layout.addStretch()

        layout.addWidget(title_label)
        layout.addWidget(content_label)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # 设置对话框大小
        self.resize(500, 300)

        # 居中显示
        self.center_dialog()

    def center_dialog(self):
        """将弹窗居中显示"""
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)

    def showEvent(self, event):
        """重写显示事件，确保对话框总是在最顶层"""
        super().showEvent(event)
        self.raise_()
        self.activateWindow()

        # 定期检查确保对话框始终置顶
        self.top_timer = QTimer(self)
        self.top_timer.timeout.connect(self._ensure_topmost)
        self.top_timer.start(1000)  # 每秒检查一次

    def _ensure_topmost(self):
        """确保对话框始终保持在最顶层"""
        self.raise_()
        self.activateWindow()

    def mousePressEvent(self, event):
        """拦截鼠标点击事件，防止被点击消失"""
        event.ignore()

    def keyPressEvent(self, event):
        """拦截键盘事件，防止ESC关闭"""
        event.ignore()

    def closeEvent(self, event):
        """重写关闭事件，仅在特定情况下允许关闭"""
        # 检查许可证是否有效，如果有效则允许关闭
        is_valid, _ = self.license_manager.check_license_validity()
        if is_valid:
            # 停止置顶定时器
            if hasattr(self, 'top_timer'):
                self.top_timer.stop()
            event.accept()
        else:
            # 如果许可证仍无效，则阻止关闭
            event.ignore()

    def hideEvent(self, event):
        """重写隐藏事件，仅在许可证有效时允许隐藏"""
        is_valid, _ = self.license_manager.check_license_validity()
        if is_valid:
            event.accept()
        else:
            # 如果许可证无效，阻止隐藏
            event.ignore()

    def open_activation_dialog(self):
        """打开激活码输入对话框"""
        # 暂时停止置顶定时器，以便激活码对话框可以显示在最前
        if hasattr(self, 'top_timer'):
            self.top_timer.stop()

        dialog = ActivationCodeDialog(parent=self, license_manager=self.license_manager)

        # 显示激活码对话框前，暂时降低过期对话框的层级
        self.lower()

        result = dialog.exec_()

        # 无论结果如何，都需要重启置顶定时器
        if hasattr(self, 'top_timer'):
            self.top_timer.start(1000)

        if result == QDialog.Accepted:
            # 激活码应用成功，检查许可证状态
            is_valid, message = self.license_manager.check_license_validity()
            if is_valid:
                # 许可证现在有效，可以关闭过期对话框
                print(f"激活码应用成功，许可证状态: {message}")
                # 停止置顶定时器
                if hasattr(self, 'top_timer'):
                    self.top_timer.stop()
                self.accept()  # 关闭当前对话框
                if self.parent():
                    # 通知父窗口刷新许可证状态
                    self.parent().check_license_after_activation()
            else:
                print(f"激活码应用后许可证仍无效: {message}")
        else:
            # 如果用户取消了激活码对话框，重新将过期对话框置顶
            self.raise_()
            self.activateWindow()

