# activation_code_dialog.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QApplication, QWidget, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class ActivationCodeDialog(QDialog):
    def __init__(self, parent=None, license_manager=None):
        super().__init__(parent)
        self.license_manager = license_manager
        self.setModal(True)
        # 使用模态对话框标志，确保显示在父窗口之上
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)

        # 设置样式，与license_expired_dialog保持一致
        self.setStyleSheet("""
            QWidget#container {
                background-color: rgb(192, 192, 192);
                border-radius: 15px;
                border: 1px solid gray;
            }
            QLabel {
                color: black;  /* 改为黑色以提高可读性 */
                font-size: 14px;
            }
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                border: 1px solid #cccccc;
                border-radius: 5px;
                background-color: white;  /* 输入框背景设为白色 */
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
        self.code_input.setPlaceholderText("请输入激活码:")
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

        # 使用容器 QWidget 承载所有内容并应用圆角灰色样式
        container = QWidget()
        container.setObjectName("container")
        container_layout = QVBoxLayout(container)
        container_layout.setAlignment(Qt.AlignCenter)
        container_layout.addWidget(title_label)
        container_layout.addSpacing(20)
        container_layout.addLayout(input_layout)
        container_layout.addSpacing(20)
        container_layout.addLayout(button_layout)
        container_layout.addSpacing(10)

        # 将容器加入主布局
        main_layout.addWidget(container)
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

    def showEvent(self, event):
        """重写显示事件，确保对话框显示在LicenseExpiredDialog之上"""
        super().showEvent(event)
        # 确保对话框显示在最前
        self.raise_()
        self.activateWindow()
        # 确保焦点在当前对话框
        self.setFocus()

    def exec_(self):
        """重写exec_方法，确保对话框正确显示"""
        # 确保在显示前将父窗口降低层级
        if self.parent():
            self.parent().lower()
        # 调用父类的exec_方法
        result = super().exec_()
        # 对话框关闭后，重新激活父窗口
        if self.parent():
            self.parent().raise_()
            self.parent().activateWindow()
        return result

    def apply_activation_code(self):
        activation_code = self.code_input.text().strip().upper()
        if not activation_code:
            self._show_frameless_message("警告", "请输入激活码")
            return
        if len(activation_code) < 10:
            self._show_frameless_message("警告", "激活码长度不足")
            return
        success, message = self.license_manager.validate_and_apply_activation_code(activation_code)
        if success:
            self._show_frameless_message("成功", message)
            self.accept()
        else:
            self._show_frameless_message("错误", message)

    def _show_frameless_message(self, title, text):
        dlg = QDialog(self)
        dlg.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog | Qt.WindowStaysOnTopHint)
        dlg.setAttribute(Qt.WA_TranslucentBackground)
        layout = QVBoxLayout(dlg)
        container = QWidget()
        container.setObjectName("msg_container")
        container_layout = QVBoxLayout(container)
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        btn = QPushButton("确定")
        btn.clicked.connect(dlg.accept)
        bl = QHBoxLayout()
        bl.addStretch()
        bl.addWidget(btn)
        bl.addStretch()
        container_layout.addWidget(label)
        container_layout.addLayout(bl)
        layout.addWidget(container)
        dlg.setStyleSheet("QWidget#msg_container { background-color: rgb(192, 192, 192); border-radius: 15px; border: 1px solid gray; } QLabel { color: black; font-size: 14px; } QPushButton { background-color: #007ACC; color: white; border: none; padding: 6px 12px; border-radius: 5px; } QPushButton:hover { background-color: #005A9E; }")
        dlg.resize(360, 140)
        if self.isVisible():
            pg = self.geometry()
            x = pg.x() + (pg.width() - dlg.width()) // 2
            y = pg.y() + (pg.height() - dlg.height()) // 2
            dlg.move(x, y)
        else:
            screen = QApplication.primaryScreen().geometry()
            x = (screen.width() - dlg.width()) // 2
            y = (screen.height() - dlg.height()) // 2
            dlg.move(x, y)
        dlg.exec_()

    def keyPressEvent(self, event):
        """拦截ESC键关闭事件"""
        if event.key() == Qt.Key_Escape:
            # 不执行任何操作，防止ESC关闭对话框
            event.ignore()
        else:
            super().keyPressEvent(event)
