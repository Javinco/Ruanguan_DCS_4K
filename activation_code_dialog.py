# activation_code_dialog.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class ActivationCodeDialog(QDialog):
    def __init__(self, parent=None, license_manager=None):
        super().__init__(parent)
        self.license_manager = license_manager
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)

        # 设置样式
        self.setStyleSheet("""
            QDialog {
                background-color: rgba(240, 240, 240, 230);
                border-radius: 10px;
                border: 2px solid #cccccc;
            }
            QLabel {
                color: #333333;
                font-size: 14px;
            }
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                border: 1px solid #cccccc;
                border-radius: 5px;
            }
            QLineEdit:focus {
                border: 2px solid #007ACC;
            }
            QPushButton {
                background-color: #007ACC;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #005A9E;
            }
            QPushButton:pressed {
                background-color: #004A8E;
            }
        """)

        # 标题
        title_label = QLabel("请输入激活码")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)

        # 激活码输入框
        input_layout = QHBoxLayout()
        input_layout.addStretch()
        code_label = QLabel("激活码:")
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("请输入激活码（如：SRT001XVJQKLMNPQR 或 LNG001PERMANENT）")
        self.code_input.setMaxLength(30)  # 支持更长的激活码
        input_layout.addWidget(code_label)
        input_layout.addWidget(self.code_input)
        input_layout.addStretch()

        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.apply_button = QPushButton("应用")
        self.cancel_button = QPushButton("取消")
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.addStretch()

        # 连接信号
        self.apply_button.clicked.connect(self.apply_activation_code)
        self.cancel_button.clicked.connect(self.reject)
        self.code_input.returnPressed.connect(self.apply_activation_code)

        # 添加到主布局
        main_layout.addWidget(title_label)
        main_layout.addSpacing(20)
        main_layout.addLayout(input_layout)
        main_layout.addSpacing(20)
        main_layout.addLayout(button_layout)
        main_layout.addSpacing(10)

        self.setLayout(main_layout)

        # 设置对话框大小
        self.resize(500, 150)

        # 居中显示
        self.center_dialog()

    def center_dialog(self):
        """将弹窗居中显示"""
        if self.parent():
            parent_geometry = self.parent().geometry()
            x = parent_geometry.x() + (parent_geometry.width() - self.width()) // 2
            y = parent_geometry.y() + (parent_geometry.height() - self.height()) // 2
            self.move(x, y)
        else:
            # 如果没有父窗口，则在屏幕上居中
            screen = QApplication.primaryScreen().geometry()
            x = (screen.width() - self.width()) // 2
            y = (screen.height() - self.height()) // 2
            self.move(x, y)

    def apply_activation_code(self):
        """应用激活码"""
        activation_code = self.code_input.text().strip().upper()

        if not activation_code:
            QMessageBox.warning(self, "警告", "请输入激活码")
            return

        if len(activation_code) < 10:
            QMessageBox.warning(self, "警告", "激活码长度不足")
            return

        # 验证并应用激活码
        success, message = self.license_manager.validate_and_apply_activation_code(activation_code)

        if success:
            QMessageBox.information(self, "成功", message)
            self.accept()  # 关闭对话框
        else:
            QMessageBox.critical(self, "错误", message)

    def keyPressEvent(self, event):
        """拦截ESC键关闭事件"""
        if event.key() == Qt.Key_Escape:
            # 不执行任何操作，防止ESC关闭对话框
            event.ignore()
        else:
            super().keyPressEvent(event)
