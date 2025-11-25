# coding: utf-8
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

class SubtitleOverlay(QWidget):
    """浮動字幕視窗"""
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        layout = QVBoxLayout()
        
        self.subtitle_label = QLabel("")
        self.subtitle_label.setFont(QFont("Microsoft JhengHei", 24, QFont.Weight.Bold))
        self.subtitle_label.setStyleSheet("color: white; background-color: rgba(0, 0, 0, 160); border-radius: 12px; padding: 12px;")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label.setWordWrap(True)
        layout.addWidget(self.subtitle_label)
        self.setLayout(layout)
        
        screen = QApplication.primaryScreen().availableGeometry()
        self.setGeometry((screen.width()-800)//2, screen.height()-250, 800, 200)

    def update_text(self, text):
        """更新字幕文字"""
        self.subtitle_label.setText(text)
        QTimer.singleShot(8000, lambda: self.subtitle_label.setText("") if self.subtitle_label.text() == text else None)
