import cv2
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QImage, QPixmap

class VideoThread(QThread):
    changePixmap = pyqtSignal(QImage)

    def __init__(self, rtsp_url):
        super().__init__()
        self.rtsp_url = rtsp_url
        self.running = True

    def run(self):
        cap = cv2.VideoCapture(self.rtsp_url)
        while self.running:
            ret, frame = cap.read()
            if ret:
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                convert_to_qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                p = convert_to_qt_format.scaled(640, 480, Qt.KeepAspectRatio)
                self.changePixmap.emit(p)
        cap.release()

    def stop(self):
        self.running = False

class CameraApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("摄像头监控系统")
        self.resize(800, 600)

        # 视频显示标签
        self.video_label = QLabel(self)
        self.video_label.setGeometry(50, 50, 640, 480)
        self.video_label.setStyleSheet("border: 1px solid black;")

        # 控制按钮
        self.start_btn = QPushButton("开始", self)
        self.start_btn.setGeometry(700, 100, 80, 30)
        self.start_btn.clicked.connect(self.start_video)

        self.stop_btn = QPushButton("停止", self)
        self.stop_btn.setGeometry(700, 150, 80, 30)
        self.stop_btn.clicked.connect(self.stop_video)
        self.stop_btn.setEnabled(False)

        self.thread = None
        # 替换为你的摄像头RTSP地址
        self.rtsp_url = "rtsp://admin:MuBai@monitor01@192.168.1.64:554/Streaming/Channels/101"

    def start_video(self):
        if self.thread is None or not self.thread.isRunning():
            self.thread = VideoThread(self.rtsp_url)
            self.thread.changePixmap.connect(self.set_image)
            self.thread.start()
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)

    def stop_video(self):
        if self.thread and self.thread.isRunning():
            self.thread.stop()
            self.thread.wait()
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)

    def set_image(self, image):
        self.video_label.setPixmap(QPixmap.fromImage(image))

    def closeEvent(self, event):
        self.stop_video()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CameraApp()
    window.show()
    sys.exit(app.exec_())
